from routers import users, auth
from routers.terminal_recordings import terminal_recordings
from models.base_models import ORMBase
from utils.fastapi import init_fastapi_app
from utils.database import engine
from utils._logging import logging
from utils.auth import fetch_keycloak_public_key


# Initialize FastAPI app
app = init_fastapi_app()

# Register routers
app.include_router(users.router, prefix="/v1/users", tags=["users"])
app.include_router(terminal_recordings.router, prefix="/v1/recordings/terminal", tags=["terminal_recordings"])
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])


# Create the database tables, create enum, and fetch Keycloak public key at startup
@app.on_event("startup")
def on_startup():
    # Create all tables that inherit from ORMBase (all models)
    logging.info("Creating database tables...")
    ORMBase.metadata.create_all(bind=engine, checkfirst=True)
    logging.info("Database tables created successfully.")

    # Fetch Keycloak public key and store it in the app state
    logging.info("Fetching Keycloak public key...")
    app.state.keycloak_public_key = fetch_keycloak_public_key()
    logging.info("Keycloak public key successfully fetched and stored in app state.")
