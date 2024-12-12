from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from typing import List
import csv
from fastapi.responses import StreamingResponse
from io import StringIO

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/history", response_model=List[schemas.BorrowRequest])
def get_user_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.BorrowRequest).filter(
        models.BorrowRequest.user_id == current_user.id
    ).all()

@router.get("/me/history/download")
def download_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    borrow_requests = db.query(models.BorrowRequest).filter(
        models.BorrowRequest.user_id == current_user.id
    ).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Book ID", "Start Date", "End Date", "Status", "Created At"])
    
    for request in borrow_requests:
        writer.writerow([
            request.book_id,
            request.start_date,
            request.end_date,
            request.status,
            request.created_at
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment;filename=borrow_history.csv"}
    )