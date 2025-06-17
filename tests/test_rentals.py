import pytest
from models import User, Book, Rental
from datetime import datetime, timedelta
from conftest import TestingSessionLocal

def test_create_rental_success(test_client):
    db = TestingSessionLocal()
    user = db.query(User).filter_by(username="testuser").first()
    book = Book(title="Available Book", authors="Author B", available=True, isbn="321")
    db.add(book)
    db.commit()
    db.refresh(book)

    response = test_client.post("/rentals", json={"book_id": book.id, "user_id": user.id})
    assert response.status_code == 200
    assert response.json()["book_id"] == book.id

def test_create_rental_book_not_found(test_client):
    db = TestingSessionLocal()
    user = db.query(User).filter_by(username="testuser").first()
    response = test_client.post("/rentals", json={"book_id": 9999, "user_id": user.id})
    assert response.status_code == 404

def test_create_rental_user_not_found(test_client):
    db = TestingSessionLocal()
    book = Book(title="Test Book", authors="Author A", available=True, isbn="4567")
    db.add(book)
    db.commit()
    db.refresh(book)
    book = db.query(Book).filter_by(available=1).first()
    print("Book available:", book.available, "Type:", type(book.available))
    assert book is not None, "Need at least one available book for this test"
    
    response = test_client.post("/rentals", json={"book_id": book.id, "user_id": 99999})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_rental_book_unavailable(test_client):
    db = TestingSessionLocal()
    book = Book(title="Unavailable Book", authors="Author C", available=False, isbn="456")
    db.add(book)
    db.commit()
    db.refresh(book)

    user = db.query(User).filter_by(id=1).first()
    response = test_client.post("/rentals", json={"book_id": book.id, "user_id": user.id})
    assert response.status_code == 400
    assert response.json()["detail"] == "Book is already rented"

def test_return_rental_success(test_client):
    db = TestingSessionLocal()
    book = Book(title="To Be Returned", authors="Author D", available=True, isbn="555")
    user = db.query(User).filter_by(id=1).first()
    db.add(book)
    db.commit()
    db.refresh(book)

    # Create rental
    rental = Rental(book_id=book.id, user_id=user.id, rental_date=datetime.now() - timedelta(days=3))
    book.available = False
    db.add(rental)
    db.commit()
    db.refresh(rental)

    response = test_client.patch(f"/rentals/{rental.id}/return")
    assert response.status_code == 200
    assert "returned by" in response.json()["message"]

def test_return_rental_not_found(test_client):
    response = test_client.patch("/rentals/9999/return")
    assert response.status_code == 404

def test_return_rental_already_returned(test_client):
    db = TestingSessionLocal()
    rental = db.query(Rental).filter(Rental.return_date.isnot(None)).first()
    if not rental:
        # fallback: create one
        rental = Rental(book_id=1, user_id=1, return_date=datetime.now())
        db.add(rental)
        db.commit()
        db.refresh(rental)

    response = test_client.patch(f"/rentals/{rental.id}/return")
    assert response.status_code == 400
    
def test_create_rental_missing_book_id(test_client):
    db = TestingSessionLocal()
    user = db.query(User).filter_by(username="testuser").first()
    response = test_client.post("/rentals", json={"user_id": user.id}) 
    assert response.status_code == 422

def test_create_rental_missing_user_id(test_client):
    db = TestingSessionLocal()
    book = Book(title="Available Book 2", authors="Author X", available=True, isbn="999")
    db.add(book)
    db.commit()
    db.refresh(book)

    response = test_client.post("/rentals", json={"book_id": book.id}) 
    assert response.status_code == 422

def test_create_rental_user_and_book_not_found(test_client):
    response = test_client.post("/rentals", json={"book_id": 99999, "user_id": 99999})
    assert response.status_code == 404

def test_create_rental_after_return(test_client):
    db = TestingSessionLocal()

    # Create and rent book
    book = Book(title="Book to Rent Again", authors="Author Y", available=True, isbn="777")
    db.add(book)
    db.commit()
    db.refresh(book)

    user = db.query(User).filter_by(username="testuser").first()

    # Rent it
    response1 = test_client.post("/rentals", json={"book_id": book.id, "user_id": user.id})
    assert response1.status_code == 200

    # Return it
    rental_id = response1.json()["id"]
    response_return = test_client.patch(f"/rentals/{rental_id}/return")
    assert response_return.status_code == 200

    # Rent again
    response2 = test_client.post("/rentals", json={"book_id": book.id, "user_id": user.id})
    assert response2.status_code == 200

def test_delete_user_with_active_rentals():
    db = TestingSessionLocal()
    # Clear relevant tables
    db.query(Rental).delete()
    db.query(User).filter(User.username == "user_to_delete").delete()
    db.commit()

    # Setup user and book
    user = User(username="user_to_delete")
    book = Book(title="BookForUserDeletion", authors="Author D", available=True, isbn="DEL123")
    db.add_all([user, book])
    db.commit()
    db.refresh(user)
    db.refresh(book)

    # Create active rental
    rental = Rental(book_id=book.id, user_id=user.id, rental_date=datetime.now())
    book.available = False
    db.add(rental)
    db.commit()

    # Try deleting user
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        assert True, f"Deletion failed as expected: {e}"
    else:
        # If deletion succeeds, check rental still exists or not
        active_rental = db.query(Rental).filter_by(user_id=user.id).first()
        assert active_rental is None or active_rental.user_id != user.id, "Rental still linked to deleted user!"

    # Clean up
    db.query(Rental).delete()
    db.query(Book).filter(Book.isbn == "DEL123").delete()
    db.query(User).filter(User.username == "user_to_delete").delete()
    db.commit()