from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ORMBase(Base):
    """ Base class for all CLAIF API object types. """

    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)


class Creatable(Base):
    """ Base class for all creatable recording types. """

    __abstract__ = True
    created_at = Column(DateTime, index=True)


class Deletable(Base):
    """ Base class for all deletable recording types. """

    __abstract__ = True
    deletion_request_id = Column(Integer, ForeignKey("deletion_requests.id"), index=True)
    is_deleted = Column(Boolean, index=True, default=False)
