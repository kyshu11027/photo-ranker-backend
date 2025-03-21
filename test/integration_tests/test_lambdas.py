import sys
import os
import moto
from boto3 import resource, client
from unittest import TestCase
from dotenv import load_dotenv
import psycopg2
import json
import logging

# Add the directory containing your lambda function to the Python path
sys.path.append(os.path.abspath('../../'))
sys.path.append(os.path.abspath('../../src'))
sys.path.append(os.path.abspath('../../test/events'))
sys.path.append(os.path.abspath('../../test/utils'))

from src.create_session import create_session_handler
from src.delete_session import delete_session_handler
from src.register_user import register_user_handler
from test.utils.unit_utils import UnitTestUtils


@moto.mock_aws
class TestCreateSession(TestCase):
    
    def setUp(self) -> None:
        """
        Create our mocked cloud resources
        """
        # Test variables
        load_dotenv()
        self.utils = UnitTestUtils()
        self.region = 'us-east-1'
        self.test_s3_bucket_name = "unit_test_photo_ranker_s3_bucket"
        self.test_access_key = "unit_test_access_key"
        self.test_secret_key = "unit_test_secret_key"
        self.db_host = os.environ["DB_HOST"]
        self.db_name = os.environ['DB_NAME']
        self.db_user = os.environ['DB_USER']
        self.db_password = os.environ['DB_PASSWORD']
        self.logger = logging.getLogger()
        # Set environment variables
        os.environ["S3_BUCKET_NAME"] = self.test_s3_bucket_name
        os.environ["AWS_ACCESS_KEY_ID"] = self.test_access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = self.test_secret_key

        # Construct s3 mock service
        self.s3_resource = resource('s3', self.region)
        self.s3_client = client('s3', region_name=self.region)
        self.s3_client.create_bucket(Bucket=self.test_s3_bucket_name)

        self.connection = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
        self.cursor = self.connection.cursor()

    def test_create_session_in_postgres(self) -> None:
        """
        Verify given correct parameters, the document will be written to S3 with proper contents.
        """
        test_event = self.utils.load_sample_event_from_file('createSession')

        if not test_event:
            raise ValueError("Test event could not be loaded correctly.")
            
        test_return_value = create_session_handler(
            event=test_event, 
            context=None,
            s3_client=self.s3_client
        )

        response = json.loads(test_return_value['body'])
        print(response)
        image_ids = response.get('imageIds', [])
        session_url = response.get('sessionUrl', '')
        session_id = response.get('sessionId', '')
        self.logger.info('Session information: %s', {
            session_url: session_url,
            session_id: session_id,
        })

        self.assertEqual(len(image_ids), 1)
        for image_id in image_ids:
            id = image_id.get('id', '')
            url = image_id.get('url', '')
            self.assertTrue(str(session_url) in id)
            self.assertTrue("https://" in url)
    
        try:
            # Assert that the rows were written in the sessions table
            self.cursor.execute("SELECT * FROM sessions WHERE session_id = %s", (session_id,))
            rows = self.cursor.fetchall()
            self.assertTrue(len(rows) == 1)
        
        except Exception as e:
            self.fail(f"Failed to retrieve session from Postgres: {str(e)}")
        
        try:
            # Assert that the rows were written in the photos table
            self.cursor.execute("SELECT * FROM photos WHERE session_id = %s", (session_id,))
            photo_id = self.cursor.fetchone()[0]
            self.assertTrue(image_ids[0].get('id', '') == photo_id)
        except Exception as e:
            self.fail(f"Failed to retrieve photo from Postgres: {str(e)}")
        
        try:
            # Assert that the rows were written to the reactions table
            self.cursor.execute("SELECT * FROM reactions WHERE photo_id = %s", (photo_id,))
            rows = self.cursor.fetchall()
            self.assertTrue(len(rows) == 1)
        except Exception as e:
            self.fail(f"Failed to retrieve reaction from Postgres: {str(e)}")

        # Cleanup
        try:
            self.cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
            self.connection.commit()
        except Exception as e:
            self.logger.error('Error cleaning up created session')

    def test_delete_session_in_postgres(self) -> None:
        test_event = self.utils.load_sample_event_from_file('createSession')
        test_return_value = create_session_handler(
            event=test_event, 
            context=None,
            s3_client=self.s3_client
        )

        response = json.loads(test_return_value['body'])
        session_id = response.get('sessionId')
        session_url = response.get('sessionUrl')
        self.logger.info('Session created: %s', {
            session_id: session_id,
            session_url: session_url
        })
        self.assertIsNotNone(session_id)

        test_event = self.utils.load_sample_event_from_file('deleteSession')

        if not test_event:
            raise ValueError("Test event could not be loaded correctly.")
            
        body = json.loads(test_event['body'])
        body['sessionId'] = session_id
        body['sessionUrl'] = session_url
        test_event['body'] = json.dumps(body)

        test_return_value = delete_session_handler(
            event=test_event, 
            context=None,
            s3_client=self.s3_client
        )
        response = json.loads(test_return_value['body'])
        print(json.dumps(response))
        success = response.get('success', False)
        self.assertTrue(success)

        try:
            # Assert that the rows were written in the sessions table
            self.cursor.execute("SELECT * FROM sessions WHERE session_id = %s", (session_id,))
            rows = self.cursor.fetchall()
            self.assertTrue(len(rows) == 0)
        
        except Exception as e:
            self.fail(f"Failed to verify session deletion from Postgres: {str(e)}")
        
        try:
            # Assert that the rows were written in the photos table
            self.cursor.execute("SELECT * FROM photos WHERE session_id = %s", (session_id,))
            photo_ids = self.cursor.fetchall()
            self.assertTrue(len(photo_ids) == 0)
        except Exception as e:
            self.fail(f"Failed to verify photo deletion from Postgres: {str(e)}")

    def test_register_user_in_postgres(self) -> None:
        test_event = self.utils.load_sample_event_from_file('registerUser')
        TEST_USER_ID = 'TESTUSER'
        TEST_EMAIL = 'test@test.com'
        body = json.loads(test_event['body'])
        body['userId'] = TEST_USER_ID
        body['email'] = TEST_EMAIL
        test_event['body'] = json.dumps(body)

        
        try:
            response = register_user_handler(
                event=test_event, 
                context=None,
            )
            self.logger.debug(json.dumps(response))
            print(json.dumps(response))
            # Assert that the rows were written in the photos table
            self.cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (TEST_USER_ID,))
            account = self.cursor.fetchone()
            self.assertTrue(account[0] == TEST_USER_ID)
            self.assertTrue(account[1] == TEST_EMAIL)

        except Exception as e:
            self.fail(f"Failed to verify user insertion from Postgres: {str(e)}")

        # Cleanup

        # try: 
        #     self.cursor.execute("DELETE FROM accounts WHERE user_id = %s", (TEST_USER_ID,))
        #     self.connection.commit()
        # except Exception as e:
        #     self.logger.error('Failed to clean up after creating account', e)

        return



    def tearDown(self) -> None:
        s3_bucket = self.s3_resource.Bucket(self.test_s3_bucket_name)
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()

        if self.connection != None:
            self.cursor.close()
            self.connection.close()