from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    RemovalPolicy
)
from constructs import Construct
import os

class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB Tables
        
        # Events Table (existing)
        events_table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # For dev/testing only
        )
        
        # Users Table
        users_table = dynamodb.Table(
            self, "UsersTable",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Registration Events Table
        registration_events_table = dynamodb.Table(
            self, "RegistrationEventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Registrations Table with GSIs
        registrations_table = dynamodb.Table(
            self, "RegistrationsTable",
            partition_key=dynamodb.Attribute(
                name="registrationId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSI for querying by userId
        registrations_table.add_global_secondary_index(
            index_name="UserIdIndex",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Add GSI for querying by eventId
        registrations_table.add_global_secondary_index(
            index_name="EventIdIndex",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Waitlist Table with GSI
        waitlist_table = dynamodb.Table(
            self, "WaitlistTable",
            partition_key=dynamodb.Attribute(
                name="entryId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Add GSI for querying by eventId and position
        waitlist_table.add_global_secondary_index(
            index_name="EventIdPositionIndex",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="position",
                type=dynamodb.AttributeType.NUMBER
            )
        )
        
        # Lambda Layer for dependencies
        lambda_layer = _lambda.LayerVersion(
            self, "DependenciesLayer",
            code=_lambda.Code.from_asset("../backend", 
                bundling={
                    "image": _lambda.Runtime.PYTHON_3_11.bundling_image,
                    "platform": "linux/amd64",  # Force x86_64 architecture for Lambda
                    "command": [
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output/python --platform manylinux2014_x86_64 --only-binary=:all: && " +
                        "rm -rf /asset-output/python/*.dist-info"
                    ]
                }
            ),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="FastAPI and dependencies"
        )
        
        # Lambda Function
        api_lambda = _lambda.Function(
            self, "EventsApiFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("../backend"),
            layers=[lambda_layer],
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "DYNAMODB_TABLE_NAME": events_table.table_name,
                "USERS_TABLE_NAME": users_table.table_name,
                "REGISTRATION_EVENTS_TABLE_NAME": registration_events_table.table_name,
                "REGISTRATIONS_TABLE_NAME": registrations_table.table_name,
                "WAITLIST_TABLE_NAME": waitlist_table.table_name
                # AWS_REGION is automatically set by Lambda runtime
            }
        )
        
        # Grant DynamoDB permissions
        events_table.grant_read_write_data(api_lambda)
        users_table.grant_read_write_data(api_lambda)
        registration_events_table.grant_read_write_data(api_lambda)
        registrations_table.grant_read_write_data(api_lambda)
        waitlist_table.grant_read_write_data(api_lambda)
        
        # API Gateway
        api = apigw.LambdaRestApi(
            self, "EventsApi",
            handler=api_lambda,
            proxy=True,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["*"]
            ),
            description="Events API Gateway"
        )
        
        # Outputs
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway endpoint URL"
        )
        
        CfnOutput(
            self, "EventsTableName",
            value=events_table.table_name,
            description="Events DynamoDB table name"
        )
        
        CfnOutput(
            self, "UsersTableName",
            value=users_table.table_name,
            description="Users DynamoDB table name"
        )
        
        CfnOutput(
            self, "RegistrationEventsTableName",
            value=registration_events_table.table_name,
            description="Registration Events DynamoDB table name"
        )
        
        CfnOutput(
            self, "RegistrationsTableName",
            value=registrations_table.table_name,
            description="Registrations DynamoDB table name"
        )
        
        CfnOutput(
            self, "WaitlistTableName",
            value=waitlist_table.table_name,
            description="Waitlist DynamoDB table name"
        )
