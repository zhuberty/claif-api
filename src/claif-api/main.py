import time
from sqlalchemy import text
from keycloak import KeycloakOpenID, KeycloakGetError
from models.base_models import ORMBase
from models.users import User, UserRead
from models.audio_recordings import AudioFile, AudioTranscription, AudioTranscriptionAnnotation
from models.terminal_recordings import TerminalRecording, TerminalRecordingAnnotation
from models.deletion_requests import DeletionRequest

from routers import users, auth
from utils.fastapi import init_fastapi_app
from utils.database import engine
from utils.env import KEYCLOAK_SERVER_URL, KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM

# Initialize FastAPI app
app = init_fastapi_app()

# Register routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, tags=["auth"])

# Function to check Keycloak realm availability and fetch the public key
def fetch_keycloak_public_key():
    keycloak_openid = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL + "/",
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM
    )

    # Retry logic to wait for the realm to be available
    while True:
        try:
            # Attempt to get the public key from Keycloak
            public_key = keycloak_openid.public_key()
            return "-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----"
        except KeycloakGetError as e:
            if e.response_code == 404:
                print("Keycloak realm does not exist yet. Retrying in 5 seconds...")
                time.sleep(5)  # Wait before retrying
            else:
                raise e


# Create the database tables, create enum, and fetch Keycloak public key at startup
@app.on_event("startup")
def on_startup():
    # Create all tables that inherit from ORMBase (all models)
    print("Creating database tables...")
    ORMBase.metadata.create_all(bind=engine, checkfirst=True)
    print("Database tables created successfully.")

    # Fetch Keycloak public key and store it in the app state
    print("Fetching Keycloak public key...")
    app.state.keycloak_public_key = fetch_keycloak_public_key()
    print("Keycloak public key successfully fetched and stored in app state.")
