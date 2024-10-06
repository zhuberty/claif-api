import json, logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.annotations import TerminalRecordingAnnotation
from utils._logging import logging
from sqlalchemy.orm import Session


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
    """Extracts annotations from recording content metadata."""
    annotations = []
    if content_metadata.get("librecode_annotations"):
        librecode_annotations = content_metadata["librecode_annotations"]

        if "layers" in librecode_annotations:
            for layer in librecode_annotations["layers"]:
                if "annotations" in layer:
                    for annotation in layer["annotations"]:
                        # Extract individual annotation data
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
    """Extracts annotation data."""
    annotation_data = {
        "text": annotation.get("text"),
        "beginning": annotation.get("beginning"),
        "end": annotation.get("end"),
    }
    return annotation_data


def create_annotation(db: Session, annotation_data: Dict[str, Any], recording_id: int, revision_number: int):
    """Create an annotation."""
    annotation = TerminalRecordingAnnotation(
        recording_id=recording_id,
        revision_number=revision_number,
        annotation_text=annotation_data.get("text"),
        start_time_milliseconds=annotation_data.get("beginning"),
        end_time_milliseconds=annotation_data.get("end"),
    )
    db.add(annotation)
