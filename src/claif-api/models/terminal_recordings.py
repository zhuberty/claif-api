from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from models.base_models import Recording, Annotation, Annotatable


# SQLAlchemy models
class TerminalRecording(Recording, Annotatable):
    __tablename__ = "terminal_recordings"


class TerminalRecordingAnnotation(Annotation):
    __tablename__ = "terminal_recording_annotations"
    terminal_recording_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    parent_annotation_id = Column(Integer, ForeignKey("terminal_recording_annotations.id"), index=True)
