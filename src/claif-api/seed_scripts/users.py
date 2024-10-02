from utils.database import run_with_db_session
from models.users import User
from datetime import datetime, timezone
from models.users import User


def seed_users(db):
    users = [
        User(
            keycloak_id="kc-12345",
            username="admin",
            created_at=datetime.now(timezone.utc),
            creator_id=None,
        ),
        User(
            keycloak_id="kc-67890",
            username="user1",
            created_at=datetime.now(timezone.utc),
            creator_id=None,
        ),
        User(
            keycloak_id="kc-24680",
            username="user2",
            created_at=datetime.now(timezone.utc),
            creator_id=None,
        )
    ]
    
    db.bulk_save_objects(users)
    db.commit()

if __name__ == "__main__":
    run_with_db_session(seed_users)
