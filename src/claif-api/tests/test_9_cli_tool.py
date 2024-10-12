import sys
import os
import pytest
from urllib3.exceptions import NameResolutionError, MaxRetryError
from requests.exceptions import RequestException
from pathlib import Path

from models.recordings import TerminalRecording
from utils.env import TEST_USER_USERNAME, TEST_USER_PASSWORD
from utils.database import get_db
from utils.cli_test_helpers import load_cli_module, set_input_prompts, capture_output, patch_sys_argv
from conftest import logger


@pytest.fixture
def setup_cli(monkeypatch):
    """
    Fixture to set up the project directory and load the CLI module.
    """
    project_dir = Path(__file__).parent.parent / "claif_cli"
    os.chdir(project_dir)
    sys.path.insert(0, str(project_dir))

    # Load CLI main module
    main_module = load_cli_module(project_dir)

    yield main_module, project_dir


@pytest.mark.order(900)
def test_cli_login(monkeypatch, setup_cli):
    # Unpack the fixture
    main_module, project_dir = setup_cli

    # Set up input prompts for the login
    set_input_prompts(monkeypatch, [TEST_USER_USERNAME])
    
    # Patch sys.argv for the command-line arguments, including the password
    patch_sys_argv(monkeypatch, ["login", "--password", TEST_USER_PASSWORD])
    
    # Capture output
    captured_output = capture_output(monkeypatch)
    
    access_token_path = project_dir / "access_token.json"

    # Check if access_token.json exists and delete it
    if os.path.exists(access_token_path):
        logger.info("Removing existing access token file")
        os.remove(access_token_path)

    # Call the main function from the dynamically loaded module
    main_module.main()

    # Assert output
    assert "Login successful! Access token saved.\n" in captured_output.getvalue()
    assert os.path.exists(access_token_path)


@pytest.mark.order(901)
def test_cli_review_terminal_recording(monkeypatch, setup_cli):
    # Unpack the fixture
    main_module, _ = setup_cli

    # Get the most recent recording with a revision greater than 1
    db: pytest.Session = next(get_db())
    recording = db.query(TerminalRecording).filter(TerminalRecording.revision_number > 1).order_by(TerminalRecording.id.desc()).first()

    # get the recording's first annotation ID
    annotation_id = recording.annotations.filter_by(revision_number=recording.revision_number).first().id

    # Set up input prompts for the review-recording command
    inputs = [str(annotation_id), "yes", "yes", "5", "yes", "yes", "0"]
    set_input_prompts(monkeypatch, inputs)

    # Pass in args: review-recording, record_id, revision_number
    patch_sys_argv(monkeypatch, ["review-recording", str(recording.id), f"--revision-number={recording.revision_number}"])

    # Capture stdout
    captured_output = capture_output(monkeypatch)

    # Call the CLI Tool's main function
    main_module.main()

    captured_output_value = captured_output.getvalue()
    assert "Error" not in captured_output.getvalue()
    assert "Annotations for Recording ID" in captured_output_value
    assert "Annotation review created" in captured_output_value


@pytest.mark.order(902)
def test_cli_create_terminal_recording(monkeypatch, setup_cli):
    # Unpack the fixture
    main_module, _ = setup_cli

    asciinema_recordings_dir = Path(__file__).parent.parent / "asciinema_recording_samples"
    recording_filepath = asciinema_recordings_dir / "recording_1_revision_1.txt"

    # Pass in args: create-recording, recording_filepath, title, description
    patch_sys_argv(monkeypatch, [
        "create-recording", str(recording_filepath),
        "CLI Test Recording", "CLI Test Description"
    ])

    # Capture stdout
    captured_output = capture_output(monkeypatch)

    # Call the CLI Tool's main function
    main_module.main()

    captured_output_value = captured_output.getvalue()
    assert "Error" not in captured_output_value
    assert "Recording created" in captured_output_value


@pytest.mark.order(903)
def test_cli_update_terminal_recording(monkeypatch, setup_cli):
    # Unpack the fixture
    main_module, _ = setup_cli

    # Get the most recent recording with a revision greater than 1
    db: pytest.Session = next(get_db())
    recording = db.query(TerminalRecording).filter(TerminalRecording.revision_number > 1).order_by(TerminalRecording.id.desc()).first()

    # Pass in args
    recording_filepath = Path(__file__).parent.parent / "asciinema_recording_samples" / "recording_1_revision_2.txt"
    patch_sys_argv(monkeypatch, [
        "update-recording", str(recording.id), f"--recording_filepath={recording_filepath}",
        "--title=CLI Test Recording Updated", "--description=CLI Test Description Updated"
    ])

    # Capture stdout
    captured_output = capture_output(monkeypatch)

    # Call the CLI Tool's main function
    main_module.main()

    captured_output_value = captured_output.getvalue()
    assert "Error" not in captured_output_value
    assert "Recording updated" in captured_output_value


@pytest.mark.order(904)
def test_cli_list_recordings(monkeypatch, setup_cli):
    # Unpack the fixture
    main_module, _ = setup_cli

    # Pass in args
    patch_sys_argv(monkeypatch, ["list-recordings"])

    # Capture stdout
    captured_output = capture_output(monkeypatch)

    # Call the CLI Tool's main function
    main_module.main()

    captured_output_value = captured_output.getvalue()
    assert "Error" not in captured_output_value
    assert "CLI Test Recording Updated" in captured_output_value


@pytest.mark.order(905)
def test_cli_host_flags(monkeypatch, setup_cli):
    # Unpack the fixture
    main_module, _ = setup_cli

    # Pass in args
    patch_sys_argv(monkeypatch, ["--base-url=http://incorrect-localhost:8000/v1", "list-recordings"])

    # Call the CLI Tool's main function
    raised_expected_errors = False
    try:
        main_module.main()
    except RequestException as e:
        # Check if the exception is wrapping a MaxRetryError
        if e.args and isinstance(e.args[0], MaxRetryError):
            max_retry_error = e.args[0]
            logger.info(f"As intended, MaxRetryError occurred.")
            
            # Further check if it is caused by a NameResolutionError
            if max_retry_error.reason and isinstance(max_retry_error.reason, NameResolutionError):
                logger.info(f"As intended, NameResolutionError occurred")
                raised_expected_errors = True
        else:
            # Handle other RequestException errors
            pytest.fail(f"An unintended requests-related error occurred: {e}")

    assert raised_expected_errors


@pytest.mark.order(906)
def test_cli_create_audio_file(monkeypatch, setup_cli):
    # Unpack the fixture
    main_module, _ = setup_cli

    # Pass in args
    audio_filepath = Path(__file__).parent.parent / "audio_recording_samples" / "frankenstein_passage_two_speakers_medium_quality.m4a"
    patch_sys_argv(monkeypatch, ["create-audio-file", str(audio_filepath)])

    # Capture stdout
    captured_output = capture_output(monkeypatch)

    # Call the CLI Tool's main function
    main_module.main()

    captured_output_value = captured_output.getvalue()
    assert "Error" not in captured_output_value
    assert "File uploaded and metadata stored successfully" in captured_output_value
