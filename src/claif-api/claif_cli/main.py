import argparse
from auth_utils import login
from annotation_reviews import create_annotation_review
from recordings import review_recording

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

    # Other subparsers and arguments
    args = parser.parse_args()

    base_url = ALTERNATE_URL if args.use_alt_port else args.base_url

    if args.command == "login":
        login(base_url, password=args.password)
    elif args.command == "create-review":
        annotation = {"id": args.annotation_id}
        create_annotation_review(base_url, annotation)
    elif args.command == "review-recording":
        review_recording(base_url, args.recording_id)

if __name__ == "__main__":
    main()
