import pytest
import requests
from sqlalchemy.orm.session import Session
from models.recordings import TerminalRecording
from utils.config import get_auth_headers
from utils.database import get_db
from utils.files import read_file, read_first_line_of_file
from models.utils.schema import get_model_schema_string

@pytest.mark.order(100)
def test_get_schema_string():
    """Test getting the schema string for the TerminalRecording model."""
    schema_string = get_model_schema_string(TerminalRecording)
    assert schema_string is not None
    assert schema_string.startswith("### ")
    assert schema_string.endswith("```\n\n")

@pytest.mark.order(101)
def test_create_terminal_recording(base_url, access_token):
    """Test creating a new TerminalRecording."""
    file_path = "asciinema_recording_samples/recording_1_revision_1.txt"
    recording_content = read_file(file_path)

    payload = {
        "title": "Writing a small hello-world Python function",
        "description": "The user writes a small Python function that prints 'Hello, Annotations!'",
        "recording_content": recording_content,
    }

    headers = get_auth_headers(access_token)
    url = f"{base_url}/recordings/terminal/create"
    response = requests.post(url, json=payload, headers=headers)
    
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    response_data = response.json()
    
    assert response_data["message"] == "Recording created"
    assert response_data["recording_id"] > 0

@pytest.mark.order(102)
def test_get_created_terminal_recording(base_url, access_token):
    """Test getting a TerminalRecording by ID."""
    headers = get_auth_headers(access_token)

    db: Session = next(get_db())
    recording = db.query(TerminalRecording).filter_by(revision_number=1).order_by(TerminalRecording.id.desc()).first()
    assert recording is not None, "No recording found"

    url = f"{base_url}/recordings/terminal/read/{recording.id}"
    response = requests.get(url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["recording"] is not None
    response_recording = response_data["recording"]
    assert response_data["annotations"] == []
    assert response_data["annotation_reviews"] == []
    assert response_recording["id"] == recording.id
    assert response_recording["content_body"].startswith("[[")
    assert response_recording["content_metadata"].startswith("{")
    assert response_recording["duration_milliseconds"] > 0
    assert response_recording["annotations_count"] == 0
    assert response_recording["revision_number"] == 1
    assert response_recording["title"] == "Writing a small hello-world Python function"
    assert response_recording["description"] == "The user writes a small Python function that prints 'Hello, Annotations!'"

@pytest.mark.order(103)
def test_update_terminal_recording(base_url, access_token):
    """Test updating an existing TerminalRecording."""
    file_path = "asciinema_recording_samples/recording_1_revision_2.txt"
    content_metadata = read_first_line_of_file(file_path)

    db: Session = next(get_db())
    updated_recording = db.query(TerminalRecording).order_by(TerminalRecording.id.desc()).first()
    assert updated_recording is not None, "No recording found"

    headers = get_auth_headers(access_token)
    update_payload = {
        "recording_id": updated_recording.id,
        "title": "Updated Recording Title",
        "description": "Updated description with more details.",
        "content_metadata": content_metadata,
    }

    update_url = f"{base_url}/recordings/terminal/update"
    update_response = requests.post(update_url, json=update_payload, headers=headers)
    
    assert update_response.status_code == 200, f"Unexpected status code: {update_response.status_code}"
    update_response_data = update_response.json()

    assert update_response_data["message"] == "Recording updated"

@pytest.mark.order(104)
def test_get_updated_terminal_recording(base_url, access_token):
    """Test getting a TerminalRecording by ID."""
    headers = get_auth_headers(access_token)

    db: Session = next(get_db())
    recording = db.query(TerminalRecording).order_by(TerminalRecording.id.desc()).first()
    assert recording is not None, "No recording found"

    url = f"{base_url}/recordings/terminal/read/{recording.id}"
    response = requests.get(url, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["recording"] is not None
    recording_response = response_data["recording"]
    assert len(response_data["annotations"]) == 9
    assert response_data["annotation_reviews"] == []
    assert recording_response["id"] == recording.id
    assert recording_response["content_body"].startswith("[[")
    assert recording_response["content_metadata"].startswith("{")
    assert recording_response["duration_milliseconds"] > 0
    assert recording_response["annotations_count"] == 9
    assert recording_response["revision_number"] == 2
    assert recording_response["title"] == "Updated Recording Title"
    assert recording_response["description"] == "Updated description with more details."
    assert recording_response["deleted_at"] is None

@pytest.mark.order(105)
def test_list_recordings(base_url, access_token):
    """Test listing all recordings."""
    headers = get_auth_headers(access_token)
    url = f"{base_url}/recordings/terminal/list"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) > 0
    for recording in response_data:
        assert recording["id"] > 0
        assert len(recording["title"]) > 0
        assert len(recording["description"]) > 0
        assert recording["revision_number"] > 0
        assert recording["creator_id"] > 0
