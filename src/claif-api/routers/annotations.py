from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from models.recordings import TerminalRecording
from models.users import User
from models.annotation_reviews import AnnotationReviewCreate, AnnotationReviewRead, AnnotationReviewUpdate
from utils.database import get_db
from utils.auth import get_current_user, limiter

router = APIRouter()


@router.post("/create")
@limiter.limit("5/minute")
async def create_recording(
    payload: AnnotationReviewCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pass
    except (ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update")
@limiter.limit("5/minute")
async def update_recording(
    payload: AnnotationReviewUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pass
    except (ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{recording_id}", response_model=AnnotationReviewRead)
@limiter.limit("20/minute")
async def read_recording(request: Request, recording_id: int, db: Session = Depends(get_db), response_model=AnnotationReviewRead):
    recording = db.query(TerminalRecording).filter_by(id=recording_id).first()
    if recording is None:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording
