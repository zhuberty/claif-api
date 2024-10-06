import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, conint
from models.recordings import TerminalRecording
from models.users import User, UserRead
from utils.database import get_db
from utils.auth import extract_user_id_or_raise, get_current_user, limiter
from utils.models.terminal_recordings import get_and_create_terminal_recording, create_annotation, extract_annotations
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
    source_revision_id: Optional[int]
    previous_revision_id: Optional[int]
    locked_for_review: bool
    revision_number: int
    published: bool
    creator: UserRead
    creator_id: int
    created_at: datetime
    is_deleted: bool

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
    title: Optional[str]
    description: Optional[str]
    content_metadata: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "recording_id": 1,
                "title": "Updated Recording Title",
                "description": "Updated description of the terminal recording",
                "content_metadata": "Header_content_of_the_asciinema_recording_here",
            }
        }


class TerminalRecordingTogglePublish(BaseModel):
    """Pydantic model for publishing a terminal recording."""
    recording_id: int
    is_published: bool


@router.post("/create")
@limiter.limit("5/minute")
async def create_recording(
    payload: TerminalRecordingCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Prepare the revision number and IDs for the new recording
        current_revision_number = 1

       # Create the new terminal recording without source_revision_id
        terminal_recording = get_and_create_terminal_recording(
            db=db,
            creator_id=current_user.id,
            title=payload.title,
            description=payload.description,
            recording_content=payload.recording_content,
            source_revision_id=None,  # Will be updated after the commit
            previous_revision_id=None,
            revision_number=current_revision_number,
        )

        db.add(terminal_recording)
        db.commit()

        # Refresh to get the generated ID
        db.refresh(terminal_recording)

        # Now Update the source_revision_id with the recording's own ID
        terminal_recording.source_revision_id = terminal_recording.id
        db.commit()
        db.refresh(terminal_recording)

        return {"message": "Recording created", "recording": TerminalRecordingRead.from_orm(terminal_recording)}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update")
@limiter.limit("5/minute")
async def update_recording(
    payload: TerminalRecordingUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Get the annotations from the encoded asciinema file-header string
        content_metadata = None
        annotations = []
        if payload.content_metadata is not None:
            content_metadata = json.loads(payload.content_metadata)
            annotations = extract_annotations(content_metadata)

        # Retrieve the current recording
        current_recording = db.query(TerminalRecording).filter_by(id=payload.recording_id).first()
        if current_recording is None:
            raise HTTPException(status_code=404, detail=f"Recording with ID {payload.recording_id} not found")
        
        # Prepare the revision number and IDs for the updated recording
        source_revision_id = current_recording.source_revision_id
        previous_revision_id = current_recording.id
        current_revision_number = current_recording.revision_number + 1

        # create a new recording with the updated title, description, and revision numbers
        updated_terminal_recording = TerminalRecording(
            creator_id=current_user.id,
            title=payload.title,
            description=payload.description,
            source_revision_id=source_revision_id,
            previous_revision_id=previous_revision_id,
            revision_number=current_revision_number,
            annotations_count=len(annotations),
            content_metadata=payload.content_metadata,
        )

        db.add(updated_terminal_recording)
        db.commit()
        db.refresh(updated_terminal_recording)

        # Create annotations for the updated recording
        try:
            for annotation in annotations:
                create_annotation(db, annotation, updated_terminal_recording.id)
        except Exception as e:
            db.delete(updated_terminal_recording)  # this cascade deletes annotations, too
            db.commit()
            raise HTTPException(status_code=400, detail=str(e))

        return {"message": "Recording updated", "recording_id": updated_terminal_recording.id}

    except (ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{recording_id}", response_model=TerminalRecordingRead)
@limiter.limit("20/minute")
async def read_recording(request: Request, recording_id: int, db: Session = Depends(get_db), response_model=TerminalRecordingRead):
    recording = db.query(TerminalRecording).filter_by(id=recording_id).first()
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@router.post("/publish")
@limiter.limit("5/minute")
async def publish_recording(
    payload: TerminalRecordingTogglePublish,
    request: Request,
    db: Session = Depends(get_db),
    keycloak_id: UserRead = Depends(extract_user_id_or_raise)
):
    recording = db.query(TerminalRecording).filter_by(id=payload.recording_id).first()
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    recording.published = payload.is_published
    db.commit()
    return {"message": f"Recording {'published' if payload.is_published else 'unpublished'} successfully"}
