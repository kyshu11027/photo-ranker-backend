import json
import os
import psycopg2
from src.utils import get_cors_headers

def register_user_handler(event, context):
    
    cors_headers = get_cors_headers(event)

    DB_HOST = os.environ.get('DB_HOST', 'NONE')
    DB_NAME = os.environ.get('DB_NAME', 'NONE')
    DB_USER = os.environ.get('DB_USER', 'NONE')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'NONE')
    
    print("Received event:", json.dumps(event))
    try:
        body = json.loads(event['body'])
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps('Issue receiving event body')
        }

    try:
        user_id = body['userId']
        email = body['email']
    except KeyError as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps(f'Issue getting fields from payload: {str(e)}')
        }

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        insert_user_query = """
            INSERT INTO accounts (user_id, email)
            VALUES (%s, %s)
            """
        cursor.execute(insert_user_query, (user_id, email))
        connection.commit()
    except psycopg2.Error as e:
        if connection:
            connection.rollback()
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps(f'Issue with database: {str(e)}')
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

    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'success': True,
            'userId': user_id
        })
    }