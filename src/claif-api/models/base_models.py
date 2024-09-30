from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ORMBase(Base):
    """ Base class for all CLAIF API object types. """

    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)


# SQLAlchemy models
class Deletable(Base):
    """ Base class for all deletable object types. """
    
    __abstract__ = True
    deletion_request_id = Column(Integer, ForeignKey("deletion_requests.id", use_alter=True), index=True, default=None)


class Creatable(Base):
    """ Base class for all creatable object types. """

    __abstract__ = True
    created_at = Column(DateTime, index=True)
    created_by = Column(Integer, ForeignKey("users.id", use_alter=True), index=True)


class Annotatable(Base):
    """ Base class for all annotatable recording types. """

    __abstract__ = True
    content_metadata = Column(String)
    content_body = Column(String)
    annotations_count = Column(Integer, index=True)
    locked_for_review = Column(Boolean, index=True, default=False)


class Recording(ORMBase, Creatable, Deletable):
    """ Base class for all recording types. """

    __abstract__ = True
    revision_number = Column(Integer, index=True)
    title = Column(String)
    description = Column(String)
    size_bytes = Column(Integer)
    duration_milliseconds = Column(Float)


class Annotation(ORMBase):
    """ Base class for all annotation types. """

    __abstract__ = True
    annotation_text = Column(String)
    start_time_milliseconds = Column(Float)
    end_time_milliseconds = Column(Float)
    children_count = Column(Integer)
