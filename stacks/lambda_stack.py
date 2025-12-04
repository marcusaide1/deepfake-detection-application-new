import os
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
    Duration
)
from constructs import Construct

class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, 
                 image_bucket: s3.Bucket,
                 api_secret: secretsmanager.Secret,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        layer = _lambda.LayerVersion(
            self, 'lambda_layer',
            code=_lambda.Code.from_asset('./layers/layer.zip'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],  
        )
        
        request_layer = _lambda.LayerVersion(
            self, 'request_layer',
            code=_lambda.Code.from_asset('./layers/request.zip'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],  
        )
        
        # Create Log Group for upload lambda with DESTROY removal policy
        upload_log_group = logs.LogGroup(
            self, 'upload_lambda_log_group',
            log_group_name=f'/aws/lambda/deepfake_upload_lambda_function',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK
        )
        
        self.upload_lambda = _lambda.Function(
            self, 'upload_lambda',
            function_name="deepfake_upload_lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            handler='upload.lambda_handler',
            layers=[layer, request_layer],
            tracing=_lambda.Tracing.ACTIVE,
            timeout=Duration.seconds(30),
            log_group=upload_log_group,
            environment={
                'BUCKET_NAME': image_bucket.bucket_name,
                'API_SECRET_ARN': api_secret.secret_arn,
                "POWERTOOLS_SERVICE_NAME": "recieptApp"
            }
            
        )
        
        api_secret.grant_read(self.upload_lambda)
        image_bucket.grant_write(self.upload_lambda)
        
        # Create Log Group for dashboard lambda with DESTROY removal policy
        dashboard_log_group = logs.LogGroup(
            self, 'dashboard_lambda_log_group',
            log_group_name=f'/aws/lambda/deepfake_dashboard_lambda_function',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK
        )
        
        # Dashboard info Lambda
        # Note: AWS_REGION is automatically set by Lambda runtime, don't set it manually
        self.dashboard_lambda = _lambda.Function(
            self, 'dashboard_lambda',
            function_name="deepfake_dashboard_lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            handler='dashboard.lambda_handler',
            timeout=Duration.seconds(10),
            log_group=dashboard_log_group,
            environment={
                "REGION": self.region,
                "DASHBOARD_NAME": "DeepFake-Monitoring-Dashboard",
                "GITHUB_REPO": "https://github.com/echefulouis/DeepFake"
            }
        )

