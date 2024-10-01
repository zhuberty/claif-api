from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from models.base_models import ORMBase, Creatable


class DeletionRequest(ORMBase, Creatable):
    __tablename__ = "deletion_requests"
    
    creator_id = Column(Integer, ForeignKey("users.id"), index=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="deletion_requests")
    closer_id = Column(Integer, ForeignKey("users.id"), index=True)
    object_id = Column(Integer, index=True)
    object_type = Column(String)
    deletion_reason = Column(String)
    deletion_status = Column(String, index=True)
    closed_at = Column(DateTime, index=True)
