import json
import base64
import boto3
from botocore.exceptions import ClientError
import os


s3_client = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
BUCKET_NAME = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    print('received event ' + json.dumps(event))
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
