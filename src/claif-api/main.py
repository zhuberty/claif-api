from keycloak import KeycloakOpenID

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

# Create the database tables, checking if they already exist
@app.on_event("startup")
def on_startup():
    # Create all tables that inherit from ORMBase (all models)
    ORMBase.metadata.create_all(bind=engine, checkfirst=True)

    # Fetch Keycloak public key and store it in the app state
    keycloak_openid = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL + "/",
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM
    )
    public_key = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
    app.state.keycloak_public_key = public_key

