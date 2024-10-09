import json
from fastapi import APIRouter, Depends, HTTPException, Request

from models.recordings import TerminalRecording
from models.users import User
from models.recordings import TerminalRecordingCreate, TerminalRecordingRead, TerminalRecordingUpdate, TerminalRecordingListRead
from models.annotations import TerminalAnnotationRead, TerminalAnnotationRead
from models.annotation_reviews import AnnotationReviewRead
from models.utils.terminal_recordings import create_annotation, extract_annotations, parse_asciinema_recording
from utils.database import get_db
from utils.auth import get_current_user, limiter
from utils.exception_handlers import value_error_handler
from sqlalchemy.orm import Session
from sqlalchemy.orm import load_only

router = APIRouter()


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
        creator_username=current_user.username,
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

    return {"message": "Recording created", "recording_id": terminal_recording.id}


@router.get("/read/{recording_id}")
@limiter.limit("20/minute")
@value_error_handler
async def read_recording(
    request: Request,
    recording_id: int,
    revision_number: int = None,
    db: Session = Depends(get_db),
):
    # Fetch the recording
    recording = db.query(TerminalRecording).filter_by(id=recording_id).first()
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Convert the dynamic annotations relationship into a list of Pydantic models
    if revision_number is None:
        revision_number = recording.revision_number
    annotations = list(recording.annotations.filter_by(revision_number=revision_number).all())
    annotations_list = [TerminalAnnotationRead.from_orm(annotation) for annotation in annotations]

    annotation_reviews = list(recording.annotation_reviews.filter_by(revision_number=revision_number).all())
    annotation_reviews_list = [AnnotationReviewRead.from_orm(review) for review in annotation_reviews]

    return {
        "recording": TerminalRecordingRead.from_orm(recording), 
        "annotations": annotations_list,
        "annotation_reviews": annotation_reviews_list,
        "selected_revision_number": revision_number,
    }


@router.get("/list")
@limiter.limit("5/minute")
@value_error_handler
async def list_recordings(request: Request, db: Session = Depends(get_db)):
    recordings = db.query(TerminalRecording).options(load_only(
        TerminalRecording.id,
        TerminalRecording.revision_number,
        TerminalRecording.title,
        TerminalRecording.description, 
        TerminalRecording.creator_id,
    )).all()
    return [TerminalRecordingListRead.from_orm(recording) for recording in recordings]


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
