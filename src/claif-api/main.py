import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2
from jose import JWTError, jwt
from typing import Optional
from keycloak import KeycloakOpenID
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware

# Initialize logger
logger = logging.getLogger("uvicorn.error")

# Keycloak settings
KEYCLOAK_SERVER_URL = os.environ.get("KEYCLOAK_SERVER_URL", "http://localhost:8085")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "fastapi")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "fastapi-client")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET", "g07L@Qg#mL&u8ukA2XE@L1wi&hioNRAoRGpYy")
KEYCLOAK_PUBLIC_KEY = None  # Will fetch from Keycloak
OPENAPI_KEYCLOAK_SERVER_URL = os.environ.get("OPENAPI_KEYCLOAK_SERVER_URL", "http://localhost:8085")

# Database URL (Using PostgreSQL)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://claif_db_user:claif_db_password@localhost:5433/claif_db"
)

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAlchemy ORM model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)

# Pydantic models for request and response bodies
class UserCreate(BaseModel):
    name: str
    email: str

class UserRead(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True  # Enables ORM model to Pydantic model conversion

# Initialize FastAPI app
app = FastAPI()

# Initialize Limiter with a key function based on Keycloak user ID
limiter = Limiter(key_func=lambda request: extract_user_id_from_token(request))

# Add SlowAPI middleware for rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Custom OpenAPI schema to include the OAuth2 Password Flow in Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="CLAIF API",
        version="0.1.0",
        description="API documentation with Keycloak OAuth2",
        routes=app.routes,
    )

    # Modify to use the correct public client password flow
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": f"{OPENAPI_KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
                    "scopes": {"openid": "OpenID Connect scope"},
                }
            }
        }
    }

    # Apply security to all routes
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Override the FastAPI's default OpenAPI generator
app.openapi = custom_openapi

# Create the database tables, checking if they already exist
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine, checkfirst=True)
    # Fetch Keycloak public key
    global KEYCLOAK_PUBLIC_KEY

    keycloak_openid = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL + "/",
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM,
        client_secret_key=KEYCLOAK_CLIENT_SECRET,
    )
    KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"

oauth2_scheme = OAuth2(
    flows=OAuthFlowsModel(
        password=OAuthFlowPassword(
            tokenUrl=f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
            scopes={"openid": "OpenID Connect scope"},
        )
    )
)

@app.get("/users/{user_id}", response_model=UserRead)
@limiter.limit("20/minute")  # Limit to 20 requests per minute per user
def read_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    # Retrieve user by ID
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Token endpoint for resource owner password credentials grant
@app.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    keycloak_openid = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL + "/",
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM,
        client_secret_key=KEYCLOAK_CLIENT_SECRET,
    )
    token = keycloak_openid.token(
        username=form_data.username,
        password=form_data.password,
        grant_type="password",
    )
    return token

def extract_user_id_from_token(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.error("Token missing or invalid")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing or invalid")
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(
            token,
            KEYCLOAK_PUBLIC_KEY,
            algorithms=["RS256"],
            audience="account",
            options={"verify_aud": True, "verify_exp": True},
        )
        user_id = payload.get("sub")
        logger.info(f"Extracted Keycloak User ID: {user_id}")
        return user_id
    except JWTError as e:
        logger.error("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e
