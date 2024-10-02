from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.base_models import ORMBase, Recording, Annotation, Annotatable, Creatable

# Association table for parent-child relationships in annotations
audio_annotation_child_association = Table(
    'audio_annotation_child_association',
    ORMBase.metadata,
    Column('parent_annotation_id', Integer, ForeignKey('audio_transcription_annotations.id')),
    Column('child_annotation_id', Integer, ForeignKey('audio_transcription_annotations.id'))
)

# SQLAlchemy models
class AudioFile(Recording):
    __tablename__ = "audio_files"
    file_url = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_files")
    audio_transcriptions = relationship("AudioTranscription", back_populates="audio_file", lazy="dynamic")


class AudioTranscription(Recording, Annotatable):
    __tablename__ = "audio_transcriptions"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_transcriptions")
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"), index=True)
    audio_file = relationship("AudioFile", foreign_keys=[audio_file_id], back_populates="audio_transcriptions")
    annotations = relationship("AudioTranscriptionAnnotation", back_populates="audio_transcription", lazy="dynamic")
    annotation_reviews = relationship("AudioAnnotationReview", back_populates="audio_transcription", lazy="dynamic")
    source_revision_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    source_revision = relationship(
        "AudioTranscription",
        foreign_keys=[source_revision_id],
        remote_side="AudioTranscription.id"
    )
    previous_revision_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    previous_revision = relationship(
        "AudioTranscription",
        foreign_keys=[previous_revision_id],
        remote_side="AudioTranscription.id"
    )


class AudioTranscriptionAnnotation(Annotation):
    __tablename__ = "audio_transcription_annotations"
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="audio_annotations")
    audio_transcription_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    audio_transcription = relationship("AudioTranscription", foreign_keys=[audio_transcription_id], back_populates="annotations")
    annotation_reviews = relationship("AudioAnnotationReview", back_populates="annotation", lazy="dynamic")

    # Association with child annotations via the association table
    child_annotations = relationship(
        "AudioTranscriptionAnnotation",
        secondary=audio_annotation_child_association,
        primaryjoin="AudioTranscriptionAnnotation.id == audio_annotation_child_association.c.parent_annotation_id",
        secondaryjoin="AudioTranscriptionAnnotation.id == audio_annotation_child_association.c.child_annotation_id",
        backref="parent_annotations"
    )
