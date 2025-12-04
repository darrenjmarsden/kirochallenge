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
        
        # DynamoDB Table
        events_table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # For dev/testing only
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
                "DYNAMODB_TABLE_NAME": events_table.table_name
                # AWS_REGION is automatically set by Lambda runtime
            }
        )
        
        # Grant DynamoDB permissions
        events_table.grant_read_write_data(api_lambda)
        
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
            self, "TableName",
            value=events_table.table_name,
            description="DynamoDB table name"
        )
