from display_utils import display_annotations
from annotation_reviews import create_review
from api_requests import api_request


def list_recordings(base_url):
    return api_request(base_url, "/recordings/terminal/list")


def fetch_recording(base_url, recording_id, revision_number):
    params = {"revision_number": revision_number}
    return api_request(base_url, f"/recordings/terminal/read/{recording_id}")


def delete_recording(base_url, recording_id):
    return api_request(base_url, f"/recordings/terminal/delete/{recording_id}", method="DELETE")


def review_recording(base_url, recording_id, revision_number):
    recording = fetch_recording(base_url, recording_id, revision_number)
    if not recording:
        return

    annotations = recording.get('annotations', [])
    while True:
        print("\nAnnotations for Recording ID:", recording_id)
        display_annotations(annotations)

        try:
            annotation_id = int(input("Enter the ID of the annotation you want to review (or 0 to exit): ").strip())
        except ValueError:
            print("Invalid input. Please enter a valid ID.")
            continue

        if annotation_id == 0:
            print("Exiting...")
            break

        selected_annotation = None
        for annotation in annotations:
            if annotation['id'] == annotation_id:
                selected_annotation = annotation
                break
        if not selected_annotation:
            print("Invalid annotation ID. Please select a valid one from the table.")
            continue

        response = create_review(base_url, selected_annotation)

        if "message" in response:
            print(response["message"])
        else:
            print("An error occurred while creating the review.")

        # Update the local annotations list to reflect the new review count
        selected_annotation['reviews_count'] += 1


def create_recording(base_url, recording_filepath, title, description):
    with open(recording_filepath, 'r') as file:
        recording_content = file.read()

    payload = {
        "title": title,
        "description": description,
        "recording_content": recording_content,
    }
    response = api_request(base_url, "/recordings/terminal/create", method="POST", json=payload)
    if "message" in response:
        print(response["message"])