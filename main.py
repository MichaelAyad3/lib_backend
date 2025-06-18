from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import engine, SessionLocal
from models import Base, Wishlist, Book, User, Rental, RentalBase, RentalOut, AvailabilityUpdate
from pydantic import BaseModel
from datetime import datetime
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)

# Dependency to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper Functions
def log_rental_action(action: str, book_title: str, book_id: int, username: str, user_id: int, timestamp: datetime):
    with open("rental_log.txt", "a") as file:
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
        line = f'"{book_title} (bookID: {book_id}) {action} by {username} (userID: {user_id}) on {formatted_time}."\n'
        file.write(line)
        
def notify_and_log_availability_change(book: Book, old_status: bool, db: Session, source: str):
    # Notify users if the book just became available
    if not old_status and book.available:
        wishlisted_users = (
            db.query(User)
            .join(Wishlist, Wishlist.user_id == User.id)
            .filter(Wishlist.book_id == book.id)
            .all()
        )
        notification_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open("notifications.txt", "a") as notif_file:
            for user in wishlisted_users:
                message = (
                    f"Dear {user.username}, the book '{book.title}' "
                    f"has been recently made available on {notification_time}.\n"
                )
                notif_file.write(message)

    # Log the availability change
    log_entry = (
        f"[{datetime.now().isoformat()}] "
        f"Book ID: {book.id}, Title: '{book.title}'\n"
        f"    Availability changed: {old_status} ➜ {book.available}\n"
        f"    Changed by: {source}\n"
        f"{'-'*60}\n"
    )
    with open("availability_log.txt", "a") as f:
        f.write(log_entry)

# Get all book information
@app.get("/books")
def get_all_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return [
        {
            "id": book.id,
            "title": book.title,
            "authors": book.authors,
            "available": book.available
        }
        for book in books
    ]


# Enhanced search books endpoint
@app.get("/books/search")
def search_books(
    query: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Book)

    if query:
        search = f"%{query.lower()}%"
        q = q.filter(
            Book.title.ilike(search) |
            Book.authors.ilike(search) |
            Book.isbn.ilike(search)
        )
    else:
        if title:
            q = q.filter(Book.title.ilike(f"%{title}%"))
        if author:
            q = q.filter(Book.authors.ilike(f"%{author}%"))

    results = q.all()
    return [
        {
            "id": book.id,
            "title": book.title,
            "authors": book.authors,
            "available": book.available
        }
        for book in results
    ]

# Create a user
@app.post("/users/")
def create_user(username: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}

# Add book to wishlist
@app.post("/wishlist/{user_id}/{book_id}")
def add_to_wishlist(user_id: int, book_id: int, db: Session = Depends(get_db)):
    existing = db.query(Wishlist).filter_by(user_id=user_id, book_id=book_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Book already in wishlist")

    wishlist_item = Wishlist(user_id=user_id, book_id=book_id)
    db.add(wishlist_item)
    db.commit()
    return {"message": "Book added to wishlist"}

# Get the wishlist of a user
@app.get("/wishlist/{user_id}")
def get_wishlist(user_id: int, db: Session = Depends(get_db)):
    wishlist = db.query(Wishlist).filter_by(user_id=user_id).all()
    return [
        {
            "book_id": item.book.id,
            "title": item.book.title,
            "authors": item.book.authors
        }
        for item in wishlist
    ]

# Remove a book from a wishlist
@app.delete("/wishlist/{user_id}/{book_id}")
def remove_from_wishlist(user_id: int, book_id: int, db: Session = Depends(get_db)):
    item = db.query(Wishlist).filter_by(user_id=user_id, book_id=book_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not in wishlist")
    db.delete(item)
    db.commit()
    return {"message": "Book removed from wishlist"}

# Update the availability of a book
@app.patch("/books/{book_id}/availability")
def update_book_availability(book_id: int, update: AvailabilityUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter_by(id=book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    old_status = book.available
    book.available = update.available
    db.commit()
    db.refresh(book)

    notify_and_log_availability_change(book, old_status, db, source=f"PATCH /books/{book_id}/availability")

    return {
        "message": f"Book '{book.title}' availability set to {book.available}"
    }

# Initiate the rental of a book
@app.post("/rentals", response_model=RentalOut)
def create_rental(rental: RentalBase, db: Session = Depends(get_db)):
    book = db.query(Book).filter_by(id=rental.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.available:
        raise HTTPException(status_code=400, detail="Book is already rented")

    user = db.query(User).filter_by(id=rental.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_status = book.available
    book.available = False
    rental_entry = Rental(book_id=rental.book_id, user_id=rental.user_id)
    db.add(rental_entry)
    db.commit()
    db.refresh(rental_entry)

    notify_and_log_availability_change(book, old_status, db, source="POST /rentals")

    log_rental_action(
        action="rented",
        book_title=book.title,
        book_id=book.id,
        username=user.username,
        user_id=user.id,
        timestamp=rental_entry.rental_date
    )

    return rental_entry

# Return a borrowed book
@app.patch("/rentals/{rental_id}/return")
def return_book(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter_by(id=rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental.return_date:
        raise HTTPException(status_code=400, detail="Book already returned")

    old_status = rental.book.available
    rental.return_date = datetime.now()
    rental.book.available = True
    db.commit()

    notify_and_log_availability_change(rental.book, old_status, db, source=f"PATCH /rentals/{rental_id}/return")

    user = db.query(User).filter_by(id=rental.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    log_rental_action(
        action="returned",
        book_title=rental.book.title,
        book_id=rental.book.id,
        username=user.username,
        user_id=user.id,
        timestamp=rental.return_date
    )

    return {"message": f"Book '{rental.book.title}' returned by {user.username}"}

# Create a report of all existing rented books
@app.get("/rental-report")
def rental_report(db: Session = Depends(get_db)):
    rentals = db.query(Rental).all()
    
    report_lines = []
    total_days = 0
    total_returned = 0
    still_rented = 0

    for r in rentals:
        rented_on = r.rental_date
        returned_on = r.return_date or datetime.now()
        days_rented = (returned_on - rented_on).days

        # Update summary metrics
        if r.return_date:
            total_days += days_rented
            total_returned += 1
        else:
            still_rented += 1
            # Include only currently rented in the detailed report
            report_lines.append(
                f"'{r.book.title}' rented by {r.user.username} for {days_rented} day(s)."
            )

    avg_duration = total_days // total_returned if total_returned else 0

    summary_lines = [
        f"Books Currently Rented: {still_rented}",
        f"Returned Rentals: {total_returned}",
        f"Total Rentals: {len(rentals)}",
        f"Average Rental Duration: {avg_duration} day(s)"
    ]

    report_path = "rental_report.txt"
    with open(report_path, "w") as file:
        file.write("Rental Report - Currently Rented Books\n")
        file.write("=" * 60 + "\n")
        for line in report_lines:
            file.write(line + "\n")
        file.write("\nSummary\n")
        file.write("=" * 60 + "\n")
        for line in summary_lines:
            file.write(line + "\n")

    return {
        "message": "Rental report generated",
        "report_lines": report_lines,  # only current rentals here
        "summary": summary_lines
    }

