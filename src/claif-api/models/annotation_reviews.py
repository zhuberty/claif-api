from sqlalchemy import CheckConstraint, Column, Integer, ForeignKey, DateTime, Boolean, String
from sqlalchemy.orm import relationship
from models.base_models import ORMBase, Creatable, Deletable


class AnnotationReview(ORMBase, Creatable, Deletable):
    __tablename__ = "annotation_reviews"
    annotation_id = Column(Integer, ForeignKey("terminal_recording_annotations.id"), index=True)
    q_does_anno_match_content = Column(Boolean, index=True)
    q_can_anno_be_halved = Column(Boolean, index=True)
    q_how_well_anno_matches_content = Column(Integer, CheckConstraint(
        'q_how_well_anno_matches_content >= 1 AND q_how_well_anno_matches_content <= 10',
        name='check_q_how_well_anno_matches_content'
    ))
    q_can_you_improve_anno = Column(Boolean, index=True)
    q_can_you_provide_markdown = Column(Boolean, index=True)
    q_can_provide_tintin_segment = Column(Boolean, index=True)
    reviewer = relationship("User", back_populates="annotation_reviews")