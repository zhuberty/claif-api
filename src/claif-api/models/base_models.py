from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# SQLAlchemy models
class RecordingBase(Base):
    """ Base class for all recording types. """

    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    revision_number = Column(Integer, index=True)
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), index=True)
    size_bytes = Column(Integer)
    duration_seconds = Column(Float)


class AnnotatableBase(Base):
    """ Base class for all annotatable recording types. """

    __abstract__ = True
    annotations_count = Column(Integer, index=True)
    content_metadata = Column(String)
    content_body = Column(String)


class AnnotationBase(Base):
    """ Base class for all annotation types. """

    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    annotation_text = Column(String)
    start_time_seconds = Column(Float)
    end_time_seconds = Column(Float)
    children_count = Column(Integer)