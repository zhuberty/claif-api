import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, conint
from models.recordings import TerminalRecording
from models.users import User, UserRead
from models.utils.terminal_recordings import create_annotation, extract_annotations, parse_asciinema_recording
from utils.database import get_db
from utils.auth import get_current_user, limiter
from utils.exception_handlers import value_error_handler
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Annotated

router = APIRouter()


class TerminalRecordingRead(BaseModel):
    """Pydantic model for reading terminal recordings."""
    id: int
    title: str
    description: str
    size_bytes: int
    duration_milliseconds: int
    content_metadata: str
    content_body: str
    annotations_count: int
    revision_number: int
    creator: UserRead
    creator_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class TerminalRecordingCreate(BaseModel):
    """Pydantic model for creating a terminal recording."""
    title: str
    description: Optional[str]
    recording_content: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "title": "Example Recording Title",
                "description": "Description of the terminal recording",
                "recording_content": "Contents_of_the_asciinema_recording_here",
            }
        }


class TerminalRecordingUpdate(BaseModel):
    """Pydantic model for updating a terminal recording."""
    recording_id: Annotated[int, conint(gt=0)]
    title: str
    description: str
    content_metadata: str

    class Config:
        schema_extra = {
            "example": {
                "recording_id": 1,
                "title": "Updated Recording Title",
                "description": "Updated description of the terminal recording",
                "content_metadata": "Header_content_of_the_asciinema_recording_here",
            }
        }


@router.post("/create")
@limiter.limit("5/minute")
@value_error_handler
async def create_recording(
    payload: TerminalRecordingCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    content_metadata, content_body, annotations = parse_asciinema_recording(payload.recording_content)

    terminal_recording = TerminalRecording(
        creator_id=current_user.id,
        title=payload.title,
        description=payload.description,
        revision_number=1,
        content_metadata=json.dumps(content_metadata),
        content_body=json.dumps(content_body),
        annotations_count=len(annotations),
        size_bytes=len(json.dumps(content_metadata)) + len(json.dumps(content_body)),
        duration_milliseconds=content_body[-1][0] * 1000 if content_body else 0,
    )

    db.add(terminal_recording)
    db.commit()

    # Refresh to get the generated ID
    db.refresh(terminal_recording)

    return {"message": "Recording created", "recording": TerminalRecordingRead.from_orm(terminal_recording)}


@router.post("/update")
@limiter.limit("5/minute")
@value_error_handler
async def update_recording(
    payload: TerminalRecordingUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get the annotations from the encoded asciinema file-header string
    content_metadata = None
    annotations = []
    if payload.content_metadata is not None:
        content_metadata = json.loads(payload.content_metadata)
        annotations = extract_annotations(content_metadata)

    # Retrieve the current recording
    recording = db.query(TerminalRecording).filter_by(id=payload.recording_id).first()
    if recording is None:
        raise HTTPException(status_code=404, detail=f"Recording with ID {payload.recording_id} not found")
    
    # update the recording with the updated title, description, and revision numbers
    recording.title = payload.title
    recording.description = payload.description
    recording.revision_number += 1
    recording.annotations_count = len(annotations)
    recording.content_metadata = payload.content_metadata

    # Create annotations linked to the new revision number
    try:
        for annotation in annotations:
            create_annotation(db, annotation, recording.id, recording.revision_number)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    db.commit()
    return {"message": "Recording updated"}


@router.get("/{recording_id}", response_model=TerminalRecordingRead)
@limiter.limit("20/minute")
@value_error_handler
async def read_recording(request: Request, recording_id: int, db: Session = Depends(get_db), response_model=TerminalRecordingRead):
    recording = db.query(TerminalRecording).filter_by(id=recording_id).first()
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording
