import argparse
from auth_utils import login
from recordings import (
    review_recording,
    create_recording,
    update_recording,
    list_recordings,
)

DEFAULT_URL = "http://localhost:8080/v1"
ALTERNATE_URL = "http://localhost:8000/v1"


def main():
    parser = argparse.ArgumentParser(description="CLI tool for interacting with FastAPI app.")
    parser.add_argument("--base-url", default=DEFAULT_URL, help="Base URL of the FastAPI app")
    parser.add_argument("--use-alt-port", action="store_true", help="Use the alternate port (8000)")
    parser.add_argument("--password", help="Provide password directly for testing purposes")

    subparsers = parser.add_subparsers(dest="command")

    login_parser = subparsers.add_parser("login", help="Login to the FastAPI app")
    login_parser.add_argument("--password", help="Password for testing purposes")

    review_recording_parser = subparsers.add_parser("review-recording", help="Review a recording")
    review_recording_parser.add_argument("recording_id", type=int, help="ID of the recording to review")
    review_recording_parser.add_argument("--revision-number", type=int, help="Revision number of the recording")

    create_recording_parser = subparsers.add_parser("create-recording", help="Create a new recording")
    create_recording_parser.add_argument("recording_filepath", help="Path to the recording file")
    create_recording_parser.add_argument("recording_title", help="Title of the recording")
    create_recording_parser.add_argument("recording_description", help="Description of the recording")

    update_recording_parser = subparsers.add_parser("update-recording", help="Update an existing recording")
    update_recording_parser.add_argument("recording_id", type=int, help="ID of the recording to update")
    update_recording_parser.add_argument("--recording_filepath", help="Path to the updated recording file")
    update_recording_parser.add_argument("--title", help="New title for the recording")
    update_recording_parser.add_argument("--description", help="New description for the recording")

    list_recordings_parser = subparsers.add_parser("list-recordings", help="List all recordings")
    
    args = parser.parse_args()

    base_url = ALTERNATE_URL if args.use_alt_port else args.base_url

    if args.command == "login":
        login(base_url, password=args.password)
    elif args.command == "review-recording":
        review_recording(base_url, args.recording_id, args.revision_number)
    elif args.command == "create-recording":
        create_recording(
            base_url, 
            args.recording_filepath, 
            args.recording_title, 
            args.recording_description
        )
    elif args.command == "update-recording":
        update_recording(
            base_url, 
            args.recording_id, 
            recording_filepath=args.recording_filepath,
            title=args.title, 
            description=args.description
        )
    elif args.command == "list-recordings":
        list_recordings(base_url)


if __name__ == "__main__":
    main()
