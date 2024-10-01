from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ORMBase(Base):
    """ Base class for all CLAIF API object types. """

    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)


class Annotatable(Base):
    """ Base class for all annotatable recording types. """

    __abstract__ = True
    content_metadata = Column(String)
    content_body = Column(String)
    annotations_count = Column(Integer, index=True)
    published = Column(Boolean, index=True, default=False)
    locked_for_review = Column(Boolean, index=True, default=False)


class Creatable(Base):
    """ Base class for all creatable recording types. """

    __abstract__ = True
    created_at = Column(DateTime, index=True)


class Deletable(Base):
    """ Base class for all deletable recording types. """

    __abstract__ = True
    deletion_request_id = Column(Integer, ForeignKey("deletion_requests.id"), index=True)
    is_deleted = Column(Boolean, index=True, default=False)


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


class AnnotationReview(ORMBase, Creatable, Deletable):
    """ Base class for all annotation review types. """

    __abstract__ = True
    q_does_anno_match_content = Column(Boolean, index=True)
    q_can_anno_be_halved = Column(Boolean, index=True)
    q_how_well_anno_matches_content = Column(Integer, CheckConstraint(
        'q_how_well_anno_matches_content >= 1 AND q_how_well_anno_matches_content <= 10',
        name='check_q_how_well_anno_matches_content'
    ))
    q_can_you_improve_anno = Column(Boolean, index=True)
    q_can_you_provide_markdown = Column(Boolean, index=True)
