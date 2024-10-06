from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from sqlalchemy.orm import Session
from models.users import User, UserRead
from utils.database import get_db
from utils.auth import limiter
from utils.exception_handlers import value_error_handler


router = APIRouter()
limiter = limiter


@router.get("/{user_id}", response_model=UserRead)
@limiter.limit("20/minute")
@value_error_handler
def read_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
