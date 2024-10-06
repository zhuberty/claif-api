from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models.base_models import Creatable, Deletable, ORMBase


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
    published = Column(Boolean, index=True, default=False)
    locked_for_review = Column(Boolean, index=True, default=False)


class TerminalRecording(RecordingAnnotatable):
    __tablename__ = "terminal_recordings"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="terminal_recordings")
    annotations = relationship("TerminalRecordingAnnotation", back_populates="recording", lazy="dynamic", cascade="all, delete-orphan")
    annotation_reviews = relationship("TerminalAnnotationReview", back_populates="recording", lazy="dynamic", cascade="all, delete-orphan")
    deletion_request_id = Column(Integer, ForeignKey("deletion_requests.id"), index=True)


class AudioFile(Recording):
    __tablename__ = "audio_files"
    file_url = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_files")
    audio_transcriptions = relationship("AudioTranscription", back_populates="audio_file", lazy="dynamic")


class AudioTranscription(RecordingAnnotatable):
    __tablename__ = "audio_transcriptions"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_transcriptions")
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"), index=True)
    audio_file = relationship("AudioFile", foreign_keys=[audio_file_id], back_populates="audio_transcriptions")
    annotations = relationship("AudioTranscriptionAnnotation", back_populates="recording", lazy="dynamic")
    annotation_reviews = relationship("AudioAnnotationReview", back_populates="recording", lazy="dynamic")
