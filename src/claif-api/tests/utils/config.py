from utils.env import CLAIF_API_HOST, CLAIF_API_PORT

def get_base_url():
    """Construct the base API URL from environment variables."""
    return f"http://{CLAIF_API_HOST}:{CLAIF_API_PORT}/v1"


def get_auth_headers(access_token):
    """Construct the Authorization header for authenticated requests."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
