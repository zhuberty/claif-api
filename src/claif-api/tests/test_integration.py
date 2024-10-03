import requests
import pytest
from sqlalchemy.orm.session import Session
from utils.config import get_auth_headers
from utils.files import read_and_encode_file
from utils.auth import get_db
from models.terminal_recordings import TerminalRecording
from tests.conftest import logger


@pytest.mark.order(1)
def test_get_terminal_recording(base_url, access_token):
    """Test getting a TerminalRecording by ID."""

    # Recording ID to get
    recording_id = 2

    # Get authorization headers
    headers = get_auth_headers(access_token)

    # Make the GET request to the /{recording_id} endpoint
    url = f"{base_url}/recordings/terminal/{recording_id}"
    response = requests.get(url, headers=headers)

    # Assert the response status and content
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == recording_id
    assert "content_body" in response_data
    assert response_data["content_body"].startswith("[[")
    assert response_data["duration_milliseconds"] > 0
    assert response_data["annotations_count"] == 9


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

    # Get the database session
    db: Session = next(get_db())

    # Get authorization headers
    headers = get_auth_headers(access_token)
    
    # Make the POST request to the /create endpoint
    url = f"{base_url}/recordings/terminal/create"
    
    for i in range(2):
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            logger.info("status_code=200: Recording created successfully")
            response_data = response.json()
            assert response_data["message"] == "Recording created"

            recording = db.query(TerminalRecording).filter_by(source_revision_id=1, revision_number=3).first()
            assert recording is not None
            assert recording.creator_id == 2
            assert recording.title == "Writing a small hello-world Python function"
            assert recording.description == "The user writes a small Python function that prints 'Hello, Annotations!'"
            assert "bash prompt visible" in recording.content_metadata
            assert recording.duration_milliseconds == 57975.151
            assert recording.size_bytes == 	16722
            assert recording.annotations_count == 9
            assert recording.is_deleted is False

        else:
            detail_msg = "Recording with source ID 1 already exists with revision number 3"
            logger.info(f"status_code=400: {detail_msg}")
            assert response.status_code == 400
            response_data = response.json()
            assert response_data["detail"] == detail_msg

            # delete the terminal recording with sqlalchemy query
            logger.info("Deleting the terminal recordings with source ID 1 and revision number 3")
            recordings: list[TerminalRecording] = db.query(TerminalRecording).filter_by(source_revision_id=1, revision_number=3).all()
            for recording in recordings:
                logger.info(f"Deleting the terminal recording with ID {recording.id} and its annotations.")
                recording.annotations.delete()
                db.delete(recording)
                db.commit()
