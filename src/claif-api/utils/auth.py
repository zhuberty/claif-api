import time
import logging

from fastapi import HTTPException, status, Request, Depends
from jose import JWTError, jwt
from keycloak import KeycloakGetError, KeycloakOpenID
from sqlalchemy.orm import Session
from slowapi import Limiter
from utils.database import get_db
from utils.env import KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM, KEYCLOAK_SERVER_URL
from models.users import User


def fetch_keycloak_public_key():
    keycloak_openid = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL + "/",
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM
    )
    while True:
        try:
            public_key = keycloak_openid.public_key()
            return "-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----"
        except KeycloakGetError as e:
            if e.response_code == 404:
                logging.info("Keycloak realm does not exist yet. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise e


def get_token_from_request(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logging.error("Token missing or invalid")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing or invalid")
    return auth_header.split(" ")[1]


def decode_token(token: str, public_key: str):
    try:
        return jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="account",
            options={"verify_aud": True, "verify_exp": True},
        )
    except JWTError as e:
        logging.error("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e


def extract_keycloak_id_from_token(token: str, public_key: str=None):
    if not public_key:
        public_key = fetch_keycloak_public_key()
    payload = decode_token(token, public_key)
    return payload.get("sub")


def extract_user_id_or_raise(request: Request):
    public_key = request.app.state.keycloak_public_key
    token = get_token_from_request(request)
    user_id = extract_keycloak_id_from_token(token, public_key)
    if not user_id:
        logging.error("Unauthorized access attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Anonymous actions are not allowed."
        )
    return user_id


def get_user_from_keycloak_id(db: Session, keycloak_id: str):
    user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)):
    public_key = request.app.state.keycloak_public_key
    token = get_token_from_request(request)
    keycloak_id = extract_keycloak_id_from_token(token, public_key)
    return get_user_from_keycloak_id(db, keycloak_id)


limiter = Limiter(
    key_func=lambda request: extract_user_id_or_raise(request)
)
