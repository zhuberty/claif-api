import requests
from auth_utils import get_auth_headers, handle_unauthorized


def api_request(base_url, endpoint, method="GET", data=None, json=None, params=None):
    """
    Makes an HTTP request to the API endpoint with authorization and retry logic.
    
    Parameters:
        - base_url (str): The base URL of the API.
        - endpoint (str): The API endpoint to call.
        - method (str): The HTTP method (GET, POST, DELETE).
        - data (dict, optional): Form data to send with the request (for POST).
        - json (dict, optional): JSON data to send with the request (for POST).
        - params (dict, optional): URL parameters to send with the request.
        
    Returns:
        - The response JSON if the request is successful, otherwise None.
    """
    url = f"{base_url}{endpoint}"
    headers = get_auth_headers()
    if not headers:
        return None

    response = requests.request(method, url, headers=headers, data=data, json=json, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        new_token = handle_unauthorized(base_url)
        if new_token:
            headers = {"Authorization": f"Bearer {new_token}"}
            response = requests.request(method, url, headers=headers, data=data, json=json, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error performing {method} request: {response.status_code} - {response.text}")
    else:
        print(f"Error performing {method} request: {response.status_code} - {response.text}")
    return None