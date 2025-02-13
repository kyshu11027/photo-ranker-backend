import json
import boto3
import os
from uuid import uuid4
from botocore.exceptions import ClientError
import time

def get_aws_clients():
    """Get AWS clients with credentials from environment variables"""
    access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "NONE")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "NONE")
    
    s3_client = boto3.client('s3', 
        region_name='us-east-1', 
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_key
    )
    
    dynamodb = boto3.client('dynamodb', 
        region_name='us-east-1',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_key
    )
    
    return s3_client, dynamodb

def create_new_session_handler(event, context, s3_client=None, dynamodb=None):
    if s3_client is None or dynamodb is None:
        s3_client, dynamodb = get_aws_clients()
    
    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'NONE')
    TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'NONE')
    
    # Log the entire event for debugging
    print("Received event:", json.dumps(event))
    
    # Get the body of the request
    try: 
        body = json.loads(event['body'])
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing body in request')
        }

    num_images = body.get('numImages', 0)
    session_id = str(uuid4())
    headers = event.get('headers', {})
    content_type = headers.get('Content-Type', '')
    image_ids = []
    item = {
        'sessionId': {'S': session_id},
        'images': {'M': {}},
        'expirationTime': {'N': str(int(time.time()) + 172800)},
    }
    
    for i in range(num_images):
        image_id = f"{session_id}-image-{i}"
        try:
            presigned_url = s3_client.generate_presigned_url('put_object', 
                Params={'Bucket': BUCKET_NAME, 'Key': image_id}, 
                ExpiresIn=3600)
            image_ids.append({
                'id': image_id,
                'url': presigned_url
            })
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error creating presigned url: {str(e)}')
            }
        
        item['images']['M'][image_id] = {
            'M': {
                'rankings': {
                    'L': []
                }
            }
        }

    try:
        response = dynamodb.put_item(TableName=TABLE_NAME, Item=item)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error uploading item {session_id}: {str(e)}')
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'sessionId': session_id,
            'imageIds': image_ids,
        })
    }


def get_session_data_handler(event, context, s3_client=None, dynamodb=None):
    if s3_client is None or dynamodb is None:
        s3_client, dynamodb = get_aws_clients()
    
    BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'NONE')
    TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'NONE')
    
    print('Received event ' + json.dumps(event))
    sessionId = event.get("queryStringParameters", {}).get("sessionId")

    if not sessionId:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "no sessionId available"})
        }

    result = []
    try:
        response = dynamodb.get_item(TableName = TABLE_NAME, Key={
            'sessionId' : {'S': sessionId}
        })

        if 'Item' not in response:
            return {
                'statusCode' : 404,
                'body' : json.dumps({'error' : 'no item found'})
            }

        # Function to convert DynamoDB ranking format to a list of numbers
        def convert_ranking(dynamo_ranking):
            # Extract the numbers from the DynamoDB L (List) format
            return [int(rank['N']) for rank in dynamo_ranking['L']]

        for imageId in response['Item']['images']['M']:
            image = response['Item']['images']['M'][imageId]['M']
            imageRanking = image['rankings']
            imageUrl = s3_client.generate_presigned_url('get_object', Params = {
                'Bucket': BUCKET_NAME,
                'Key': imageId
            }, ExpiresIn=3600)

            # Convert rankings to a simple list of numbers
            converted_ranking = convert_ranking(imageRanking)

            result.append({
                'imageUrl': imageUrl,
                'imageId': imageId,
                'ranking': converted_ranking
            })
        
        return {
            "statusCode" : 200,
            'body' : json.dumps(result)
        }

    except ClientError as e:
        print(f"Error fetching image from S3 or DynamoDB: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }


def update_session_handler(event, context, s3_client=None, dynamodb=None):
    if s3_client is None or dynamodb is None:
        s3_client, dynamodb = get_aws_clients()

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
            'body': json.dumps(update_response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Failed to update ranking: {str(e)}")
        }

