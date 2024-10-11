import os
from utils.env import CLAIF_API_HOST, CLAIF_API_PORT


def get_base_url():
    """Construct the base API URL from environment variables."""
    host = os.environ.get("CLAIF_API_HOST", "localhost")
    port = os.environ.get("CLAIF_API_PORT", "8000")

    # Add protocol only if it doesn't already exist
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"

    return f"{host}:{port}/v1"


def get_auth_headers(access_token):
    """Construct the Authorization header for authenticated requests."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
