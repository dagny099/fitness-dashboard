"""
tests/test_session.py - Tests for session management functionality
"""
def test_create_new_session(session_manager):
    """
    Test that we can create a new session and it starts empty.
    Like verifying a new workout tracking sheet is blank.
    """
    # Verify scratchpad starts empty
    assert session_manager.get_scratchpad() == ""
    
    # Verify query history starts empty
    assert len(session_manager.get_query_history()) == 0

def test_update_scratchpad(session_manager):
    """
    Test that we can update and retrieve scratchpad content.
    Like writing notes in your workout log and making sure
    they're saved correctly.
    """
    test_content = "SELECT * FROM workout_summary"
    
    # Update the scratchpad
    session_manager.update_scratchpad(test_content)
    
    # Verify the content was saved
    assert session_manager.get_scratchpad() == test_content

def test_query_history(session_manager):
    """
    Test that query history is recorded correctly.
    Like making sure your workout history is being logged properly.
    """
    test_query = "SELECT COUNT(*) FROM workout_summary"
    test_result = {
        'execution_time': 0.1,
        'row_count': 5
    }
    
    # Add a query to history
    session_manager.add_query_to_history(test_query, test_result)
    
    # Get the history
    history = session_manager.get_query_history()
    
    # Verify the query was recorded
    assert len(history) == 1
    assert history[0]['query'] == test_query
    assert history[0]['result']['row_count'] == 5