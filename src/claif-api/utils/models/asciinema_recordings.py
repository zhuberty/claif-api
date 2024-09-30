import json
from utils._logging import logging


def parse_asciinema_recording(file_path):
    logging.debug(f"Parsing Asciinema recording from file: {file_path}")
    
    # Read the first line (metadata header)
    first_line = read_first_line(file_path)
    if first_line is None:
        return None, None, None
    
    # Parse the header JSON
    content_metadata = parse_header_json(first_line)
    if content_metadata is None:
        return None, None, None
    
    # Parse the body of the recording
    content_body = parse_content_body(file_path)
    
    # Extract annotations (including nested annotations if any)
    annotations = extract_annotations(content_metadata)
    
    return content_metadata, content_body, annotations


def read_first_line(file_path):
    """Reads and returns the first line of the file."""
    logging.debug(f"Reading the first line of {file_path}")
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
        return first_line
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None


def parse_header_json(first_line):
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


def parse_content_body(file_path):
    """Reads and parses the body of the recording (terminal events)."""
    logging.debug(f"Parsing content body of Asciinema recording from file: {file_path}")
    content_body = []
    try:
        with open(file_path, 'r') as file:
            next(file)  # Skip the first line
            for line in file:
                line = line.strip()
                if line:
                    try:
                        event = json.loads(line)
                        content_body.append(event)
                    except json.JSONDecodeError:
                        logging.error(f"Failed to decode line of {file_path}: {line}")
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
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
