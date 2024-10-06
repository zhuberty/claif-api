import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils._logging import logging
from models.users import User, UserRead
from models.recordings import TerminalRecording, AudioFile, AudioTranscription
from models.annotations import TerminalRecordingAnnotation, AudioTranscriptionAnnotation
from models.annotation_reviews import TerminalAnnotationReview, AudioAnnotationReview
from models.deletion_requests import DeletionRequest




DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://claif_db_user:claif_db_password@localhost:5433/claif_db"
)

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_with_db_session(callback, *args, **kwargs):
    """
    General-purpose function to run a task that requires a DB session.
    
    :param callback: Function that performs the DB logic. Should accept a DB session as an argument.
    :param args: Positional arguments to pass to the callback function.
    :param kwargs: Keyword arguments to pass to the callback function.
    """
    db = SessionLocal()
    try:
        logging.debug("Running database operation...")
        callback(db, *args, **kwargs)
        logging.debug("Database operation completed.")
    except Exception as e:
        db.rollback()
        logging.error(f"Database operation error: {e}")
    finally:
        db.close()
