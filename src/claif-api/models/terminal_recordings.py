from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# SQLAlchemy models
class TerminalRecording(Base):
    __tablename__ = "terminal_recordings"
    id = Column(Integer, primary_key=True, index=True)
    revision_number = Column(Integer, index=True)
    title = Column(String)
    description = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, index=True)
    recording_content = Column(String)
    recording_size_bytes = Column(Integer)
    recording_time_seconds = Column(Float)
    annotations_count = Column(Integer, default=0, index=True)


class TerminalRecordingAnnotation(Base):
    __tablename__ = "terminal_recording_annotations"
    id = Column(Integer, primary_key=True, index=True)
    terminal_recording_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    parent_annotation_id = Column(Integer, ForeignKey("terminal_recording_annotations.id"), index=True)
    annotation_text = Column(String)
    start_time_seconds = Column(Float)
    end_time_seconds = Column(Float)
    children_count = Column(Integer)