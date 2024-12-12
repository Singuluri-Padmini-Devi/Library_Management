from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_librarian = Column(Boolean, default=False)
    borrow_requests = relationship("BorrowRequest", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    isbn = Column(String, unique=True)
    copies = Column(Integer)
    borrow_requests = relationship("BorrowRequest", back_populates="book")

class BorrowRequest(Base):
    __tablename__ = "borrow_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)  # pending, approved, denied, returned
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="borrow_requests")
    book = relationship("Book", back_populates="borrow_requests")