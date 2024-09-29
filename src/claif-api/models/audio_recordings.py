from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from models.base_models import Recording, Annotation, Annotatable


# SQLAlchemy models
class AudioFile(Recording):
    __tablename__ = "audio_files"
    file_url = Column(String)


class AudioTranscription(Recording, Annotatable):
    __tablename__ = "audio_transcriptions"
    audio_file_id = Column(Integer, ForeignKey("audio_files.id"), index=True)


class AudioTranscriptionAnnotation(Annotation):
    __tablename__ = "audio_transcription_annotations"
    audio_transcription_id = Column(Integer, ForeignKey("audio_transcriptions.id"), index=True)
    parent_annotation_id = Column(Integer, ForeignKey("audio_transcription_annotations.id"), index=True)
