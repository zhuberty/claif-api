import pytest
import requests
from sqlalchemy.orm.session import Session
from models.recordings import TerminalRecording
from models.annotations import TerminalRecordingAnnotation
from utils.config import get_auth_headers
from utils.database import get_db

@pytest.mark.order(200)
def test_get_annotations():
    """Test getting all annotations for a recording."""
    db = next(get_db())
    recording = db.query(TerminalRecording).order_by(TerminalRecording.id.desc()).first()
    assert recording is not None, "No recording found"
    annotations: list[TerminalRecordingAnnotation] = recording.annotations.all()
    assert len(annotations) == 9
    for annotation in annotations:
        assert annotation.recording_id == recording.id
        assert annotation.revision_number == recording.revision_number
        assert annotation.level >= 0
        assert len(annotation.annotation_text) > 0

@pytest.mark.order(201)
def test_create_terminal_annotation_review(base_url, access_token):
    """Test creating a new annotation review."""
    db: Session = next(get_db())
    recording = db.query(TerminalRecording).order_by(TerminalRecording.id.desc()).first()
    assert recording is not None, "No recording found"

    annotation: TerminalRecordingAnnotation = recording.annotations.first()
    assert annotation is not None, "No annotations found"

    payload = {
        "annotation_id": annotation.id,
        "q_does_anno_match_content": True,
        "q_can_anno_be_halved": False,
        "q_how_well_anno_matches_content": 5,
        "q_can_you_improve_anno": True,
        "q_can_you_provide_markdown": False,
    }

    headers = get_auth_headers(access_token)
    url = f"{base_url}/annotation_reviews/create"
    response = requests.post(url, json=payload, headers=headers)

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    response_data = response.json()
    assert response_data["message"] == "Annotation review created"
    assert response_data["annotation_review_id"] > 0

@pytest.mark.order(202)
def test_get_terminal_recording_with_reviews(base_url, access_token):
    """Test getting all annotation reviews for a recording."""
    db: Session = next(get_db())
    recording = db.query(TerminalRecording).filter_by(revision_number=2).order_by(TerminalRecording.id.desc()).first()
    assert recording is not None, "No recording found"

    headers = get_auth_headers(access_token)
    url = f"{base_url}/recordings/terminal/read/{recording.id}"
    response = requests.get(url, headers=headers)
    response_data = response.json()
    assert response.status_code == 200

    assert "annotations" in response_data
    found_annotation_with_reviews = False
    for annotation in response_data["annotations"]:
        if annotation["reviews_count"] > 0:
            found_annotation_with_reviews = True
            break
    assert found_annotation_with_reviews, "No annotations with reviews found"

    assert "annotation_reviews" in response_data
    for review in response_data["annotation_reviews"]:
        assert review["annotation_id"] > 0
        assert review["creator_id"] == 2
        assert review["q_does_anno_match_content"] in [True, False]
        assert review["q_can_anno_be_halved"] in [True, False]
        assert review["q_how_well_anno_matches_content"] in [i for i in range(1, 11)]
        assert review["q_can_you_improve_anno"] in [True, False]
        assert review["q_can_you_provide_markdown"] in [True, False]
