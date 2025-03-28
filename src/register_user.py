import json
import os
import psycopg2
from utils import get_cors_headers, verify_token

def register_user_handler(event, context, db_connection=None):
    cors_headers = get_cors_headers(event)
    try:
        jwt = verify_token(event)
        if "add:user" not in jwt["scope"]:
            raise Exception("Unauthorized")
    except Exception as e:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({
                'success': False,
                'message': f'Failed to verify token: {str(e)}'
            })
        }

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
            'body': json.dumps({
                'success': False,
                'message': f'Issue receiving event body: {str(e)}'
            })
        }

    try:
        user_id = body['userId']
        email = body['email']
    except KeyError as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({
                'success': False,    
                'message': f'Issue getting fields from payload: {str(e)}'
            })
        }

    created_connection = False
    try:
        if db_connection is None:
            connection = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            created_connection = True

        cursor = connection.cursor()

        # Check if the user_id already exists
        check_user_query = "SELECT 1 FROM accounts WHERE user_id = %s"
        cursor.execute(check_user_query, (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'success': True,
                    'message': 'User ID already exists'
                })
            }
        
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
            'body': json.dumps({
                'success': False,
                'message': f'Issue with database: {str(e)}'
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
            'success': True,
            'userId': user_id
        })
    }