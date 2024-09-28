from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from models.base_models import RecordingBase, AnnotationBase, AnnotatableBase

Base = declarative_base()


# SQLAlchemy models
class AudioFile(RecordingBase):
    __tablename__ = "audio_files"
    file_url = Column(String)


class AudioTranscription(RecordingBase, AnnotatableBase):
    __tablename__ = "audio_recording_transcriptions"
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"), index=True)
    transcription_text = Column(String)
    annotations_count = Column(Integer, index=True)


class AudioTranscriptionAnnotation(AnnotationBase):
    __tablename__ = "audio_transcription_annotations"
    audio_transcription_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    parent_annotation_id = Column(Integer, ForeignKey("audio_transcription_annotations.id"), index=True)
