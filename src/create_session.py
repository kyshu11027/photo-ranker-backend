import json
import boto3
import os
from uuid import uuid4
from botocore.exceptions import ClientError
import psycopg2
import time
import datetime
from utils import get_cors_headers, verify_token

def create_session_handler(event, context, s3_client=None, db_connection=None):
    # Get CORS headers
    cors_headers = get_cors_headers(event)
    
    try:
        jwt = verify_token(event)
        if "create:session" not in jwt["scope"]:
            raise Exception("Unauthorized")
    except Exception as e:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps(f'Failed to verify token: {str(e)}')
        }
    
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
    except Exception:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps('Issue receiving event body')
        }

    user_id = jwt['sub']  # Ensure consistency of session ownership
    password = body.get('password', 'NONE')
    num_images = body.get('numImages', 0)
    expires_at = datetime.datetime.fromtimestamp(int(time.time()) + 604800)
    url = str(uuid4())
    images = []
    photo_ids = []

    created_connection = False  # Track if we created the connection

    try:
        # If no db_connection is passed (i.e., production), create a new one
        if db_connection is None:
            db_connection = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            created_connection = True  # Mark that we created this connection
        
        cursor = db_connection.cursor()

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
        
        insert_guest_query = """
            INSERT INTO guests (guest_id, name, session_id, is_owner)
            VALUES (%s, %s, %s)
            """
        
        cursor.execute(insert_session_query, (user_id, password, url, expires_at))
        session_id = cursor.fetchone()[0]

        guest_id = f'{user_id}|{session_id}'
        cursor.execute(insert_guest_query, (guest_id, "Session Owner", session_id, True) )

        for i in range(num_images):
            photo_id = f'{url}-image-{str(i)}'
            cursor.execute(insert_photo_query, (photo_id, session_id))
            photo_id = cursor.fetchone()[0]
            if not photo_id:
                raise Exception(f'Failed to insert photo {str(photo_id)}')
            
            photo_ids.append(photo_id)

        db_connection.commit()
        
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
        if db_connection:
            db_connection.rollback()
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({
                'success': False,
                'message': f'Issue with database: {str(e)}'
            })
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({
                'success': False,
                'message': f'Issue generating presigned url: {str(e)}'
            })
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({
                'success': False,
                'message': f'Unexpected error: {str(e)}'
            })
        }
    finally:
        if 'cursor' in locals():  # Ensure cursor exists before closing
            cursor.close()
        if created_connection and db_connection is not None:  # Only close if we created it
            db_connection.close()
