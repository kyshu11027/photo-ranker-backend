import sys
import os
import moto
from boto3 import resource, client
from unittest import TestCase
import json

# Add the directory containing your lambda function to the Python path
sys.path.append(os.path.abspath('../../'))
sys.path.append(os.path.abspath('../../src'))
sys.path.append(os.path.abspath('../../test/events'))
sys.path.append(os.path.abspath('../../test/utils'))

from src.classes import LambdaDynamoDBClass, LambdaS3Class
from src.app import create_new_session_handler
from test.utils.unit_utils import UnitTestUtils


@moto.mock_aws
class TestCreateSession(TestCase):
    
    def setUp(self) -> None:
        """
        Create our mocked cloud resources
        """
        # Test variables
        self.utils = UnitTestUtils()
        self.region = 'us-east-1'
        self.test_s3_bucket_name = "unit_test_photo_ranker_s3_bucket"
        self.test_ddb_table_name = "unit_test_photo_ranker_ddb"
        self.test_access_key = "unit_test_access_key"
        self.test_secret_key = "unit_test_secret_key"
        # Set environment variables
        os.environ["DYNAMODB_TABLE_NAME"] = self.test_ddb_table_name
        os.environ["S3_BUCKET_NAME"] = self.test_s3_bucket_name
        os.environ["AWS_ACCESS_KEY_ID"] = self.test_access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.test_secret_key

        # Construct dynamodb mock service
        self.ddb_client = client('dynamodb', region_name=self.region)
        self.ddb_resource = resource('dynamodb', region_name=self.region)
        self.ddb_resource.create_table(
            TableName=self.test_ddb_table_name,
            KeySchema=[{'AttributeName': 'sessionId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'sessionId', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        # Construct s3 mock service
        self.s3_resource = resource('s3', self.region)
        self.s3_client = client('s3', region_name=self.region)
        self.s3_client.create_bucket(Bucket=self.test_s3_bucket_name)

    # @pytest.mark.skip(reason="This test is currently under development")
    def test_create_session_in_ddb(self) -> None:
        """
        Verify given correct parameters, the document will be written to S3 with proper contents.
        """
        test_event = self.utils.load_sample_event_from_file('createSession')

        if not test_event:
            raise ValueError("Test event could not be loaded correctly.")
            
        test_return_value = create_new_session_handler(
            event=test_event, 
            context=None,
            s3_client=self.s3_client,
            dynamodb=self.ddb_client
        )

        response = json.loads(test_return_value['body'])
        image_ids = response.get('imageIds', [])
        session_id = response.get('sessionId', '')

        self.assertEqual(len(image_ids), 1)
        for image_id in image_ids:
            id = image_id.get('id', '')
            url = image_id.get('url', '')
            self.assertTrue(session_id in id)
            self.assertTrue("https://" in url)

        # Verify item was actually created in DynamoDB
        try:
            item = self.ddb_client.get_item(
                TableName=self.test_ddb_table_name,
                Key={'sessionId': {'S': session_id}}
            )
            self.assertIn('Item', item)
        except Exception as e:
            self.fail(f"Failed to retrieve item from DynamoDB: {str(e)}")

    def tearDown(self) -> None:
        s3_bucket = self.s3_resource.Bucket(self.test_s3_bucket_name)
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()
        self.ddb_client.delete_table(TableName=self.test_ddb_table_name)