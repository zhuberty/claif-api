from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from models.recordings import TerminalRecording
from models.users import User
from models.annotation_reviews import (
    TerminalAnnotationReview,
    AudioAnnotationReview,
    AnnotationReviewCreate,
    AnnotationReviewRead,
    AnnotationReviewUpdate,
)
from utils.database import get_db
from utils.auth import get_current_user, limiter
from utils.exception_handlers import value_error_handler

router = APIRouter()


@router.post("/create")
@limiter.limit("5/minute")
@value_error_handler
async def create_annotation_review(
    payload: AnnotationReviewCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pass


@router.post("/update")
@limiter.limit("5/minute")
@value_error_handler
async def update_annotation_review(
    payload: AnnotationReviewUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pass


@router.get("/{recording_id}", response_model=AnnotationReviewRead)
@limiter.limit("20/minute")
@value_error_handler
async def read_recording(request: Request, recording_id: int, db: Session = Depends(get_db), response_model=AnnotationReviewRead):
    pass
