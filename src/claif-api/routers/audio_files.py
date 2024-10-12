import mimetypes
from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from models.recordings import AudioFile
from models.users import User
from utils.database import get_db
from utils.auth import get_current_user, limiter
from utils.exception_handlers import value_error_handler
from utils.minio_utils import ensure_bucket_exists, upload_file_to_minio
from datetime import datetime, timezone
import logging

router = APIRouter()

@router.post("/create")
@limiter.limit("5/minute")
@value_error_handler
async def create_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new audio file by uploading to Minio and storing metadata in the database."""
    
    logging.info(f"Received file: {file.filename}")  # Log the received file
    
    # Ensure the bucket exists
    try:
        ensure_bucket_exists()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Bucket error: {str(e)}")
    
    # Read the uploaded file data
    file_data = await file.read()

    # Infer content type if not provided
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    # Generate a unique file name
    file_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{file.filename}"

    # Upload the file to MinIO
    try:
        upload_result = upload_file_to_minio(
            file_data=file_data,
            file_name=file_name,
            content_type=content_type,  # Use the inferred or provided content type
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")
    
    # Store file metadata in the database
    new_audio_file = AudioFile(
        storage_path=f"audio/{file_name}",
        creator_id=current_user.id,
        size_bytes=len(file_data),
        content_type=content_type,  # Store the correct content type
        duration_milliseconds=None,
        created_at=datetime.now(timezone.utc),
        revision_number=1,
        title=file.filename,
        description=None,
    )
    
    db.add(new_audio_file)
    db.commit()
    db.refresh(new_audio_file)

    return {"message": "File uploaded and metadata stored successfully", "file_metadata": new_audio_file}
