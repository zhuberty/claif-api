import time
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import OAuth2
from jose import JWTError, jwt
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from keycloak import KeycloakGetError, KeycloakOpenID
from sqlalchemy.orm import Session
from slowapi import Limiter
from utils._logging import logging
from utils.database import get_db
from utils.env import KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM, KEYCLOAK_SERVER_URL
from models.users import User


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
                logging.info("Keycloak realm does not exist yet. Retrying in 5 seconds...")
                time.sleep(5)  # Wait before retrying
            else:
                raise e


# Function to extract user ID or raise an exception if unauthenticated
def extract_user_id_or_raise(request: Request):
    public_key = request.app.state.keycloak_public_key
    try:
        return extract_keycloak_id_from_request(request, public_key)
    except HTTPException as e:
        # Log the error and raise an exception, blocking unauthenticated users
        logging.error("Unauthorized access attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Anonymous actions are not allowed."
        ) from e


def extract_keycloak_id_from_request(request: Request, public_key: str):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        logging.error("Token missing or invalid")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing or invalid")
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(
            token,
            public_key,  # Use the public key passed as an argument
            algorithms=["RS256"],
            audience="account",
            options={"verify_aud": True, "verify_exp": True},
        )
        user_id = payload.get("sub")
        logging.info(f"Extracted Keycloak User ID: {user_id}")
        return user_id
    except JWTError as e:
        logging.error("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e


def extract_keycloak_id_from_token(token):
    try:
        payload = jwt.decode(
            token,
            fetch_keycloak_public_key(),
            algorithms=["RS256"],
            audience="account",
            options={"verify_aud": True, "verify_exp": True},
        )
        user_id = payload.get("sub")
        logging.info(f"Extracted Keycloak User ID: {user_id}")
        return user_id
    except JWTError as e:
        logging.error("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e


# Function to extract user object based on keycloak_id
def get_current_user(request: Request, db: Session = Depends(get_db)):
    public_key = request.app.state.keycloak_public_key
    try:
        # Extract the keycloak ID from the token
        keycloak_id = extract_keycloak_id_from_request(request, public_key)
        
        # Fetch the user from the database based on the keycloak_id
        user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        return user
    except HTTPException as e:
        # Log the error and raise an exception for unauthenticated or unauthorized users
        logging.error("Unauthorized access attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Anonymous actions are not allowed."
        ) from e



def get_user_from_keycloak_id(db, keycloak_id):
    db: Session = get_db()
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Limiter with key function that ensures only authenticated users can access
limiter = Limiter(
    key_func=lambda request: extract_user_id_or_raise(request)
)
