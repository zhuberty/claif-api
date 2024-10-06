from typing import Annotated, Optional
from pydantic import BaseModel, conint
from sqlalchemy import CheckConstraint, Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base_models import ORMBase, Creatable, Deletable
from models.users import UserRead


# SQLAlchemy models
class AnnotationReview(ORMBase, Creatable, Deletable):
    """ Base class for all annotation review types. """

    __abstract__ = True
    q_does_anno_match_content = Column(Boolean, index=True)
    q_can_anno_be_halved = Column(Boolean, index=True)
    q_how_well_anno_matches_content = Column(Integer, CheckConstraint(
        'q_how_well_anno_matches_content >= 1 AND q_how_well_anno_matches_content <= 10',
        name='check_q_how_well_anno_matches_content'
    ))
    q_can_you_improve_anno = Column(Boolean, index=True)
    q_can_you_provide_markdown = Column(Boolean, index=True)


class TerminalAnnotationReview(AnnotationReview):
    __tablename__ = "terminal_annotation_reviews"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="terminal_annotation_reviews")
    annotation_id = Column(Integer, ForeignKey("terminal_recording_annotations.id"), index=True)
    annotation = relationship("TerminalRecordingAnnotation", foreign_keys=[annotation_id], back_populates="annotation_reviews")
    terminal_recording_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    terminal_recording = relationship("TerminalRecording", foreign_keys=[terminal_recording_id], back_populates="annotation_reviews")
    q_can_provide_tintin_segment = Column(Boolean, index=True)


class AudioAnnotationReview(AnnotationReview):
    __tablename__ = "audio_annotation_reviews"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_annotation_reviews")
    annotation_id = Column(Integer, ForeignKey("audio_transcription_annotations.id"), index=True)
    annotation = relationship("AudioTranscriptionAnnotation", foreign_keys=[annotation_id], back_populates="annotation_reviews")
    audio_transcription_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    audio_transcription = relationship("AudioTranscription", foreign_keys=[audio_transcription_id], back_populates="annotation_reviews")


# Pydantic models
class AnnotationReviewRead(BaseModel):
    """Pydantic model for reading terminal recordings."""
    creator_id: int
    creator: UserRead
    annotation_id: int
    q_can_anno_be_halved: bool
    q_does_anno_match_content: bool
    q_how_well_anno_matches_content: int
    q_can_you_improve_anno: bool
    q_can_you_provide_markdown: bool
    

class AnnotationReviewCreate(BaseModel):
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


class AnnotationReviewUpdate(BaseModel):
    """Pydantic model for updating a terminal recording."""
    recording_id: Annotated[int, conint(gt=0)]
    title: Optional[str]
    description: Optional[str]
    content_metadata: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "recording_id": 1,
                "title": "Updated Recording Title",
                "description": "Updated description of the terminal recording",
                "content_metadata": "Header_content_of_the_asciinema_recording_here",
            }
        }