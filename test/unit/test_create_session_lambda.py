import sys
import os
import moto
from boto3 import resource, client
from unittest import TestCase

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

        # Set environment variables
        os.environ["DYNAMODB_TABLE_NAME"] = self.test_ddb_table_name
        os.environ["S3_BUCKET_NAME"] = self.test_s3_bucket_name

        # Construct dynamodb mock service
        dynamodb = resource('dynamodb', region_name=self.region)
        dynamodb.create_table(
            TableName = self.test_ddb_table_name,
            KeySchema = [{'AttributeName': 'sessionId', 'KeyType': 'HASH'}],
            AttributeDefinitions = [{'AttributeName': 'sessionId', 'AttributeType': 'S'}],
            BillingMode = 'PAY_PER_REQUEST'
        )

        # Construct s3 mock service
        s3_client = client('s3', region_name=self.region)
        s3_client.create_bucket(Bucket=self.test_s3_bucket_name)

        # Set global variables for tests
        mocked_dynamodb_resource = {'resource': resource('dynamodb', self.region),
                                    'table_name': self.test_ddb_table_name}
        mocked_s3_resource = {'resource': resource('s3', self.region),
                              'bucket_name': self.test_s3_bucket_name}
        self.mocked_dynamodb_resource = LambdaDynamoDBClass(mocked_dynamodb_resource)
        self.mocked_s3_resource = LambdaS3Class(mocked_s3_resource)


    def test_create_session_in_ddb(self) -> None:
        """
        Verify given correct parameters, the document will be written to S3 with proper contents.
        """
        test_event = self.utils.load_sample_event_from_file('createSession')
        test_return_value = create_new_session_handler(event=test_event, context=None)

        image_ids = test_return_value.get('imageIds', [])
        session_id = test_return_value.get('sessionId', '')
        print(test_return_value)

        self.assertEqual(len(image_ids), 1)
        for image_id in image_ids:
            id = image_id.get('id', '')
            self.assertTrue(session_id in id)

    
    def tearDown(self) -> None:
        s3_resource = resource("s3",region_name=self.region)
        s3_bucket = s3_resource.Bucket( self.test_s3_bucket_name )
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()

        dynamodb_resource = client("dynamodb", region_name=self.region)
        dynamodb_resource.delete_table(TableName = self.test_ddb_table_name )
