import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import Optional
from keycloak import KeycloakOpenID

# Keycloak settings
KEYCLOAK_SERVER_URL = os.environ.get("KEYCLOAK_SERVER_URL", "http://keycloak:8080")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "fastapi")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "fastapi-client")
KEYCLOAK_CLIENT_SECRET = os.environ.get("KEYCLOAK_CLIENT_SECRET", "g07L@Qg#mL&u8ukA2XE@L1wi&hioNRAoRGpYy")
KEYCLOAK_PUBLIC_KEY = None  # Will fetch from Keycloak

# Database URL (Using PostgreSQL)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://claif_db_user:claif_db_password@claif_db:5432/claif_db"
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

# Create the database tables, checking if they already exist
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine, checkfirst=True)
    # Fetch Keycloak public key
    global KEYCLOAK_PUBLIC_KEY

    print("Realm: ", KEYCLOAK_REALM)

    keycloak_openid = KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL + "/",
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM,
        client_secret_key=KEYCLOAK_CLIENT_SECRET,
    )
    KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Decode and verify the token
    try:
        payload = jwt.decode(
            token,
            KEYCLOAK_PUBLIC_KEY,
            algorithms=["RS256"],
            audience="account",
            options={"verify_aud": True, "verify_exp": True},
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from e

# Endpoint to create a new user
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    # Check if the email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create a new user instance
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh instance with new data from the database
    return new_user

# Endpoint to get user information by ID
@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(get_current_user)):
    # Retrieve user by ID
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Token endpoint for resource owner password credentials grant
@app.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    from keycloak import KeycloakOpenID

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
