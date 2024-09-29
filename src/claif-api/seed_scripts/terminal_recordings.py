import json
from datetime import datetime, timezone
from models.terminal_recordings import TerminalRecording, TerminalRecordingAnnotation
from utils.database import run_with_db_session
from utils.logging import logging

def parse_asciinema_recording(file_path):
    logging.debug(f"Parsing Asciinema recording from file: {file_path}")
    with open(file_path, 'r') as file:
        # Read the first line for metadata
        first_line = file.readline().strip()

    try:
        # Parse the first line as JSON (this is the content header)
        data = json.loads(first_line)
        
        logging.debug(f"Successfully decoded asciinema JSON from the first line of {file_path}.")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from the first line of {file_path}: {e}")
        return None, None, None
    
    # Extract content header metadata
    content_metadata = {
        "version": data.get("version"),
        "width": data.get("width"),
        "height": data.get("height"),
        "timestamp": data.get("timestamp"),
        "idle_time_limit": data.get("idle_time_limit"),
        "env": data.get("env")
    }

    # Now read the rest of the file for terminal events (this is the content body)
    content_body = []
    with open(file_path, 'r') as file:
        # Skip the first line
        next(file)
        for line in file:
            # Remove any surrounding whitespace and check if the line is non-empty
            line = line.strip()
            if line:
                try:
                    # Parse each event line as JSON and add it to the content body
                    event = json.loads(line)
                    content_body.append(event)
                except json.JSONDecodeError:
                    logging.error(f"Failed to decode line of {file_path}: {line}")
                    continue
    
    # Since there are no annotations in the provided data, we'll return an empty list for annotations
    annotations = []
    
    return content_metadata, content_body, annotations

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
