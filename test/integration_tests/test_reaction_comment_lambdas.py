import json
import pytest
from uuid import uuid4
from src.add_reaction import add_reaction_handler
from src.remove_reaction import remove_reaction_handler

def test_add_remove_reaction_lambda(db_connection, test_session, logger, load_sample_event):
    session_id, photo_id = test_session
    conn, cursor = db_connection
    TEST_GUEST_ID = 'TEST_GUEST_ID'
    test_event = load_sample_event('testEvent')
    test_event['body'] = json.dumps({
        'guestId': TEST_GUEST_ID,
        'emojiId': 'smiley',
        'photoId': photo_id
    })

    cursor.execute('INSERT INTO guests (guest_id, session_id) VALUES (%s, %s)', (TEST_GUEST_ID, session_id))
    conn.commit()

    test_return_value = add_reaction_handler(
        event=test_event,
        context=None,
        db_connection=conn
    )
    logger.info('Add reaction return value: %s', test_return_value)
    assert test_return_value['statusCode'] == 200
    
    try:
        cursor.execute("SELECT * FROM reactions WHERE photo_id=%s", (photo_id,))
        rows = cursor.fetchall()
        assert len(rows) == 1
    except Exception as e:
        pytest.fail(f'Failed to retrieve reaction from Postgres: {str(e)}')

    test_return_value = remove_reaction_handler(
        event=test_event,
        context=None,
        db_connection=conn
    )
    logger.info('Remove reaction return value: %s', test_return_value)

    assert test_return_value['statusCode'] == 200
    try:
        cursor.execute("SELECT * FROM reactions WHERE photo_id=%s", (photo_id,))
        rows = cursor.fetchall()
        assert len(rows) == 0
    except Exception as e:
        pytest.fail(f'Failed to verify no reaction from Postgres: {str(e)}')