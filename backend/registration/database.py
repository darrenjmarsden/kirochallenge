"""Database schema and initialization for registration system"""
import boto3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import logging

from config import settings
from .exceptions import NotFoundError, DuplicateError, RegistrationSystemError

logger = logging.getLogger(__name__)


class RegistrationDatabase:
    """Database client for registration system using DynamoDB"""
    
    def __init__(self):
        self.region = settings.AWS_REGION
        
        # Initialize DynamoDB client
        try:
            if settings.AWS_ENDPOINT_URL:
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    endpoint_url=settings.AWS_ENDPOINT_URL,
                    region_name=self.region
                )
                logger.info(f"Connected to DynamoDB Local at {settings.AWS_ENDPOINT_URL}")
            else:
                self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
                logger.info(f"Connected to DynamoDB in region {self.region}")
            
            # Table names
            self.users_table_name = os.getenv("USERS_TABLE_NAME", "users-table")
            self.registration_events_table_name = os.getenv("REGISTRATION_EVENTS_TABLE_NAME", "registration-events-table")
            self.registrations_table_name = os.getenv("REGISTRATIONS_TABLE_NAME", "registrations-table")
            self.waitlist_table_name = os.getenv("WAITLIST_TABLE_NAME", "waitlist-table")
            
            # Get table references
            self.users_table = self.dynamodb.Table(self.users_table_name)
            self.registration_events_table = self.dynamodb.Table(self.registration_events_table_name)
            self.registrations_table = self.dynamodb.Table(self.registrations_table_name)
            self.waitlist_table = self.dynamodb.Table(self.waitlist_table_name)
            
        except Exception as e:
            logger.error(f"Failed to initialize registration database: {str(e)}")
            raise RegistrationSystemError(f"Database initialization failed: {str(e)}")
    
    def create_tables_if_not_exist(self):
        """Create DynamoDB tables if they don't exist (for local development)"""
        try:
            # Create users table
            try:
                self.users_table.load()
            except ClientError:
                self.dynamodb.create_table(
                    TableName=self.users_table_name,
                    KeySchema=[{'AttributeName': 'userId', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'userId', 'AttributeType': 'S'}],
                    BillingMode='PAY_PER_REQUEST'
                )
                logger.info(f"Created users table: {self.users_table_name}")
            
            # Create registration events table
            try:
                self.registration_events_table.load()
            except ClientError:
                self.dynamodb.create_table(
                    TableName=self.registration_events_table_name,
                    KeySchema=[{'AttributeName': 'eventId', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'eventId', 'AttributeType': 'S'}],
                    BillingMode='PAY_PER_REQUEST'
                )
                logger.info(f"Created registration events table: {self.registration_events_table_name}")
            
            # Create registrations table with GSI for user queries
            try:
                self.registrations_table.load()
            except ClientError:
                self.dynamodb.create_table(
                    TableName=self.registrations_table_name,
                    KeySchema=[{'AttributeName': 'registrationId', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[
                        {'AttributeName': 'registrationId', 'AttributeType': 'S'},
                        {'AttributeName': 'userId', 'AttributeType': 'S'},
                        {'AttributeName': 'eventId', 'AttributeType': 'S'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'UserIdIndex',
                            'KeySchema': [{'AttributeName': 'userId', 'KeyType': 'HASH'}],
                            'Projection': {'ProjectionType': 'ALL'}
                        },
                        {
                            'IndexName': 'EventIdIndex',
                            'KeySchema': [{'AttributeName': 'eventId', 'KeyType': 'HASH'}],
                            'Projection': {'ProjectionType': 'ALL'}
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                logger.info(f"Created registrations table: {self.registrations_table_name}")
            
            # Create waitlist table with GSI for event queries
            try:
                self.waitlist_table.load()
            except ClientError:
                self.dynamodb.create_table(
                    TableName=self.waitlist_table_name,
                    KeySchema=[{'AttributeName': 'entryId', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[
                        {'AttributeName': 'entryId', 'AttributeType': 'S'},
                        {'AttributeName': 'eventId', 'AttributeType': 'S'},
                        {'AttributeName': 'position', 'AttributeType': 'N'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'EventIdPositionIndex',
                            'KeySchema': [
                                {'AttributeName': 'eventId', 'KeyType': 'HASH'},
                                {'AttributeName': 'position', 'KeyType': 'RANGE'}
                            ],
                            'Projection': {'ProjectionType': 'ALL'}
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                logger.info(f"Created waitlist table: {self.waitlist_table_name}")
                
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise RegistrationSystemError(f"Table creation failed: {str(e)}")


# Singleton instance
registration_db = RegistrationDatabase()
