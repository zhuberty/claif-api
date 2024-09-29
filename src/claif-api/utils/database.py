import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from utils.logging import logging


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


def run_with_db_session(callback):
    """
    General-purpose function to run a task that requires a DB session.
    
    :param callback: Function that performs the DB logic. Should accept a DB session as an argument.
    """
    db = SessionLocal()
    try:
        logging.debug("Running database operation...")
        callback(db)
        logging.debug("Database operation completed.")
    except Exception as e:
        db.rollback()
        logging.error(f"Database operation rrror: {e}")
    finally:
        db.close()