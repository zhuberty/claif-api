import json
from utils.logging import logging

def parse_asciinema_recording(file_path):
    logging.debug(f"Parsing Asciinema recording from file: {file_path}")
    
    # Read the first line (metadata header)
    first_line = read_first_line(file_path)
    if first_line is None:
        return None, None, None
    
    # Parse the header JSON
    content_metadata = parse_header_json(first_line, file_path)
    if content_metadata is None:
        return None, None, None
    
    # Parse the body of the recording
    content_body = parse_content_body(file_path)
    
    # Since there are no annotations in the provided data, we'll return an empty list for annotations
    annotations = []
    
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

def parse_header_json(first_line, file_path):
    """Parses the first line as JSON and extracts metadata."""
    logging.debug(f"Parsing header JSON from the first line of {file_path}")
    try:
        data = json.loads(first_line)
        content_metadata = {
            "version": data.get("version"),
            "width": data.get("width"),
            "height": data.get("height"),
            "timestamp": data.get("timestamp"),
            "idle_time_limit": data.get("idle_time_limit"),
            "env": data.get("env")
        }
        return content_metadata
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from the first line of {file_path}: {e}")
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


def extract_annotations(header_json):
    # {"version":2,"width":120,"height":30,"timestamp":1727468683,"idle_time_limit":2,"env":{"SHELL":"/bin/bash","TERM":"xterm-256color"},"librecode_annotations":{"note":"librecode annotations","version":1,"layers":[{"annotations":[{"group":"1089445984-2918024939-889183283-2104567988","beginning":30600,"end":39200,"text":"User is writing a Python function header."},{"group":"2659511747-2705856985-636869548-2241453423","beginning":0,"end":1000,"text":"blank terminal"},{"group":"4088595733-3037695177-396385201-1502328558","beginning":40200,"end":49200,"text":"User is writing a Python function body."},{"group":"589252183-3178315870-3360112910-966824157","beginning":53600,"end":53800,"text":"exit bash prompt"}]},{"annotations":[{"group":"1612000329-4220584520-1731625148-3222517124","beginning":30600,"end":49200,"text":"User is writing a Python function."}]},{"annotations":[{"group":"106054957-1981513984-3551564-3400823607","beginning":1200,"end":24000,"text":"bash prompt"},{"group":"4193107425-2224200481-3616209211-485215623","beginning":51800,"end":53600,"text":"bash prompt"},{"group":"681464911-1596533976-4202961837-3510279323","beginning":24200,"end":51600,"text":"vi text editor"},{"group":"834657899-1053451049-3991566020-3057541873","beginning":29200,"end":50800,"text":"vi insert mode"}]}]}}
    annotations = []
    if "librecode_annotations" in header_json:
        librecode_annotations = header_json["librecode_annotations"]
        if "layers" in librecode_annotations:
            for layer in librecode_annotations["layers"]:
                if "annotations" in layer:
                    for annotation in layer["annotations"]:
                        annotations.append(annotation)
                else:
                    logging.debug("No librecode annotations found in layer.")
        else:
            logging.debug("No librecode layers found in header.")
    else:
        logging.debug("No librecode annotations found in header.")

    return annotations