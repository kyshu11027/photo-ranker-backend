import json
import boto3
import os
from uuid import uuid4
from botocore.exceptions import ClientError
import time
from src.utils import get_cors_headers

def create_session_handler(event, s3_client=None, dynamodb=None):
    # Get CORS headers
    cors_headers = get_cors_headers(event)
    
    if s3_client is None:
        s3_client = boto3.client('s3')

    if dynamodb is None:
        dynamodb = boto3.client('dynamodb')
    
    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'NONE')
    TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'NONE')
    
    # Log the entire event for debugging
    print("Received event:", json.dumps(event))
    
    # Get the body of the request
    try: 
        body = json.loads(event['body'])
    except KeyError:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps('Missing body in request')
        }

    num_images = body.get('numImages', 0)
    session_id = str(uuid4())
    image_ids = []
    item = {
        'sessionId': {'S': session_id},
        'images': {'M': {}},
        'expirationTime': {'N': str(int(time.time()) + 172800)},
    }
    
    for i in range(num_images):
        image_id = f"{session_id}-image-{i}"
        try:
            presigned_url = s3_client.generate_presigned_url('put_object', 
                Params={'Bucket': BUCKET_NAME, 'Key': image_id}, 
                ExpiresIn=3600)
            image_ids.append({
                'id': image_id,
                'url': presigned_url
            })
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': cors_headers,
                'body': json.dumps(f'Error creating presigned url: {str(e)}')
            }
        
        item['images']['M'][image_id] = {
            'M': {
                'rankings': {
                    'L': []
                }
            }
        }

    try:
        dynamodb.put_item(TableName=TABLE_NAME, Item=item)
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps(f'Error uploading item {session_id}: {str(e)}')
        }

    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'sessionId': session_id,
            'imageIds': image_ids,
        })
    }


