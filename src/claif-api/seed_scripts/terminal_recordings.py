import json
from datetime import datetime, timezone
from models.terminal_recordings import TerminalRecording, TerminalRecordingAnnotation
from utils.database import run_with_db_session
from utils.models.terminal_recordings import parse_asciinema_recording
from utils._logging import logging
from utils.files import read_file


def seed_terminal_recordings(
    db, 
    file_path, 
    title, 
    description, 
    revision_number=1, 
    creator_id=1, 
    source_revision_id=None, 
    previous_revision_id=None, 
    locked_for_review=False
):
    # Parse the recording file
    recording_content = read_file(file_path)
    content_metadata, content_body, annotations = parse_asciinema_recording(recording_content)
    
    if not content_metadata or not content_body:
        logging.error(f"Failed to parse the Asciinema recording from file: {file_path}")
        return

    # Create a TerminalRecording object
    terminal_recording = TerminalRecording(
        title=title,
        description=description,
        size_bytes=len(json.dumps(content_body)),
        duration_milliseconds=(content_body[-1][0] * 1000 if content_body else 0),  # Last timestamp (in milliseconds)
        revision_number=revision_number,
        created_at=datetime.now(timezone.utc),
        creator_id=creator_id,
        content_metadata=json.dumps(content_metadata),
        content_body=json.dumps(content_body),
        annotations_count=len(annotations),
        source_revision_id=source_revision_id,
        previous_revision_id=previous_revision_id,
        locked_for_review=locked_for_review,
    )
    
    db.add(terminal_recording)
    db.commit()

    # Function to recursively seed child annotations
    def seed_annotation(annotation_data, parent_annotation_id=None):
        terminal_annotation = TerminalRecordingAnnotation(
            recording_id=terminal_recording.id,
            parent_annotation_id=parent_annotation_id,
            annotation_text=annotation_data.get("text"),
            start_time_milliseconds=annotation_data.get("beginning"),
            end_time_milliseconds=annotation_data.get("end"),
            children_count=len(annotation_data.get("children", []))
        )
        db.add(terminal_annotation)
        db.commit()

        # Recursively seed child annotations, if any
        for child in annotation_data.get("children", []):
            seed_annotation(child, terminal_annotation.id)

    # Seed annotations, including any nested child annotations
    for annotation in annotations:
        seed_annotation(annotation)

    db.commit()


if __name__ == "__main__":
    recordings_dir = "asciinema_recording_samples"
    recording_1_title = "Writing a small hello-world Python function"
    recording_1_description = "The user writes a small Python function that prints 'Hello, Annotations!'"

    # Seed first revision
    run_with_db_session(
        seed_terminal_recordings, 
        f"{recordings_dir}/recording_1_revision_1.txt",
        recording_1_title,
        recording_1_description,
    )

    # Seed second revision
    run_with_db_session(
        seed_terminal_recordings, 
        f"{recordings_dir}/recording_1_revision_2.txt",
        recording_1_title,
        recording_1_description,
        revision_number=2,
        creator_id=1,
        source_revision_id=1,
        previous_revision_id=1,
        locked_for_review=True,
    )
