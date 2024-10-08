from display_utils import display_annotations
from api_requests import api_request


def list_recordings(base_url):
    return api_request(base_url, "/recordings/terminal/list")


def fetch_recording(base_url, recording_id):
    return api_request(base_url, f"/recordings/terminal/read/{recording_id}")


def create_review(base_url, annotation_data):
    return api_request(base_url, "/annotations/review", method="POST", json=annotation_data)


def delete_recording(base_url, recording_id):
    return api_request(base_url, f"/recordings/terminal/delete/{recording_id}", method="DELETE")


def review_recording(base_url, recording_id):
    recording = fetch_recording(base_url, recording_id)
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

        selected_annotation = next((anno for anno in annotations if anno['id'] == annotation_id), None)
        if not selected_annotation:
            print("Invalid annotation ID. Please select a valid one from the table.")
            continue

        create_review(base_url, selected_annotation)

        # Update the local annotations list to reflect the new review count
        selected_annotation['reviews_count'] += 1
