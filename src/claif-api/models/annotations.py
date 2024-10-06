

from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Float, Integer, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from models.base_models import ORMBase


# SQLAlchemy models
class Annotation(ORMBase):
    """ Base class for all annotation types. """

    __abstract__ = True
    annotation_text = Column(String)
    start_time_milliseconds = Column(Float)
    end_time_milliseconds = Column(Float)
    children_count = Column(Integer)
    

terminal_annotation_child_association = Table(
    'terminal_annotation_child_association',
    ORMBase.metadata,
    Column('parent_annotation_id', Integer, ForeignKey('terminal_recording_annotations.id')),
    Column('child_annotation_id', Integer, ForeignKey('terminal_recording_annotations.id'))
)


class TerminalRecordingAnnotation(Annotation):
    __tablename__ = "terminal_recording_annotations"
    
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="terminal_annotations")
    recording_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    recording = relationship("TerminalRecording", foreign_keys=[recording_id], back_populates="annotations")
    parent_annotation_id = Column(Integer, ForeignKey("terminal_recording_annotations.id"), index=True)
    child_annotations = relationship(
        "TerminalRecordingAnnotation",
        secondary=terminal_annotation_child_association,
        primaryjoin="TerminalRecordingAnnotation.id == terminal_annotation_child_association.c.parent_annotation_id",
        secondaryjoin="TerminalRecordingAnnotation.id == terminal_annotation_child_association.c.child_annotation_id",
        backref="parent_annotations"
    )
    annotation_reviews = relationship("TerminalAnnotationReview", back_populates="annotation", lazy="dynamic")


audio_annotation_child_association = Table(
    'audio_annotation_child_association',
    ORMBase.metadata,
    Column('parent_annotation_id', Integer, ForeignKey('audio_transcription_annotations.id')),
    Column('child_annotation_id', Integer, ForeignKey('audio_transcription_annotations.id'))
)


class AudioTranscriptionAnnotation(Annotation):
    __tablename__ = "audio_transcription_annotations"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_annotations")
    recording_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    recording = relationship("AudioTranscription", foreign_keys=[recording_id], back_populates="annotations")
    annotation_reviews = relationship("AudioAnnotationReview", back_populates="annotation", lazy="dynamic")

    # Association with child annotations via the association table
    child_annotations = relationship(
        "AudioTranscriptionAnnotation",
        secondary=audio_annotation_child_association,
        primaryjoin="AudioTranscriptionAnnotation.id == audio_annotation_child_association.c.parent_annotation_id",
        secondaryjoin="AudioTranscriptionAnnotation.id == audio_annotation_child_association.c.child_annotation_id",
        backref="parent_annotations"
    )


# Pydantic models
class TerminalAnnotationRead(BaseModel):
    """Pydantic model for reading terminal recording annotations."""
    id: int
    parent_annotation_id: Optional[int]
    annotation_text: str
    start_time_milliseconds: int
    end_time_milliseconds: Optional[int]
    children_count: int
