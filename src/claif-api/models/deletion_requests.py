from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from models.base_models import Base

# Define the PostgreSQL ENUM with a name
object_type_enum = Enum(
    "audio_file",
    "audio_transcription",
    "audio_transcription_annotation",
    "terminal_recording",
    "terminal_recording_annotation",
    "user",
    name="object_type_enum"  # Provide a name for the ENUM type
)

# SQLAlchemy models
class DeletionRequest(Base):
    __tablename__ = "deletion_requests"
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, index=True)
    object_type = Column(object_type_enum)  # Use the named ENUM
    deletion_reason = Column(String)
    created_at = Column(DateTime, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), index=True)
    is_deleted = Column(Boolean, index=True)
    deleted_at = Column(DateTime, index=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), index=True)
