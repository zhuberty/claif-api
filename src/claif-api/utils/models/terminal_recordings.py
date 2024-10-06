from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session
from models.recordings import TerminalRecording
from models.annotations import TerminalRecordingAnnotation
from utils._logging import logging

def parse_asciinema_recording(recording_content: str):
    """Parses the Asciinema recording from the passed content string."""
    logging.debug(f"Parsing Asciinema recording from content")

    # Split the content into lines
    lines = recording_content.splitlines()

    if not lines:
        return None, None, None

    # Read the first line (metadata header)
    first_line = lines[0]
    content_metadata = parse_header_json(first_line)
    if content_metadata is None:
        return None, None, None

    # Parse the body of the recording
    content_body = parse_content_body(lines[1:])

    # Extract annotations (including nested annotations if any)
    annotations = extract_annotations(content_metadata)

    return content_metadata, content_body, annotations


def parse_header_json(first_line: str):
    """Parses the first line as JSON and extracts metadata."""
    logging.debug(f"Parsing header JSON from the first line.")
    try:
        data = json.loads(first_line)
        content_metadata = {
            "version": data.get("version"),
            "width": data.get("width"),
            "height": data.get("height"),
            "timestamp": data.get("timestamp"),
            "idle_time_limit": data.get("idle_time_limit"),
            "env": data.get("env"),
            "librecode_annotations": data.get("librecode_annotations")
        }
        return content_metadata
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from the first line: {e}")
        return None


def parse_content_body(lines: list):
    """Reads and parses the body of the recording (terminal events) from the content."""
    logging.debug(f"Parsing content body of Asciinema recording.")
    content_body = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                event = json.loads(line)
                content_body.append(event)
            except json.JSONDecodeError:
                logging.error(f"Failed to decode line: {line}")
    return content_body


def extract_annotations(content_metadata: dict):
    """Extracts annotations and handles nested child annotations."""
    annotations = []
    if content_metadata.get("librecode_annotations"):
        librecode_annotations = content_metadata["librecode_annotations"]

        if "layers" in librecode_annotations:
            for layer in librecode_annotations["layers"]:
                if "annotations" in layer:
                    for annotation in layer["annotations"]:
                        # Extract individual annotation and any nested children
                        extracted_annotation = extract_annotation_data(annotation)
                        annotations.append(extracted_annotation)
                else:
                    logging.debug("No annotations found in layer.")
        else:
            logging.debug("No layers found in librecode annotations.")
    else:
        logging.debug("No librecode annotations found in header.")

    return annotations


def extract_annotation_data(annotation):
    """Extracts annotation data recursively, including nested child annotations."""
    annotation_data = {
        "text": annotation.get("text"),
        "beginning": annotation.get("beginning"),
        "end": annotation.get("end"),
        "children": []
    }

    # Recursively extract child annotations if present
    if "children" in annotation:
        for child_annotation in annotation["children"]:
            child_data = extract_annotation_data(child_annotation)
            annotation_data["children"].append(child_data)

    return annotation_data


from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
import logging

def parse_and_validate_content(recording_content: str) -> Dict[str, Any]:
    """Parse recording content and validate the metadata and body."""
    content_metadata, content_body, annotations = parse_asciinema_recording(recording_content)
    
    if not content_metadata or not content_body:
        logging.error("Failed to parse the Asciinema recording from content.")
        raise ValueError("Failed to parse the Asciinema recording.")
    
    return {
        "metadata": content_metadata,
        "body": content_body,
        "annotations": annotations
    }


def create_terminal_recording_object(
    title: str, description: str, content: Dict[str, Any], revision_number: int, creator_id: int, 
    source_revision_id: int, previous_revision_id: int, locked_for_review: bool
) -> TerminalRecording:
    """Create a TerminalRecording object from parsed content."""
    size_bytes = len(json.dumps(content["metadata"])) + len(json.dumps(content["body"]))
    duration_milliseconds = content["body"][-1][0] * 1000 if content["body"] else 0

    return TerminalRecording(
        title=title,
        description=description,
        size_bytes=size_bytes,
        duration_milliseconds=duration_milliseconds,
        revision_number=revision_number,
        created_at=datetime.now(timezone.utc),
        creator_id=creator_id,
        content_metadata=json.dumps(content["metadata"]),
        content_body=json.dumps(content["body"]),
        annotations_count=len(content["annotations"]),
        source_revision_id=source_revision_id,
        previous_revision_id=previous_revision_id,
        locked_for_review=locked_for_review,
    )


def save_terminal_recording(db: Session, terminal_recording: TerminalRecording):
    """Save and refresh a TerminalRecording object in the database."""
    db.add(terminal_recording)
    db.commit()
    db.refresh(terminal_recording)


def create_annotation(db: Session, annotation_data: Dict[str, Any], recording_id: int, parent_annotation_id: int = None):
    """Create an annotation and recursively add child annotations."""
    annotation = TerminalRecordingAnnotation(
        recording_id=recording_id,
        parent_annotation_id=parent_annotation_id,
        annotation_text=annotation_data.get("text"),
        start_time_milliseconds=annotation_data.get("beginning"),
        end_time_milliseconds=annotation_data.get("end"),
        children_count=len(annotation_data.get("children", []))
    )
    
    db.add(annotation)
    db.commit()
    db.refresh(annotation)

    for child in annotation_data.get("children", []):
        create_annotation(db, child, recording_id, annotation.id)


def save_annotations(db: Session, annotations: List[Dict[str, Any]], recording_id: int):
    """Save all annotations for a given recording."""
    for annotation in annotations:
        create_annotation(db, annotation, recording_id)
    db.commit()


def get_and_create_terminal_recording(
    db: Session, title: str, description: str, recording_content: str, 
    revision_number: int = 1, creator_id: int = 1, 
    source_revision_id: int = None, previous_revision_id: int = None, locked_for_review: bool = False
) -> TerminalRecording:
    """Parses the recording content and creates a new TerminalRecording."""
    
    # Parse and validate the recording content
    content = parse_and_validate_content(recording_content)

    # Create the TerminalRecording object
    terminal_recording = create_terminal_recording_object(
        title, description, content, revision_number, creator_id, source_revision_id, previous_revision_id, locked_for_review
    )
    
    # Save the terminal recording
    save_terminal_recording(db, terminal_recording)

    # Create and save annotations
    save_annotations(db, content["annotations"], terminal_recording.id)

    return terminal_recording
