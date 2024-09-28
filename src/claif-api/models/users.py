from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)


# Pydantic Models
class UserRead(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True  # Enables ORM model to Pydantic model conversion