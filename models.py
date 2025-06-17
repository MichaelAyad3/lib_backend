from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

    rentals = relationship("Rental", back_populates="user", cascade="all, delete-orphan")
    wishlist = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True, nullable=False)
    authors = Column(String)
    publication_year = Column(Integer)
    title = Column(String)
    language = Column(String)
    available = Column(Boolean, default=True)
    amazon_id = Column(String, nullable=True)

    rentals = relationship("Rental", back_populates="book", cascade="all, delete-orphan")
    wishlisted_by = relationship("Wishlist", back_populates="book", cascade="all, delete-orphan")


class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))

    user = relationship("User", back_populates="wishlist")
    book = relationship("Book", back_populates="wishlisted_by")

    __table_args__ = (UniqueConstraint('user_id', 'book_id', name='_user_book_uc'),)
    
class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rental_date = Column(DateTime, default=datetime.now)
    return_date = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="rentals")
    user = relationship("User", back_populates="rentals")

class RentalBase(BaseModel):
    book_id: int
    user_id: int  

class RentalOut(RentalBase):
    id: int
    rental_date: datetime
    return_date: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

class AvailabilityUpdate(BaseModel):
    available: bool