import boto3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
import logging

from config import settings
from exceptions import EventNotFoundException, DatabaseException

logger = logging.getLogger(__name__)


class DynamoDBClient:
    def __init__(self):
        self.table_name = settings.DYNAMODB_TABLE_NAME
        self.region = settings.AWS_REGION
        
        # Initialize DynamoDB client
        try:
            if settings.AWS_ENDPOINT_URL:
                # For local development with DynamoDB Local
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    endpoint_url=settings.AWS_ENDPOINT_URL,
                    region_name=self.region
                )
                logger.info(f"Connected to DynamoDB Local at {settings.AWS_ENDPOINT_URL}")
            else:
                self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
                logger.info(f"Connected to DynamoDB in region {self.region}")
            
            self.table = self.dynamodb.Table(self.table_name)
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB client: {str(e)}")
            raise DatabaseException("initialization", str(e))

    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event in DynamoDB"""
        try:
            # Use provided eventId or generate a new one
            event_id = event_data.pop('eventId', None) or str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                "eventId": event_id,
                "createdAt": timestamp,
                "updatedAt": timestamp,
                **event_data
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Created event with ID: {event_id}")
            return item
        except ClientError as e:
            logger.error(f"Failed to create event: {e.response['Error']['Message']}")
            raise DatabaseException("create", e.response['Error']['Message'])
        except Exception as e:
            logger.error(f"Unexpected error creating event: {str(e)}")
            raise DatabaseException("create", str(e))

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get an event by ID"""
        try:
            response = self.table.get_item(Key={"eventId": event_id})
            item = response.get("Item")
            if item:
                logger.debug(f"Retrieved event: {event_id}")
            return item
        except ClientError as e:
            logger.error(f"Failed to get event {event_id}: {e.response['Error']['Message']}")
            raise DatabaseException("get", e.response['Error']['Message'])
        except Exception as e:
            logger.error(f"Unexpected error getting event {event_id}: {str(e)}")
            raise DatabaseException("get", str(e))

    def list_events(self, limit: Optional[int] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events with optional limit and status filter"""
        try:
            scan_kwargs = {}
            if limit:
                scan_kwargs['Limit'] = min(limit, settings.MAX_EVENTS_PER_REQUEST)
            
            # Add status filter if provided
            if status_filter:
                scan_kwargs['FilterExpression'] = Attr('status').eq(status_filter)
            
            response = self.table.scan(**scan_kwargs)
            items = response.get("Items", [])
            logger.info(f"Retrieved {len(items)} events" + (f" with status={status_filter}" if status_filter else ""))
            return items
        except ClientError as e:
            logger.error(f"Failed to list events: {e.response['Error']['Message']}")
            raise DatabaseException("list", e.response['Error']['Message'])
        except Exception as e:
            logger.error(f"Unexpected error listing events: {str(e)}")
            raise DatabaseException("list", str(e))

    def update_event(self, event_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an event"""
        if not update_data:
            return self.get_event(event_id)
        
        try:
            # Build update expression with ExpressionAttributeNames for reserved keywords
            update_expr = "SET updatedAt = :updatedAt"
            expr_attr_values = {":updatedAt": datetime.utcnow().isoformat()}
            expr_attr_names = {}
            
            for key, value in update_data.items():
                if value is not None:
                    # Use ExpressionAttributeNames to handle reserved keywords
                    attr_name = f"#{key}"
                    update_expr += f", {attr_name} = :{key}"
                    expr_attr_values[f":{key}"] = value
                    expr_attr_names[attr_name] = key
            
            update_params = {
                "Key": {"eventId": event_id},
                "UpdateExpression": update_expr,
                "ExpressionAttributeValues": expr_attr_values,
                "ConditionExpression": "attribute_exists(eventId)",
                "ReturnValues": "ALL_NEW"
            }
            
            # Only add ExpressionAttributeNames if we have any
            if expr_attr_names:
                update_params["ExpressionAttributeNames"] = expr_attr_names
            
            response = self.table.update_item(**update_params)
            logger.info(f"Updated event: {event_id}")
            return response.get("Attributes")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"Event not found for update: {event_id}")
                raise EventNotFoundException(event_id)
            logger.error(f"Failed to update event {event_id}: {e.response['Error']['Message']}")
            raise DatabaseException("update", e.response['Error']['Message'])
        except Exception as e:
            logger.error(f"Unexpected error updating event {event_id}: {str(e)}")
            raise DatabaseException("update", str(e))

    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            self.table.delete_item(
                Key={"eventId": event_id},
                ConditionExpression="attribute_exists(eventId)"
            )
            logger.info(f"Deleted event: {event_id}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"Event not found for deletion: {event_id}")
                raise EventNotFoundException(event_id)
            logger.error(f"Failed to delete event {event_id}: {e.response['Error']['Message']}")
            raise DatabaseException("delete", e.response['Error']['Message'])
        except Exception as e:
            logger.error(f"Unexpected error deleting event {event_id}: {str(e)}")
            raise DatabaseException("delete", str(e))


# Singleton instance
db_client = DynamoDBClient()
