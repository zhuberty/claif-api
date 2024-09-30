from fastapi import HTTPException, status, Request, Depends
from fastapi.security import OAuth2
from jose import JWTError, jwt
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from slowapi import Limiter
from utils._logging import logging
from utils.env import KEYCLOAK_REALM, KEYCLOAK_SERVER_URL


def extract_user_id_from_token(request: Request, public_key: str):
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


# OAuth2 scheme setup
oauth2_scheme = OAuth2(
    flows=OAuthFlowsModel(
        password=OAuthFlowPassword(
            tokenUrl=f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
            scopes={"openid": "OpenID Connect scope"},
        )
    )
)

# Limiter with key function
limiter = Limiter(
    key_func=lambda request: extract_user_id_or_anonymous(request)
)

# Function to extract user ID or return a fallback if token is invalid
def extract_user_id_or_anonymous(request: Request):
    public_key = request.app.state.keycloak_public_key
    try:
        return extract_user_id_from_token(request, public_key)
    except HTTPException:
        # If token is invalid or missing, fallback to 'anonymous' for limiting
        return "anonymous"
