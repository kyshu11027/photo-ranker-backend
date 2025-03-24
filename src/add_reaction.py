import json
import os
import psycopg2
from src.utils import get_cors_headers

def add_reaction_handler(event, context, db_connection=None):
    # Get CORS headers
    cors_headers = get_cors_headers(event)

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
            'body': json.dumps({
                'success': False,
                'message': f'Issue receiving event body: {str(e)}'
            })
        }
    
    try:
        guest_id = body['guestId']
        emoji_id = body['emojiId']
        photo_id = body['photoId']
    except KeyError as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({
                'success': False,
                'message': f'Issue with payload: {str(e)}'
            })
        }
    
    created_connection = False
    try:
        if db_connection is None:
            db_connection = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            created_connection = True  # Mark that we created this connection
        
        cursor = db_connection.cursor()

        insert_reaction_query = """
            INSERT INTO reactions (guest_id, emoji_id, photo_id)
            VALUES (%s, %s, %s)
            """
        
        cursor.execute(insert_reaction_query, (guest_id, emoji_id, photo_id))
        db_connection.commit()

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'success': True,
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

