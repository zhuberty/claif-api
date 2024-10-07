import json
import requests
from getpass import getpass

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
