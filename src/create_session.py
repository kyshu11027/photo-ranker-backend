import json
import boto3
import os
from uuid import uuid4
from botocore.exceptions import ClientError
import psycopg2
import time
import datetime
from src.utils import get_cors_headers, verify_token

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
    
    user_id = body.get('sub', 'NONE')
    password = body.get('password', 'NONE')
    num_images = body.get('numImages', 0)
    expires_at = datetime.datetime.fromtimestamp(int(time.time()) + 604800)
    url = str(uuid4())
    images = []
    photo_ids = []

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = connection.cursor()

        insert_session_query = """
            INSERT INTO sessions (user_id, password_hash, url, expires_at)
            VALUES (%s, %s, %s, %s)
            RETURNING session_id;
            """
        insert_photo_query = """
            INSERT INTO photos (photo_id, session_id)
            VALUES (%s, %s)
            RETURNING photo_id;
            """
        insert_reaction_query = """
            INSERT INTO reactions (photo_id)
            VALUES (%s)
            """
        
        cursor.execute(insert_session_query, (user_id, password, url, expires_at))
        session_id = cursor.fetchone()[0]

        for i in range(num_images):
            photo_id = f'{url}-image-{str(i)}'
            cursor.execute(insert_photo_query, (photo_id, session_id))
            photo_id = cursor.fetchone()[0]
            if not photo_id:
                raise Exception(f'Failed to insert photo {str(photo_id)}')
            
            cursor.execute(insert_reaction_query, (photo_id,))
            photo_ids.append(photo_id)

        connection.commit()
        
        for photo_id in photo_ids:
            presigned_url = s3_client.generate_presigned_url('put_object', 
                Params={'Bucket': BUCKET_NAME, 'Key': photo_id}, 
                ExpiresIn=3600)
            images.append({
                'id': photo_id,
                'url': presigned_url
            })
            
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'sessionId': session_id, 
                'sessionUrl': url,
                'imageIds': images,
            })
        }
        
    except psycopg2.Error as e:
        if connection:
            connection.rollback()
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps(f'Issue with database: {str(e)}')
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps(f'Issue generating presigned url: {str(e)}')
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps(f'Unexpected error: {str(e)}')
        }
    finally:
        if connection is not None:
            connection.close()
            cursor.close()


