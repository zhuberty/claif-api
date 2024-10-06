from datetime import datetime
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


class AudioAnnotationReview(AnnotationReview):
    __tablename__ = "audio_annotation_reviews"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_annotation_reviews")
    annotation_id = Column(Integer, ForeignKey("audio_transcription_annotations.id"), index=True)
    annotation = relationship("AudioTranscriptionAnnotation", foreign_keys=[annotation_id], back_populates="annotation_reviews")
    audio_transcription_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    audio_transcription = relationship("AudioTranscription", foreign_keys=[audio_transcription_id], back_populates="annotation_reviews")


# Pydantic models (serializers/validators)
class AnnotationReviewQuestions(BaseModel):
    """Pydantic model for annotation reviews."""
    q_does_anno_match_content: bool
    q_can_anno_be_halved: bool
    q_how_well_anno_matches_content: int
    q_can_you_improve_anno: bool
    q_can_you_provide_markdown: bool


class AnnotationReviewRead(AnnotationReviewQuestions):
    """Pydantic model for terminal annotation reviews."""
    id: int
    annotation_id: int
    recording_id: int
    creator_id: int
    creator: UserRead
    created_at: datetime
    audio_recording_id: int


annotation_review_create_example = {
    "example": {
        "annotation_id": 1,
        "recording_id": 1,
        "q_does_anno_match_content": True,
        "q_can_anno_be_halved": False,
        "q_how_well_anno_matches_content": 5,
        "q_can_you_improve_anno": True,
        "q_can_you_provide_markdown": False,
    }
}


class AnnotationReviewCreate(AnnotationReviewQuestions):
    """Pydantic model for creating a terminal annotation review."""
    annotation_id: Annotated[int, conint(gt=0)]
    recording_id: Annotated[int, conint(gt=0)]

    class Config:
        schema_extra = annotation_review_create_example


class AnnotationReviewUpdate(AnnotationReviewQuestions):
    """Pydantic model for updating a terminal recording review."""
    annotation_id: Annotated[int, conint(gt=0)]
    recording_id: Annotated[int, conint(gt=0)]

    class Config:
        schema_extra = annotation_review_create_example
