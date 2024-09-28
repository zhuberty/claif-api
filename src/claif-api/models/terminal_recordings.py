from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# SQLAlchemy models
class TerminalRecording(Base):
    __tablename__ = "terminal_recordings"
    id = Column(Integer, primary_key=True, index=True)
    revision_number = Column(Integer)
    title = Column(String)
    description = Column(String)
    created_by_user_id = Column(String)
    created_at = Column(DateTime)
    recording_content = Column(String)
    recording_size_bytes = Column(Integer)
    recording_time_seconds = Column(Float)
    annotations_count = Column(Integer)
