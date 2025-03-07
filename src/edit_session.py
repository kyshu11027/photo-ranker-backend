import boto3
import json
import os
from utils import get_cors_headers

def edit_session_handler(event, s3_client=None, dynamodb=None):
    # Get CORS headers
    cors_headers = get_cors_headers(event)
    
    if s3_client is None:
        s3_client = boto3.client('s3')

    if dynamodb is None:
        dynamodb = boto3.client('dynamodb')

    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'NONE')
    TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'NONE')
    # Extract sessionId, imageId, and newRanking from the event
    body = json.loads(event['body'])
    sessionId = body.get('sessionId')

    rankings = body['rankings']

    imageId = body.get('imageId')
    newRanking = body.get('newRanking')
    update_response = []
    try:

        for ranking in rankings:
            imageId = ranking['imageId']
            newRanking = ranking['newRanking']
            

            # Update the rankings list for the specified imageId using ExpressionAttributeNames
            response = dynamodb.update_item(
                TableName=TABLE_NAME,
                Key={'sessionId': {'S': sessionId}},
                UpdateExpression="SET #images.#img_id.rankings = list_append(#images.#img_id.rankings, :newRanking)",
                ExpressionAttributeNames={
                    '#images': 'images',
                    '#img_id': imageId  # Using imageId as an attribute name here
                },
                ExpressionAttributeValues={
                    ':newRanking': {'L': [{'N': str(newRanking)}]}
                }
            )
            update_response.append({
                "imageId": imageId,
                "message": "ranking updated successfully"
            })
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps(update_response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps(f"Failed to update ranking: {str(e)}")
        }