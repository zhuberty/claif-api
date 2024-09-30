from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.base_models import ORMBase, Annotation, Recording, Annotatable


# SQLAlchemy models
class TerminalRecording(Recording, Annotatable):
    __tablename__ = "terminal_recordings"
    source_revision_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    previous_revision_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)


annotation_child_association = Table(
    'annotation_child_association',
    ORMBase.metadata,
    Column('parent_annotation_id', Integer, ForeignKey('terminal_recording_annotations.id')),
    Column('child_annotation_id', Integer, ForeignKey('terminal_recording_annotations.id'))
)


class TerminalRecordingAnnotation(Annotation):
    __tablename__ = "terminal_recording_annotations"
    
    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("terminal_recordings.id"), index=True)
    parent_annotation_id = Column(Integer, ForeignKey("terminal_recording_annotations.id"), index=True)
    children = relationship(
        "TerminalRecordingAnnotation",
        secondary=annotation_child_association,
        primaryjoin="TerminalRecordingAnnotation.id==annotation_child_association.c.parent_annotation_id",
        secondaryjoin="TerminalRecordingAnnotation.id==annotation_child_association.c.child_annotation_id",
        backref="parents"
    )
