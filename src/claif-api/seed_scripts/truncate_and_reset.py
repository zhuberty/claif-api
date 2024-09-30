from sqlalchemy import text
from utils.database import run_with_db_session
from utils._logging import logging

def truncate_and_reset(db):
    # List of tables to truncate (in the correct order of dependencies)
    tables = [
        "deletion_requests", 
        "users", 
        "audio_files", 
        "audio_transcriptions", 
        "audio_transcription_annotations",
        "terminal_recordings", 
        "terminal_recording_annotations"
    ]
    
    # Truncate each table and reset primary key sequences
    for table in tables:
        logging.info(f"Truncating table {table} and resetting its primary key sequence.")
        
        # Truncate the table and restart identity (reset primary key sequence)
        db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
    
    db.commit()
    logging.info("All tables truncated and primary key sequences reset.")

if __name__ == "__main__":
    run_with_db_session(truncate_and_reset)
