

from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from models.base_models import ORMBase


# SQLAlchemy models
class Annotation(ORMBase):
    """ Base class for all annotation types. """

    __abstract__ = True
    revision_number = Column(Integer)
    annotation_text = Column(String)
    start_time_milliseconds = Column(Float)
    end_time_milliseconds = Column(Float)
    reviews_count = Column(Integer, default=0)
    

class TerminalRecordingAnnotation(Annotation):
    __tablename__ = "terminal_recording_annotations"
    
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="terminal_annotations")
    recording_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    recording = relationship("TerminalRecording", foreign_keys=[recording_id], back_populates="annotations")
    annotation_review = relationship("TerminalAnnotationReview", back_populates="annotation", lazy="dynamic")


class AudioTranscriptionAnnotation(Annotation):
    __tablename__ = "audio_transcription_annotations"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_annotations")
    recording_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    recording = relationship("AudioTranscription", foreign_keys=[recording_id], back_populates="annotations")
    annotation_review = relationship("AudioAnnotationReview", back_populates="annotation", lazy="dynamic")


# Pydantic models
class TerminalAnnotationRead(BaseModel):
    """Pydantic model for reading terminal recording annotations."""
    id: int
    revision_number: int
    recording_id: int
    annotation_text: str
    start_time_milliseconds: int
    end_time_milliseconds: int
    reviews_count: int

    class Config:
        orm_mode = True
