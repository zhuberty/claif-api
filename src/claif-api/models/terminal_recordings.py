from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base
from models.base_models import RecordingBase, AnnotationBase, AnnotatableBase

Base = declarative_base()


# SQLAlchemy models
class TerminalRecording(RecordingBase, AnnotatableBase):
    __tablename__ = "terminal_recordings"
    recording_text = Column(String)
    annotations_count = Column(Integer, index=True)


class TerminalRecordingAnnotation(AnnotationBase):
    __tablename__ = "terminal_recording_annotations"
    terminal_recording_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    parent_annotation_id = Column(Integer, ForeignKey("terminal_recording_annotations.id"), index=True)