from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, conint
from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_models import ORMBase, Creatable, Deletable
from models.users import UserRead


# SQLAlchemy models
class Recording(ORMBase, Creatable, Deletable):
    """ Base class for all recording types. """

    __abstract__ = True
    revision_number = Column(Integer, index=True)
    title = Column(String)
    description = Column(String)
    size_bytes = Column(Integer)
    duration_milliseconds = Column(Float)


class RecordingAnnotatable(Recording):
    """ Base class for all annotatable recording types. """

    __abstract__ = True
    content_metadata = Column(String)
    content_body = Column(String)
    annotations_count = Column(Integer, index=True)


class TerminalRecording(RecordingAnnotatable):
    __tablename__ = "terminal_recordings"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="terminal_recordings")
    annotations = relationship("TerminalRecordingAnnotation", back_populates="recording", lazy="dynamic", cascade="all, delete-orphan")
    annotation_reviews = relationship("TerminalAnnotationReview", back_populates="recording", lazy="dynamic", cascade="all, delete-orphan")


class AudioFile(Recording):
    __tablename__ = "audio_files"
    file_url = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_files")
    audio_transcription = relationship("AudioTranscription", back_populates="audio_file", lazy="dynamic")


class AudioTranscription(RecordingAnnotatable):
    __tablename__ = "audio_transcriptions"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_transcriptions")
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"), index=True)
    audio_file = relationship("AudioFile", foreign_keys=[audio_file_id], back_populates="audio_transcription")
    annotations = relationship("AudioTranscriptionAnnotation", back_populates="recording", lazy="dynamic")
    annotation_reviews = relationship("AudioAnnotationReview", back_populates="recording", lazy="dynamic")


# Pydantic models
class TerminalRecordingRead(BaseModel):
    """Pydantic model for reading terminal recordings."""
    id: int
    title: str
    description: str
    size_bytes: int
    duration_milliseconds: int
    content_metadata: str
    content_body: str
    annotations_count: int
    revision_number: int
    creator: UserRead
    creator_id: int
    created_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


# Pydantic models
class TerminalRecordingListRead(BaseModel):
    """Pydantic model for reading terminal recordings in a list. """
    id: int
    title: str
    description: str
    revision_number: int
    creator_id: int
    annotations_count: int
    size_bytes: int
    duration_milliseconds: int

    class Config:
        orm_mode = True


class TerminalRecordingCreate(BaseModel):
    """Pydantic model for creating a terminal recording."""
    title: str
    description: Optional[str]
    recording_content: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "title": "Example Recording Title",
                "description": "Description of the terminal recording",
                "recording_content": "Contents_of_the_asciinema_recording_here",
            }
        }


class TerminalRecordingUpdate(BaseModel):
    """Pydantic model for updating a terminal recording."""
    recording_id: Annotated[int, conint(gt=0)]
    title: str
    description: str
    content_metadata: str

    class Config:
        schema_extra = {
            "example": {
                "recording_id": 1,
                "title": "Updated Recording Title",
                "description": "Updated description of the terminal recording",
                "content_metadata": "Header_content_of_the_asciinema_recording_here",
            }
        }