from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# SQLAlchemy models
class AudioRecording(Base):
    __tablename__ = "audio_recordings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    recording_url = Column(String)
    author_user_id = Column(String)
    created_at = Column(DateTime)


class AudioTranscription(Base):
    __tablename__ = "audio_transcriptions"
    id = Column(Integer, primary_key=True, index=True)
    audio_recording_id = Column(Integer, ForeignKey("audio_recordings.id"))
    revision_number = Column(Integer)
    transcription_text = Column(String)
    created_at = Column(DateTime)
