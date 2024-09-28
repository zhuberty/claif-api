from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from keycloak import KeycloakOpenID
from fastapi import APIRouter
from utils.env import KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM, KEYCLOAK_SERVER_URL


router = APIRouter()


@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
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
    return token