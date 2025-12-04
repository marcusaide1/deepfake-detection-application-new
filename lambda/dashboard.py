import json
import os

def lambda_handler(event, context):
    """
    Returns the CloudWatch dashboard URL and GitHub repo URL
    """
    region = os.environ.get('REGION', 'us-east-1')
    dashboard_name = os.environ.get('DASHBOARD_NAME', 'DeepFake-Monitoring-Dashboard')
    github_repo = os.environ.get('GITHUB_REPO', 'https://github.com/yourusername/deepfake-detection')
    
    dashboard_url = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name={dashboard_name}"
    
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "dashboard_url": dashboard_url,
            "github_repo": github_repo
        })
    }

