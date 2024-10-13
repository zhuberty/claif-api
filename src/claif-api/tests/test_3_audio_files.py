from pathlib import Path
import pytest
import requests
from utils.config import get_auth_headers

@pytest.mark.order(300)
def test_create_audio_file(base_url, access_token):
    """Test creating a new audio recording by uploading a file."""
    
    # Path to the audio file
    samples_path = Path(__file__).parent.parent / "audio_recording_samples"
    audio_filepath = samples_path / "frankenstein_passage_two_speakers_medium_quality.wav"
    assert audio_filepath.exists(), f"File not found: {audio_filepath}"

    # Prepare the file upload and other metadata
    files = {
        "file": open(audio_filepath, "rb"),  # Open the file in binary mode
    }

    # Get authorization headers
    headers = get_auth_headers(access_token)

    # URL for the audio file creation endpoint
    url = f"{base_url}/recordings/audio_files/create"

    # Make the request to upload the file
    response = requests.post(url, files=files, headers=headers)

    # Ensure the response is successful
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    # Parse the response JSON data
    response_data = response.json()

    # Check if the response contains the correct message and metadata
    assert response_data["message"] == "File uploaded and metadata stored successfully."
    assert "file_metadata" in response_data
    assert response_data["file_metadata"]["id"] > 0
    assert "storage_path" in response_data["file_metadata"]
    assert response_data["file_metadata"]["storage_path"].startswith("audio/")

    # Close the file after upload
    files["file"].close()
