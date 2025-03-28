import json
import pytest
from src.register_user import register_user_handler

"""
Tests user registration by inserting a user into the database and verifying its existence.
"""
def test_register_user_in_postgres(db_connection, test_user, logger, load_sample_event):

    conn, cursor = db_connection  # Get database connection and cursor

    # Generate a test JWT
    try:
        access_token, TEST_USER_ID = test_user
    except Exception as e:
        pytest.fail(f'Failed to get JWT: {str(e)}')

    # Load test event for registering a user
    test_event = load_sample_event('testEvent')
    test_event['headers']['Authorization'] = f'Bearer {access_token}'

    TEST_EMAIL = 'test@test.com'
    test_event['body'] = json.dumps({
        'userId': TEST_USER_ID,
        'email': TEST_EMAIL
    })

    # Call register user handler
    try:
        response = register_user_handler(event=test_event, context=None)
        logger.debug(json.dumps(response))
        print(json.dumps(response))

        # Verify user was inserted in the accounts table
        cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (TEST_USER_ID,))
        account = cursor.fetchone()

        assert account is not None, "User should be inserted in the database"
        assert account[0] == TEST_USER_ID, f"Expected user ID {TEST_USER_ID}, got {account[0]}"
        assert account[1] == TEST_EMAIL, f"Expected email {TEST_EMAIL}, got {account[1]}"

    except Exception as e:
        pytest.fail(f"Failed to verify user insertion from Postgres: {str(e)}")

    # Cleanup: Delete test user from the database
    try:
        cursor.execute("DELETE FROM accounts WHERE user_id = %s", (TEST_USER_ID,))
        conn.commit()
    except Exception as e:
        logger.error('Failed to clean up after creating account', exc_info=True)