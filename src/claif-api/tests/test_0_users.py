import pytest
from sqlalchemy.orm.session import Session
from models.users import User
from utils.auth import extract_keycloak_id_from_token
from utils.database import get_db

@pytest.mark.order(1)
def test_set_user_keycloak_id(access_token):
    """Test setting the Keycloak ID for the test user."""
    db: Session = next(get_db())
    user = db.query(User).filter_by(username="user1").first()
    assert user is not None, "User not found"
    user.keycloak_id = extract_keycloak_id_from_token(access_token)
    db.commit()
    db.refresh(user)
    assert len(user.keycloak_id) == 36, "Invalid Keycloak ID length"
