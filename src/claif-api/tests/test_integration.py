import json
import requests
import pytest
from sqlalchemy.orm.session import Session
from utils.config import get_auth_headers
from utils.files import read_first_line_of_file, read_file
from utils.database import get_db
from utils.auth import extract_keycloak_id_from_token
from models.recordings import TerminalRecording
from models.annotations import TerminalRecordingAnnotation
from models.users import User
from models.utils.schema import get_model_schema_string
from tests.conftest import logger


@pytest.mark.order(1)
def test_set_user_keycloak_id(access_token):
    """Test setting the Keycloak ID for the test user."""
    db: Session = next(get_db())
    user = db.query(User).filter_by(username="user1").first()
    assert user is not None, "User not found"
    user.keycloak_id = extract_keycloak_id_from_token(access_token)
    db.commit()
    db.refresh(user)
    assert len(user.keycloak_id) == 36, "Invalid Keycloak ID length"


@pytest.mark.order(2)
def test_get_schema_string():
    """Test getting the schema string for the TerminalRecording model."""
    schema_string = get_model_schema_string(TerminalRecording)
    assert schema_string is not None
    assert schema_string.startswith("### ")
    assert schema_string.endswith("```\n\n")


@pytest.mark.order(3)
def test_create_terminal_recording(base_url, access_token):
    """Test creating a new TerminalRecording."""

    # File path to the sample recording file
    file_path = "asciinema_recording_samples/recording_1_revision_1.txt"
    
    # Read and encode the recording content
    recording_content = read_file(file_path)

    # Construct the payload for creating a new TerminalRecording
    payload = {
        "title": "Writing a small hello-world Python function",
        "description": "The user writes a small Python function that prints 'Hello, Annotations!'",
        "recording_content": recording_content,
    }

    # Get authorization headers
    headers = get_auth_headers(access_token)
    
    # Make the POST request to the /create endpoint
    url = f"{base_url}/recordings/terminal/create"
    
    # Try to create the recording
    response = requests.post(url, json=payload, headers=headers)
    
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    response_data = response.json()
    
    saved_recording: TerminalRecording = response_data["recording"]
    assert response_data["message"] == "Recording created"
    assert saved_recording is not None
    
    assert saved_recording["creator_id"] == 2  # Assuming this is the correct user ID
    assert saved_recording["title"] == payload["title"]
    assert saved_recording["description"] == payload["description"]
    assert saved_recording["duration_milliseconds"] > 0
    assert saved_recording["annotations_count"] == 0  # Assuming no annotations on create


@pytest.mark.order(4)
def test_get_created_terminal_recording(base_url, access_token):
    """Test getting a TerminalRecording by ID."""

    # Get authorization headers
    headers = get_auth_headers(access_token)

    # get the recording id of the last recording where revision_number is 1
    db: Session = next(get_db())
    recording = db.query(TerminalRecording).filter_by(revision_number=1).order_by(TerminalRecording.id.desc()).first()

    assert recording is not None, "No recording found"

    # Make the GET request to the /{recording_id} endpoint
    url = f"{base_url}/recordings/terminal/{recording.id}"
    response = requests.get(url, headers=headers)

    # Assert the response status and content
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == recording.id
    assert "content_body" in response_data
    assert response_data["content_body"].startswith("[[")
    assert response_data["content_metadata"].startswith("{")
    assert response_data["duration_milliseconds"] > 0
    assert response_data["annotations_count"] == 0
    assert response_data["revision_number"] == 1
    assert response_data["title"] == "Writing a small hello-world Python function"
    assert response_data["description"] == "The user writes a small Python function that prints 'Hello, Annotations!'"


@pytest.mark.order(5)
def test_update_terminal_recording(base_url, access_token):
    """Test updating an existing TerminalRecording."""

    # File path to the updated sample recording file
    file_path = "asciinema_recording_samples/recording_1_revision_2.txt"
    
    # get the annotations from the updated recording file and encode
    content_metadata = read_first_line_of_file(file_path)

    # get the most recently created recording (which is also the one that was updated)
    db: Session = next(get_db())
    updated_recording = db.query(TerminalRecording).order_by(TerminalRecording.id.desc()).first()

    assert updated_recording is not None, "No recording found"

    # Now update the recording
    headers = get_auth_headers(access_token)
    update_payload = {
        "recording_id": updated_recording.id,  # Pass in the created recording's ID
        "title": "Updated Recording Title",
        "description": "Updated description with more details.",
        "content_metadata" : content_metadata,
    }

    update_url = f"{base_url}/recordings/terminal/update"
    update_response = requests.post(update_url, json=update_payload, headers=headers)
    
    assert update_response.status_code == 200, f"Unexpected status code: {update_response.status_code}"
    update_response_data = update_response.json()

    assert update_response_data["message"] == "Recording updated"


@pytest.mark.order(6)
def test_get_updated_terminal_recording(base_url, access_token):
    """Test getting a TerminalRecording by ID."""

    # Get authorization headers
    headers = get_auth_headers(access_token)

    # get the recording id of the last recording where revision_number is 1
    db: Session = next(get_db())
    recording = db.query(TerminalRecording).order_by(TerminalRecording.id.desc()).first()

    assert recording is not None, "No recording found"

    # Make the GET request to the /{recording_id} endpoint
    url = f"{base_url}/recordings/terminal/{recording.id}"
    response = requests.get(url, headers=headers)

    # Assert the response status and content
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == recording.id
    assert "content_body" in response_data
    assert response_data["content_body"].startswith("[[")
    assert response_data["content_metadata"].startswith("{")
    assert response_data["duration_milliseconds"] > 0
    assert response_data["annotations_count"] == 9
    assert response_data["revision_number"] == 2
    assert response_data["title"] == "Updated Recording Title"
    assert response_data["description"] == "Updated description with more details."


@pytest.mark.order(7)
def test_create_terminal_annotation_review(base_url, access_token):
    """Test creating a new annotation review."""

    # get the recording id of the last recording where revision_number is 2
    db: Session = next(get_db())

    recording = db.query(TerminalRecording).order_by(TerminalRecording.id.desc()).first()
    assert recording is not None, "No recording found"

    annotation: TerminalRecordingAnnotation = recording.annotations.first()
    assert annotation is not None, "No annotations found"

    # Construct the payload for creating a new AnnotationReview
    payload = {
        "annotation_id": annotation.id,
        "recording_id": annotation.recording_id,
        "q_does_anno_match_content": True,
        "q_can_anno_be_halved": False,
        "q_how_well_anno_matches_content": 5,
        "q_can_you_improve_anno": True,
        "q_can_you_provide_markdown": False,
    }

    # Make the POST request to the /create endpoint
    headers = get_auth_headers(access_token)
    url = f"{base_url}/annotation_reviews/create"
    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    response_data = response.json()
    assert response_data["message"] == "Annotation review created"
    assert response_data["annotation_review"] is not None
    assert response_data["annotation_review"]["creator_id"] == 2
    assert response_data["annotation_review"]["annotation_id"] == annotation.id
    assert response_data["annotation_review"]["recording_id"] == annotation.recording_id
