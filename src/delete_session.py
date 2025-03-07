import boto3
from src.utils import get_cors_headers


def delete_session_handler(event, s3_client=None, dynamodb=None):
    #TODO: Implement delete API'
    cors_headers = get_cors_headers(event)
    return {
        "statusCode": 200,
        "headers": cors_headers,
        'body': 'placeholder'
    }