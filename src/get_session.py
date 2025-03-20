import json
import boto3
import os
import psycopg2
from botocore.exceptions import ClientError
from src.utils import get_cors_headers

def get_session_handler(event, context, s3_client=None):
    # Get CORS headers
    cors_headers = get_cors_headers(event)
    
    if s3_client is None:
        s3_client = boto3.client('s3')

    try:
        body = json.loads(event['body'])
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps('Issue receiving event body')
        }
    
    session_id = body.get('sessionId', '')
    password = body.get('password', '')
    
    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'NONE')
    DB_HOST = os.environ.get('DB_HOST', 'NONE')
    DB_NAME = os.environ.get('DB_NAME', 'NONE')
    DB_USER = os.environ.get('DB_USER', 'NONE')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'NONE')

    print('Received event ' + json.dumps(event))

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()

        get_session_query = """
            SELECT * FROM photos WHERE session_id = %s
            """
        cursor.execute(get_session_query, (session_id,))
        photos = cursor.fetchall()

        for photo in photos:
            photo_id = photo[0]

            image_url = s3_client.generate_presigned_url('get_object', Params = {
                'Bucket': BUCKET_NAME,
                'Key': photo_id
            }, ExpiresIn=3600)

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'photos': []
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

    for imageId in response['Item']['images']['M']:
        image = response['Item']['images']['M'][imageId]['M']
        imageRanking = image['rankings']
        imageUrl = s3_client.generate_presigned_url('get_object', Params = {
            'Bucket': BUCKET_NAME,
            'Key': imageId
        }, ExpiresIn=3600)