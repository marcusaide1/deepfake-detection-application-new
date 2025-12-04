from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_cloudwatch as cloudwatch,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
)
from constructs import Construct


class DashboardStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, 
                 upload_lambda: _lambda.Function,
                 api_gateway: apigateway.RestApi,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(
            self, "DeepFakeMonitoringDashboard",
            dashboard_name="DeepFake-Monitoring-Dashboard"
        )

        # Lambda Metrics
        lambda_invocations = cloudwatch.Metric(
            namespace="AWS/Lambda",
            metric_name="Invocations",
            dimensions_map={
                "FunctionName": upload_lambda.function_name
            },
            statistic="Sum",
            period=Duration.minutes(3),
            label="Lambda Invocations"
        )

        lambda_errors = cloudwatch.Metric(
            namespace="AWS/Lambda",
            metric_name="Errors",
            dimensions_map={
                "FunctionName": upload_lambda.function_name
            },
            statistic="Sum",
            period=Duration.minutes(5),
            label="Lambda Errors"
        )

        lambda_duration = cloudwatch.Metric(
            namespace="AWS/Lambda",
            metric_name="Duration",
            dimensions_map={
                "FunctionName": upload_lambda.function_name
            },
            statistic="Average",
            period=Duration.minutes(5),
            label="Lambda Duration (ms)"
        )

        lambda_throttles = cloudwatch.Metric(
            namespace="AWS/Lambda",
            metric_name="Throttles",
            dimensions_map={
                "FunctionName": upload_lambda.function_name
            },
            statistic="Sum",
            period=Duration.minutes(5),
            label="Lambda Throttles"
        )

        # API Gateway Metrics - Use API ID for REST APIs
        api_requests = cloudwatch.Metric(
            namespace="AWS/ApiGateway",
            metric_name="Count",
            dimensions_map={
                "ApiName": api_gateway.rest_api_name,
                "Stage": "prod"
            },
            statistic="Sum",
            period=Duration.minutes(5),
            label="API Requests"
        )

        api_4xx_errors = cloudwatch.Metric(
            namespace="AWS/ApiGateway",
            metric_name="4XXError",
            dimensions_map={
                "ApiName": api_gateway.rest_api_name,
                "Stage": "prod"
            },
            statistic="Sum",
            period=Duration.minutes(5),
            label="4XX Errors"
        )

        api_5xx_errors = cloudwatch.Metric(
            namespace="AWS/ApiGateway",
            metric_name="5XXError",
            dimensions_map={
                "ApiName": api_gateway.rest_api_name,
                "Stage": "prod"
            },
            statistic="Sum",
            period=Duration.minutes(5),
            label="5XX Errors"
        )

        api_latency = cloudwatch.Metric(
            namespace="AWS/ApiGateway",
            metric_name="Latency",
            dimensions_map={
                "ApiName": api_gateway.rest_api_name,
                "Stage": "prod"
            },
            statistic="Average",
            period=Duration.minutes(5),
            label="API Latency (ms)"
        )

        # Add widgets to dashboard
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Lambda Invocations",
                left=[lambda_invocations],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="Lambda Errors",
                left=[lambda_errors],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="Lambda Duration",
                left=[lambda_duration],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="Lambda Throttles",
                left=[lambda_throttles],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="API Gateway Requests",
                left=[api_requests],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="API Gateway 4XX Errors",
                left=[api_4xx_errors],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="API Gateway 5XX Errors",
                left=[api_5xx_errors],
                width=12
            ),
            cloudwatch.GraphWidget(
                title="API Gateway Latency",
                left=[api_latency],
                width=12
            ),
        )

        # Output dashboard URL
        dashboard_url = f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?region={self.region}#dashboards:name={dashboard.dashboard_name}"
        
        CfnOutput(
            self, "DashboardURL",
            value=dashboard_url,
            description="CloudWatch Dashboard URL for monitoring"
        )
        
        self.dashboard_url = dashboard_url

