import json
from datetime import datetime, timezone
from models.terminal_recordings import TerminalRecording, TerminalRecordingAnnotation
from utils.database import run_with_db_session
from utils.models.asciinema_recordings import parse_asciinema_recording
from utils.logging import logging


def seed_terminal_recordings(db):
    # Parse the recording file
    file_path = "asciinema_recording_samples/recording_1_revision_1.txt"
    content_metadata, content_body, annotations = parse_asciinema_recording(file_path)
    
    if not content_metadata or not content_body:
        logging.error(f"Failed to parse the Asciinema recording from file: {file_path}")
        return

    # Create a TerminalRecording object
    terminal_recording = TerminalRecording(
        title="Sample Terminal Recording",
        description="Parsed from Asciinema recording",
        size_bytes=len(json.dumps(content_body)),  # Size in bytes
        duration_milliseconds=(content_body[-1][0] * 1000 if content_body else 0),  # Last timestamp (in milliseconds)
        revision_number=1,
        created_at=datetime.now(timezone.utc),
        created_by=1,  # Assuming user 1 already exists
        modified_at=datetime.now(timezone.utc),
        modified_by=1,
        content_metadata=json.dumps(content_metadata),
        content_body=json.dumps(content_body),
        annotations_count=len(annotations)
    )
    
    db.add(terminal_recording)
    db.commit()
    
    # Seed terminal recording annotations (if any)
    for annotation in annotations:
        terminal_annotation = TerminalRecordingAnnotation(
            terminal_recording_id=terminal_recording.id,
            parent_annotation_id=None,  # Assuming no parent annotation for now
            annotation_text=annotation["text"],
            start_time_milliseconds=annotation["beginning"],
            end_time_milliseconds=annotation["end"],
            created_at=datetime.now(timezone.utc),
            created_by=1,
            modified_at=datetime.now(timezone.utc),
            modified_by=1,
            children_count=0
        )
        db.add(terminal_annotation)
    
    db.commit()

if __name__ == "__main__":
    run_with_db_session(seed_terminal_recordings)
