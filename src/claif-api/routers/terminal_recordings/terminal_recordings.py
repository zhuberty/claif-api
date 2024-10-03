import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from models.terminal_recordings import TerminalRecording, TerminalRecordingAnnotation
from models.users import User, UserRead
from utils.database import get_db
from utils.auth import extract_user_id_or_raise, limiter
from utils.models.terminal_recordings import get_and_create_terminal_recording
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import base64

router = APIRouter()


class TerminalRecordingRead(BaseModel):
    """Pydantic model for reading terminal recordings."""
    id: int
    title: str
    description: Optional[str]
    size_bytes: int
    duration_milliseconds: int
    content_metadata: str
    content_body: str
    annotations_count: int
    source_revision_id: Optional[int]
    previous_revision_id: Optional[int]
    locked_for_review: bool
    revision_number: int
    published: bool
    creator: UserRead
    created_at: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class TerminalRecordingCreate(BaseModel):
    """Pydantic model for creating a new terminal recording."""
    creator_id: int
    title: str
    description: Optional[str]
    recording_content: str  # Base64 encoded string for the Asciinema recording content
    revision_number: Optional[int] = 1
    source_revision_id: Optional[int] = None
    previous_revision_id: Optional[int] = None
    published: Optional[bool] = False

    class Config:
        schema_extra = {
            "example": {
                "title": "Example Recording Title",
                "description": "Description of the terminal recording",
                "recording_content": "Base64_encoded_string_of_recording_content_here",
                "revision_number": 1,
                "published": False
            }
        }

    def decode_recording_content(self) -> str:
        """Helper method to decode the Base64 recording content."""
        return base64.b64decode(self.recording_content).decode('utf-8')


@router.post("/create")
@limiter.limit("5/minute")
async def create_recording(
    payload: TerminalRecordingCreate,
    request: Request,
    db: Session = Depends(get_db),
    keycloak_id: UserRead = Depends(extract_user_id_or_raise)
):
    try:
        # Check if a recording with the same source_id and revision_number already exists
        existing_recording = db.query(TerminalRecording).filter_by(
            source_revision_id=payload.source_revision_id,
            revision_number=payload.revision_number
        ).first()

        if existing_recording:
            return JSONResponse(
                status_code=400,
                content={"detail": f"Recording with source ID {payload.source_revision_id} already exists with revision number {payload.revision_number}"}
            )

        # Decode the Base64 encoded recording content
        decoded_content = payload.decode_recording_content()

        # Create the new terminal recording
        terminal_recording = get_and_create_terminal_recording(
            db=db,
            title=payload.title,
            description=payload.description,
            recording_content=decoded_content,  # Use the decoded content
            revision_number=payload.revision_number,
            creator_id=payload.creator_id,
            source_revision_id=1,
            previous_revision_id=2,
        )

        return {"message": "Recording created", "recording": terminal_recording}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/{recording_id}", response_model=TerminalRecordingRead)
@limiter.limit("20/minute")
async def read_recording(request: Request, recording_id: int, db: Session = Depends(get_db), response_model=TerminalRecordingRead):
    recording = db.query(TerminalRecording).filter_by(id=recording_id).first()
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording
