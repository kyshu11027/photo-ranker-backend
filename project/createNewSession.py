import json
import boto3
import os
import base64
from uuid import uuid4
import time

# Initialize the S3 client
s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['S3_BUCKET_NAME']

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')
TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']

def lambda_handler(event, context):
    # Log the entire event for debugging
    print("Received event:", json.dumps(event))
    
    # Get the body of the request
    try:
        body = json.loads(event['body'])
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing body in request')
        }

    num_images = body.get('numImages', 0)
    session_id = str(uuid4())
    headers = event.get('headers', {})
    content_type = headers.get('Content-Type', '')
    image_ids = []
    item = {
        'sessionId': {'S': session_id},  # Specify the type as String
        'images': {'M': {}},  # Initialize as a list
        'expirationTime': {'N': str(int(time.time()) + 172800)},
    }
    for i in range(num_images):
        image_id = f"{session_id}-image-{i}"  # Adjust filename as needed    
        try:
            # Generate a presigned URL for a PUT operation
            presigned_url = s3_client.generate_presigned_url('put_object', Params={'Bucket': BUCKET_NAME, 'Key': image_id}, ExpiresIn=3600)
            image_ids.append({
                'id': image_id,
                'url': presigned_url
            })
        except Exception as e:
            return {
            'statusCode' : 500,
            'body': json.dumps(f'Error creating presigned url: {str(e)}')
        }
        
        item['images']['M'][image_id] = {
            'M': {
                'rankings' : {
                    'L' : []
                }
            }
        }


    try:
        response = dynamodb.put_item(TableName = TABLE_NAME, Item = item)
    except Exception as e:
        return {
            'statusCode' : 500,
            'body': json.dumps(f'Error uploading item {session_id}: {str(e)}')
        }


    return {
        'statusCode': 200,
        'body': json.dumps({
            'sessionId': session_id,
            'imageIds': image_ids,
        })
    }
