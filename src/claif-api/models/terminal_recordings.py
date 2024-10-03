from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.base_models import ORMBase, Annotation, Recording, Annotatable


# SQLAlchemy models
class TerminalRecording(Recording, Annotatable):
    __tablename__ = "terminal_recordings"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="terminal_recordings")
    source_revision_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    source_revision = relationship(
        "TerminalRecording",
        foreign_keys=[source_revision_id],
        remote_side="TerminalRecording.id"
    )
    previous_revision_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    previous_revision = relationship(
        "TerminalRecording",
        foreign_keys=[previous_revision_id],
        remote_side="TerminalRecording.id"
    )
    annotations = relationship("TerminalRecordingAnnotation", back_populates="recording", lazy="dynamic", cascade="all, delete-orphan")
    annotation_reviews = relationship("TerminalAnnotationReview", back_populates="terminal_recording", lazy="dynamic", cascade="all, delete-orphan")
    deletion_request_id = Column(Integer, ForeignKey("deletion_requests.id"), index=True)


# Association table for parent-child relationships in annotations
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
