import requests, logging
import pytest
from utils.config import get_auth_headers


@pytest.mark.order(1)
def test_get_users(base_url, access_token):
    """Test retrieving multiple user objects."""
    users_to_test = [
        {"id": 1, "expected_username": "admin"},
        {"id": 2, "expected_username": "user1"},
        {"id": 3, "expected_username": "user2"}
    ]
    
    headers = get_auth_headers(access_token)
    
    for user in users_to_test:
        url = f"{base_url}/users/{user['id']}"
        response = requests.get(url, headers=headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['username'] == user["expected_username"]
