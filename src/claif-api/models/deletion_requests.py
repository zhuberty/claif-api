from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ENUM as Enum
from models.base_models import ORMBase, Creatable, Modifiable


# SQLAlchemy models
class DeletionRequest(ORMBase, Creatable, Modifiable):
    __tablename__ = "deletion_requests"
    object_id = Column(Integer, index=True)
    object_type = Column(String)  # Use the named ENUM
    deletion_reason = Column(String)
    created_at = Column(DateTime, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), index=True)
    is_deleted = Column(Boolean, index=True)
    deleted_at = Column(DateTime, index=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), index=True)
