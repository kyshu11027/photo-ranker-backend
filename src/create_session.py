import json
import boto3
import os
from uuid import uuid4
from botocore.exceptions import ClientError
import psycopg2
import time
from src.utils import get_cors_headers

def create_session_handler(event, context, s3_client=None):
    # Get CORS headers
    cors_headers = get_cors_headers(event)
    
    if s3_client is None:
        s3_client = boto3.client('s3')
    
    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'NONE')
    DB_HOST = os.environ.get('DB_HOST', 'NONE')
    DB_NAME = os.environ.get('DB_NAME', 'NONE')
    DB_USER = os.environ.get('DB_USER', 'NONE')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'NONE')
    
    # Log the entire event for debugging
    print("Received event:", json.dumps(event))
    try:
        body = json.loads(event['body'])
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps('Issue receiving event body')
        }
    
    user_id = body.get('userId', 'NONE')
    password = body.get('password', 'NONE')
    num_images = body.get('numImages', 0)
    expires_at = str(int(time.time()) + 604800)
    images = []
    s3_ids = []

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps('Issue connecting to database')
        }
    
    cursor = connection.cursor()

    insert_session_query = """
        INSERT INTO sessions (user_id, password_hash, expires_at)
        VALUES (%s, %s, %s)
        RETURNING session_id;
        """
    insert_photo_query = """
        INSERT INTO photos (session_id, s3_item_id)
        VALUES (%s, %s)
        RETURNING photo_id;
        """
    insert_reaction_query = """
        INSERT INTO reactions (photo_id)
        VALUES (%s)
        """
    try:
        cursor.execute(insert_session_query, (user_id, password, expires_at))
        session_id = cursor.fetchone()[0]

        for i in range(num_images):
            s3_item_id = f'{str(session_id)}-image-{str(i)}'
            cursor.execute(insert_photo_query, (session_id, s3_item_id))
            photo_id = cursor.fetchone()[0]
            if not photo_id:
                raise Exception(f'Failed to insert photo {str(s3_item_id)}')
            
            cursor.execute(insert_reaction_query, (photo_id,))
            s3_ids.append(s3_item_id)


    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps(f'Issue writing to database {str(e)}')
        }
    
    try:
        for s3_id in s3_ids:
            presigned_url = s3_client.generate_presigned_url('put_object', 
                Params={'Bucket': BUCKET_NAME, 'Key': s3_id}, 
                ExpiresIn=3600)
            images.append({
                'id': s3_id,
                'url': presigned_url
            })
    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps(f'Issue generating presigned url: {str(e)}')
        }

    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'sessionId': session_id,
            'imageIds': images,
        })
    }


