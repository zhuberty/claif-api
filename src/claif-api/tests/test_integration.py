import requests
import pytest
from utils.config import get_auth_headers
from utils.files import read_and_encode_file


@pytest.mark.order(2)
def test_create_terminal_recording(base_url, access_token):
    """Test creating a new TerminalRecording."""

    # File path to the sample recording file
    file_path = "asciinema_recording_samples/recording_1_revision_3.txt"
    
    # Read and encode the recording content
    encoded_content = read_and_encode_file(file_path)


    # Construct the payload for creating a new TerminalRecording
    payload = {
        "creator_id": 2,
        "title": "Writing a small hello-world Python function",
        "description": "The user writes a small Python function that prints 'Hello, Annotations!'",
        "recording_content": encoded_content,  # Base64-encoded content of the recording
        "source_revision_id": 1,
        "previous_revision_id": 2,
        "revision_number": 3,
    }

    # Get authorization headers
    headers = get_auth_headers(access_token)
    
    # Make the POST request to the /create endpoint
    url = f"{base_url}/recordings/terminal/create"
    response = requests.post(url, json=payload, headers=headers)

    # Assert the response status and content
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Recording created"
    assert "recording" in response_data
