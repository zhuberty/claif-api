from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base_models import AnnotationReview


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
