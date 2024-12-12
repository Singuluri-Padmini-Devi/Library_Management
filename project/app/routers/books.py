from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from typing import List
from datetime import datetime

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=List[schemas.Book])
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@router.post("/borrow", response_model=schemas.BorrowRequest)
def borrow_book(
    request: schemas.BorrowRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Check if book exists
    book = db.query(models.Book).filter(models.Book.id == request.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Check for overlapping requests
    overlapping_requests = db.query(models.BorrowRequest).filter(
        models.BorrowRequest.book_id == request.book_id,
        models.BorrowRequest.status == "approved",
        models.BorrowRequest.start_date <= request.end_date,
        models.BorrowRequest.end_date >= request.start_date
    ).count()

    if overlapping_requests >= book.copies:
        raise HTTPException(status_code=400, detail="Book not available for selected dates")

    borrow_request = models.BorrowRequest(
        user_id=current_user.id,
        book_id=request.book_id,
        start_date=request.start_date,
        end_date=request.end_date,
        status="pending"
    )
    db.add(borrow_request)
    db.commit()
    db.refresh(borrow_request)
    return borrow_request