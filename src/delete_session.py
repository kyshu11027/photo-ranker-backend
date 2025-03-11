import boto3
import os
import json
import psycopg2
from botocore.exceptions import ClientError
from src.utils import get_cors_headers


def delete_session_handler(event, context, s3_client=None):
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
    session_id = body.get('sessionId', 'NONE')
    session_url = body.get('sessionUrl', 'NONE')
    objects_to_delete = []

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )        
        cursor = connection.cursor()
        delete_query = """
            DELETE FROM sessions
            WHERE user_id = %s AND session_id = %s AND password_hash = %s;
            """
        
        cursor.execute(delete_query, (user_id, session_id, password))
        connection.commit()
        
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
            'body': json.dumps(f'Issue with S3 object deletion: {str(e)}')
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps(f'Unexpected error: {str(e)}')
        }
    
    finally:
        if connection != None:
            cursor.close()
            connection.close()

    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            "success": db_deletion_success
        })
    }