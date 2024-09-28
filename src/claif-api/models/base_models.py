from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
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
    deletion_request_id = Column(Integer, ForeignKey("deletion_requests.id"), index=True)


class Creatable(Base):
    """ Base class for all creatable object types. """

    __abstract__ = True
    created_at = Column(DateTime, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), index=True)


class Modifiable(Base):
    """ Base class for all modifiable object types. """

    __abstract__ = True
    modified_at = Column(DateTime, index=True)
    modified_by = Column(Integer, ForeignKey("users.id"), index=True)


class Annotatable(Base):
    """ Base class for all annotatable recording types. """

    __abstract__ = True
    content_metadata = Column(String)
    content_body = Column(String)
    annotations_count = Column(Integer, index=True)


class Recording(ORMBase, Creatable, Modifiable, Deletable):
    """ Base class for all recording types. """

    __abstract__ = True
    revision_number = Column(Integer, index=True)
    title = Column(String)
    description = Column(String)
    size_bytes = Column(Integer)
    duration_seconds = Column(Float)


class Annotation(ORMBase, Deletable):
    """ Base class for all annotation types. """

    __abstract__ = True
    annotation_text = Column(String)
    start_time_seconds = Column(Float)
    end_time_seconds = Column(Float)
    children_count = Column(Integer)
