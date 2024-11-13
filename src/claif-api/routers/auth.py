from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from keycloak import KeycloakOpenID
from fastapi import APIRouter
from utils.env import KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM, KEYCLOAK_SERVER_URL
from models.users import User
from sqlalchemy.orm import Session
from utils.database import get_db
from utils.auth import extract_keycloak_id_from_token


router = APIRouter()


@router.post("/token")
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    ):
    keycloak_openid = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL + "/",
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM,
    )
    token = keycloak_openid.token(
        username=form_data.username,
        password=form_data.password,
        grant_type="password",
    )

    if "access_token" in token:
        # if user does not exist, add user to database
        keycloak_id = extract_keycloak_id_from_token(token["access_token"])
        user = db.query(User).filter(User.keycloak_id == keycloak_id).first()
        if not user:
            db.add(User(keycloak_id=keycloak_id, username=form_data.username))
            db.commit()
            db.close()

    return token