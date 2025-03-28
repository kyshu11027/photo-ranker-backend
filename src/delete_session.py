import boto3
import os
import json
import psycopg2
from botocore.exceptions import ClientError
from utils import get_cors_headers, verify_token


def delete_session_handler(event, context, s3_client=None, db_connection=None):
    cors_headers = get_cors_headers(event)
    try:
        jwt = verify_token(event)
        if "delete:session" not in jwt["scope"]:
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
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({
                'success': False,
                'message': f'Issue receiving event body: {str(e)}'
            })
        }
    
    user_id = jwt['sub'] # We want to ensure that the person deleting this is the session owner
    password = body.get('password', 'NONE')
    session_id = body.get('sessionId', 'NONE')
    session_url = body.get('sessionUrl', 'NONE')
    objects_to_delete = []

    created_connection = False
    try:
        if db_connection is None:
            db_connection = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            created_connection = True
               
        cursor = db_connection.cursor()
        delete_query = """
            DELETE FROM sessions
            WHERE user_id = %s AND session_id = %s AND password_hash = %s;
            """
        
        cursor.execute(delete_query, (user_id, session_id, password))
        db_connection.commit()
        
        db_deletion_success = cursor.rowcount > 0

        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=session_url):
            if 'Contents' in page:
                objects_to_delete.extend([{'Key': obj['Key']} for obj in page['Contents']])

        if objects_to_delete:
            print(f"Found {len(objects_to_delete)} objects to delete...")

            # Delete in batches of 1,000 (S3 API limit)
            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i:i + 1000]
                s3_client.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': batch})
                print(f"Deleted {len(batch)} objects.")

            print("All matching objects deleted.")
        else:
            print("No matching objects found.")

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
                'message': f'Issue with S3 object deletion: {str(e)}'
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

    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            "success": db_deletion_success
        })
    }