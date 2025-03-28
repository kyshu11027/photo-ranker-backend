import json
import pytest
from src.create_session import create_session_handler
from src.delete_session import delete_session_handler

"""
    Testing the creation of sessions. The test should:
    - Return success
    - Create 2 images in the photos table
    - Have an empty reactions row
    - Insert a row in the sessions table
""" 
def test_create_session_lambda(load_sample_event, test_user, db_connection, s3_bucket, logger):

    access_token, _ = test_user  # Retrieve test user token
    test_event = load_sample_event("testEvent")
    test_event["headers"]["Authorization"] = f"Bearer {access_token}"

    test_event["body"] = json.dumps({
        "password": "test_password",
        "numImages": 1
    })

    s3_client, _ = s3_bucket
    conn, cursor = db_connection

    # Call Lambda function handler
    test_return_value = create_session_handler(
        event=test_event,
        context=None,
        s3_client=s3_client,
        db_connection=conn
    )
    logger.info('Lambda return value: %s', test_return_value)

    response = json.loads(test_return_value['body'])
    image_ids = response.get('imageIds', [])
    session_url = response.get('sessionUrl', '')
    session_id = response.get('sessionId', '')
    logger.info('Session information: %s', response)

    assert test_return_value["statusCode"] == 200
    assert len(image_ids) == 1

    for image_id in image_ids:
        id = image_id.get('id', '')
        url = image_id.get('url', '')
        assert str(session_url) in id
        assert "https://" in url

    try:
        # Assert that the rows were written in the sessions table
        cursor.execute("SELECT * FROM sessions WHERE session_id = %s", (session_id,))
        rows = cursor.fetchall()
        assert len(rows) == 1
    except Exception as e:
        pytest.fail(f"Failed to retrieve session from Postgres: {str(e)}")
    
    try:
        # Assert that the rows were written in the photos table
        cursor.execute("SELECT * FROM photos WHERE session_id = %s", (session_id,))
        photo_id = cursor.fetchone()[0]
        assert image_ids[0].get('id', '') == photo_id
    except Exception as e:
        pytest.fail(f"Failed to retrieve photo from Postgres: {str(e)}")


"""
    Tests that a session is created and then deleted properly in PostgreSQL.
"""
def test_delete_session_lambda(db_connection, test_user, s3_bucket, logger, load_sample_event):
    TEST_PASSWORD = 'test_pass'
    conn, cursor = db_connection  # Get database connection and cursor
    access_token, _ = test_user  # Retrieve test user token

    # Load test event for creating a session
    test_event = load_sample_event('testEvent')
    test_event['headers']['Authorization'] = f'Bearer {access_token}'
    test_event['body'] = json.dumps({"password": TEST_PASSWORD, "numImages": 2})

    s3_client, _ = s3_bucket  # Get S3 client

    # Call create session handler
    test_return_value = create_session_handler(event=test_event, context=None, s3_client=s3_client, db_connection=conn)
    response = json.loads(test_return_value['body'])

    session_id = response.get('sessionId')
    session_url = response.get('sessionUrl')
    logger.info("Session created: %s", {"session_id": session_id, "session_url": session_url})
    
    assert session_id is not None, "Session ID should not be None"

    # Load test event for deleting the session

    if not test_event:
        pytest.fail("Test event could not be loaded correctly.")

    test_event['body'] = json.dumps({
        'sessionId': session_id,
        'password': TEST_PASSWORD
    })

    # Call delete session handler
    test_return_value = delete_session_handler(event=test_event, context=None, s3_client=s3_client, db_connection=conn)
    response = json.loads(test_return_value['body'])
    logger.info('Delete session response: %s', test_return_value)

    success = response.get('success', False)
    assert success, "Session deletion should return success"

    try:
        # Verify session is deleted from the sessions table
        cursor.execute("SELECT * FROM sessions WHERE session_id = %s", (session_id,))
        rows = cursor.fetchall()
        assert len(rows) == 0, "Session should be deleted from the database"

    except Exception as e:
        pytest.fail(f"Failed to verify session deletion from Postgres: {str(e)}")

    try:
        # Verify photos related to the session are deleted
        cursor.execute("SELECT * FROM photos WHERE session_id = %s", (session_id,))
        photo_ids = cursor.fetchall()
        assert len(photo_ids) == 0, "Photos related to session should be deleted"

    except Exception as e:
        pytest.fail(f"Failed to verify photo deletion from Postgres: {str(e)}")