from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from models.base_models import ORMBase, Deletable, Creatable


# SQLAlchemy Models
class User(ORMBase, Deletable, Creatable):
    __tablename__ = "users"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship(
        "User",
        foreign_keys=[creator_id],
        remote_side="User.id"
    )
    keycloak_id = Column(String, index=True, unique=True)
    username = Column(String, unique=True, index=True)
    audio_files = relationship("AudioFile", back_populates="creator", lazy="dynamic")
    audio_transcriptions = relationship("AudioTranscription", back_populates="creator", lazy="dynamic")
    audio_annotations = relationship("AudioTranscriptionAnnotation", back_populates="creator", lazy="dynamic")
    audio_annotation_reviews = relationship("AudioAnnotationReview", back_populates="creator", lazy="dynamic")
    terminal_recordings = relationship("TerminalRecording", back_populates="creator", lazy="dynamic")
    terminal_annotations = relationship("TerminalRecordingAnnotation", back_populates="creator", lazy="dynamic")
    terminal_annotation_reviews = relationship("TerminalAnnotationReview", back_populates="creator", lazy="dynamic")
    deletion_requests = relationship("DeletionRequest", foreign_keys="[DeletionRequest.creator_id]", back_populates="creator", lazy="dynamic")


# Pydantic Models
class UserRead(BaseModel):
    id: int
    keycloak_id: str
    username: str

    class Config:
        orm_mode = True  # Enables ORM model to Pydantic model conversion
