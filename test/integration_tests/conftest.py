import os
import pytest
import json
import moto
import psycopg2
import requests
import logging
from dotenv import load_dotenv
from boto3 import resource, client
from src.utils import verify_token
import sys

@pytest.fixture(scope="session")
def load_env():
    """Load environment variables for testing."""
    load_dotenv()

@pytest.fixture(scope="function")
def s3_bucket():
    """Create a mocked S3 client and bucket using Moto."""
    with moto.mock_aws():
        region = 'us-east-1'
        bucket_name = "unit_test_photo_ranker_s3_bucket"
        os.environ["S3_BUCKET_NAME"] = bucket_name
        # Create mock S3 client and resource
        s3_client = client("s3", region_name=region)
        s3_resource = resource("s3", region_name=region)
        
        # Create a bucket
        s3_client.create_bucket(Bucket=bucket_name)
        
        yield s3_client, bucket_name  # Return both client and bucket name

        # Cleanup: Delete bucket and objects
        bucket = s3_resource.Bucket(bucket_name)
        for obj in bucket.objects.all():
            obj.delete()
        bucket.delete()

@pytest.fixture(scope="function")
def get_test_jwt():
    """Obtain a test JWT token from Auth0."""
    def _get_jwt(auth0_domain, client_id, client_secret, api_audience):
        token_response = requests.post(f'{auth0_domain}/oauth/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'audience': api_audience,
            'grant_type': 'client_credentials'
        })
        token_response.raise_for_status()
        return token_response.json().get('access_token')
    
    return _get_jwt

@pytest.fixture(scope="function")
def load_sample_event():
    """Fixture to load a sample test event from a JSON file."""
    def _load_sample_event(file_name):
        with open(f"test/events/{file_name}.json", "r", encoding='utf-8') as file_handle:
            return json.load(file_handle)
    return _load_sample_event

@pytest.fixture(scope="function")
def test_user(db_connection, get_test_jwt, load_env):
    """Create a test user in the database and return their token & user_id."""
    conn, cursor = db_connection
    email = "test@test.com"
    
    # Fetch Auth0 environment variables
    auth0_domain = os.environ['AUTH0_DOMAIN']
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    api_audience = os.environ['API_AUDIENCE']
    
    # Generate test JWT
    access_token = get_test_jwt(auth0_domain, client_id, client_secret, api_audience)

    # Verify token & extract user_id
    test_event = {"headers": {"Authorization": f"Bearer {access_token}"}}
    payload = verify_token(test_event)
    user_id = payload['sub']

    # Insert test user into database
    cursor.execute("INSERT INTO accounts (user_id, email) VALUES (%s, %s)", (user_id, email))
    conn.commit()

    return access_token, user_id

@pytest.fixture(scope="function")
def test_session(db_connection, test_user):
    """Create a test session and return session_id and a photo_id"""
    conn, cursor = db_connection
    _, user_id = test_user

    insert_session_query = """
        INSERT INTO sessions (user_id)
        VALUES (%s)
        RETURNING session_id;
        """
    insert_photo_query = """
        INSERT INTO photos (photo_id, session_id)
        VALUES (%s, %s)
        RETURNING photo_id;
        """
    
    cursor.execute(insert_session_query, (user_id,))
    session_id = cursor.fetchone()[0]
    conn.commit()

    TEST_PHOTO_ID = 'TEST_PHOTO_ID'
    cursor.execute(insert_photo_query, (TEST_PHOTO_ID, session_id))
    conn.commit

    return session_id, TEST_PHOTO_ID

@pytest.fixture(scope="session")
def logger():
    """Configures and returns a logger for tests."""
    logger = logging.getLogger("pytest_tests")
    logger.setLevel(logging.DEBUG)  # Set logging level (DEBUG, INFO, WARNING, ERROR)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # Set log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Avoid duplicate handlers
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger

@pytest.fixture(scope="function")
def db_connection(postgresql):
    """
    Creates a fresh PostgreSQL database connection for each test function.
    This fixture uses pytest-postgresql to provide a temporary database.
    """
    # Create tables in the test database
    schema_sql = """
        CREATE TABLE accounts (
        user_id text PRIMARY KEY,
        email TEXT NOT NULL
        );

        CREATE TABLE sessions (
        session_id SERIAL PRIMARY KEY,
        user_id text NOT NULL,
        password_hash TEXT,
        url TEXT, 
        expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
        FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE
        );

        CREATE TABLE photos (
            photo_id text PRIMARY KEY,
            session_id INT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
        );

        CREATE TABLE guests (
        	guest_id text primary key,
        	name text default 'guest',
        	session_id int not null,
            is_owner BOOLEAN DEFAULT FALSE,
        	foreign key (session_id) references sessions(session_id) on delete cascade
        );

        CREATE TABLE comments (
            comment_id SERIAL PRIMARY KEY,
            photo_id text NOT NULL,
            guest_id text not null,
            comment TEXT,
            FOREIGN KEY (photo_id) REFERENCES photos(photo_id) ON DELETE cascade,
            foreign key (guest_id) references guests(guest_id)
        );

        CREATE TABLE reactions (
            reaction_id SERIAL PRIMARY KEY,
            guest_id text not null,
            photo_id text not null,
            emoji_id text not null,
            FOREIGN KEY (photo_id) REFERENCES photos(photo_id) ON DELETE cascade,
            foreign key (guest_id) references guests(guest_id)
        );

        CREATE INDEX comments_photo_id_guest_id_index ON comments(photo_id, guest_id);
        CREATE INDEX comments_photo_id_index ON comments(photo_id);
        CREATE INDEX comments_guest_id_index ON comments(guest_id);

        CREATE INDEX reactions_guest_id_photo_id_index ON reactions(guest_id, photo_id);
        CREATE INDEX reactions_guest_id_index ON reactions(guest_id);
        CREATE INDEX reactions_photo_id_index ON reactions(photo_id);

        CREATE INDEX photos_session_id_index ON photos(session_id);

        CREATE INDEX session_user_id_index ON sessions(user_id);

        CREATE INDEX guests_session_id_index ON guests(session_id);
    """

    # Connect to the test database
    conn = postgresql
    cursor = conn.cursor()
    cursor.execute(schema_sql)
    conn.commit()

    yield conn, cursor  # Provide the connection and cursor to the test

    # Cleanup: Close connection
    cursor.close()
    conn.close()
