from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from typing import List

router = APIRouter(prefix="/librarian", tags=["librarian"])

async def get_current_librarian(
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.is_librarian:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.post("/users", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_librarian)
):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/requests", response_model=List[schemas.BorrowRequest])
def get_all_requests(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_librarian)
):
    return db.query(models.BorrowRequest).all()

@router.put("/requests/{request_id}")
def update_request_status(
    request_id: int,
    status: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_librarian)
):
    if status not in ["approved", "denied"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    borrow_request = db.query(models.BorrowRequest).filter(
        models.BorrowRequest.id == request_id
    ).first()
    
    if not borrow_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    borrow_request.status = status
    db.commit()
    return {"message": "Status updated successfully"}