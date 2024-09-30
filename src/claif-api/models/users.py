from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from models.base_models import ORMBase, Creatable, Deletable


# SQLAlchemy Models
class User(ORMBase, Creatable, Deletable):
    __tablename__ = "users"
    keycloak_user_id = Column(String, index=True, unique=True)
    username = Column(String, unique=True, index=True)


# Pydantic Models
class UserRead(BaseModel):
    id: int
    keycloak_user_id: str
    username: str

    class Config:
        orm_mode = True  # Enables ORM model to Pydantic model conversion
