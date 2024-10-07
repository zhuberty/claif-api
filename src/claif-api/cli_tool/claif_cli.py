import argparse
import requests
import json
from getpass import getpass
from tabulate import tabulate

# Default base URLs
DEFAULT_URL = "http://localhost:8080/v1"
ALTERNATE_URL = "http://localhost:8000/v1"

# File to store the token
TOKEN_FILE = "access_token.json"


def get_auth_headers():
    token = load_access_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    else:
        print("Access token not found. Please login first using the 'login' command.")
        return {}


def load_access_token():
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data.get("access_token")
    except FileNotFoundError:
        return None


def save_access_token(token):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({"access_token": token}, f)


def login(base_url):
    username = input("Username: ").strip()
    password = getpass("Password: ").strip()  # Use getpass to securely enter the password

    url = f"{base_url}/auth/token"
    payload = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        if access_token:
            save_access_token(access_token)
            print("Login successful! Access token saved.")
            return access_token
        else:
            print("Error: Access token not found in the response.")
            return None
    else:
        print(f"Error logging in: {response.status_code} - {response.text}")
        return None


def handle_unauthorized(base_url):
    print("Access token has expired or is invalid. Please log in again.")
    return login(base_url)


def fetch_recording(base_url, recording_id):
    url = f"{base_url}/recordings/terminal/{recording_id}"
    headers = get_auth_headers()
    if not headers:
        return None

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        new_token = handle_unauthorized(base_url)
        if new_token:
            headers = {"Authorization": f"Bearer {new_token}"}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching recording: {response.status_code} - {response.text}")
        else:
            print("Unable to fetch the recording due to authorization failure.")
    else:
        print(f"Error fetching recording: {response.status_code} - {response.text}")
    return None


def create_annotation_review(base_url, annotation):
    print(f"Annotation text: {annotation['annotation_text']}")

    # Prompt the user for answers
    q_does_anno_match_content = input("Does the annotation match the content? (yes/no): ").strip().lower() == 'yes'
    q_can_anno_be_halved = input("Can the annotation be halved? (yes/no): ").strip().lower() == 'yes'
    q_how_well_anno_matches_content = int(input("How well does the annotation match the content (1-5): ").strip())
    q_can_you_improve_anno = input("Can you improve the annotation? (yes/no): ").strip().lower() == 'yes'
    q_can_you_provide_markdown = input("Can you provide markdown? (yes/no): ").strip().lower() == 'yes'

    payload = {
        "annotation_id": annotation['id'],
        "q_does_anno_match_content": q_does_anno_match_content,
        "q_can_anno_be_halved": q_can_anno_be_halved,
        "q_how_well_anno_matches_content": q_how_well_anno_matches_content,
        "q_can_you_improve_anno": q_can_you_improve_anno,
        "q_can_you_provide_markdown": q_can_you_provide_markdown,
    }

    url = f"{base_url}/annotation_reviews/create"
    headers = get_auth_headers()
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Annotation review created successfully!")
    elif response.status_code == 401:
        new_token = handle_unauthorized(base_url)
        if new_token:
            headers = {"Authorization": f"Bearer {new_token}"}
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print("Annotation review created successfully!")
            else:
                print(f"Error creating annotation review: {response.status_code}")
    else:
        print(f"Error creating annotation review: {response.status_code}")


def display_annotations(annotations):
    table_data = []
    for anno in annotations:
        truncated_text = anno['annotation_text'][:20] + '...' if len(anno['annotation_text']) > 20 else anno['annotation_text']
        row = [anno['id'], truncated_text, anno['reviews_count']]
        table_data.append(row)
    
    headers = ["ID", "Annotation Text", "Review Count"]
    print(tabulate(table_data, headers, tablefmt="grid"))


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

        create_annotation_review(base_url, selected_annotation)

        # Update the local annotations list to reflect the new review count
        selected_annotation['reviews_count'] += 1


def main():
    parser = argparse.ArgumentParser(description="CLI tool for interacting with FastAPI app.")
    parser.add_argument("--base-url", default=DEFAULT_URL, help="Base URL of the FastAPI app")
    parser.add_argument("--use-alt-port", action="store_true", help="Use the alternate port (8000)")

    subparsers = parser.add_subparsers(dest="command")

    login_parser = subparsers.add_parser("login", help="Login and obtain an access token")

    review_parser = subparsers.add_parser("create-review", help="Create an annotation review")
    review_parser.add_argument("annotation_id", type=int, help="ID of the annotation to review")

    recording_parser = subparsers.add_parser("review-recording", help="Review annotations in a terminal recording")
    recording_parser.add_argument("recording_id", type=int, help="ID of the terminal recording to review")

    args = parser.parse_args()

    base_url = ALTERNATE_URL if args.use_alt_port else args.base_url

    if args.command == "login":
        login(base_url)
    elif args.command == "create-review":
        annotation = {"id": args.annotation_id}
        create_annotation_review(base_url, annotation)
    elif args.command == "review-recording":
        review_recording(base_url, args.recording_id)

if __name__ == "__main__":
    main()
