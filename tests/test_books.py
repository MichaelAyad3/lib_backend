import pytest
from models import User, Book, Rental
from datetime import datetime, timedelta
from conftest import TestingSessionLocal

def test_patch_book_availability_success(test_client):
    db = TestingSessionLocal()
    book = db.query(Book).first()
    response = test_client.patch(f"/books/{book.id}/availability", json={"available": False})
    assert response.status_code == 200
    assert response.json()["message"] == f"Book '{book.title}' availability set to False"

def test_patch_book_availability_not_found(test_client):
    response = test_client.patch("/books/9999/availability", json={"available": False})
    assert response.status_code == 404

def test_patch_book_availability_missing_key(test_client):
    db = TestingSessionLocal()
    book = db.query(Book).first()
    response = test_client.patch(f"/books/{book.id}/availability", json={})
    assert response.status_code == 422  

def test_patch_book_availability_wrong_type(test_client):
    db = TestingSessionLocal()
    book = db.query(Book).first()
    response = test_client.patch(f"/books/{book.id}/availability", json={"available": "notabool"})
    assert response.status_code == 422  

def test_patch_book_availability_set_true(test_client):
    db = TestingSessionLocal()
    book = db.query(Book).first()

    # First set to False
    response_false = test_client.patch(f"/books/{book.id}/availability", json={"available": False})
    assert response_false.status_code == 200
    assert response_false.json()["message"] == f"Book '{book.title}' availability set to False"

    # Then set back to True (reactivate)
    response_true = test_client.patch(f"/books/{book.id}/availability", json={"available": True})
    assert response_true.status_code == 200
    assert response_true.json()["message"] == f"Book '{book.title}' availability set to True"

    # Confirm in DB
    db.expire_all()
    updated_book = db.query(Book).filter(Book.id == book.id).first()
    assert updated_book.available is True

def test_delete_book_currently_rented():
    db = TestingSessionLocal()
    # Cleanup
    db.query(Rental).delete()
    db.query(Book).filter(Book.isbn == "DEL456").delete()
    db.commit()

    user = db.query(User).filter_by(username="testuser").first()
    book = Book(title="BookToDeleteRented", authors="Author E", available=False, isbn="DEL456")
    db.add(book)
    db.commit()
    db.refresh(book)

    rental = Rental(book_id=book.id, user_id=user.id, rental_date=datetime.now())
    db.add(rental)
    db.commit()

    # Try deleting the book
    try:
        db.delete(book)
        db.commit()
    except Exception as e:
        db.rollback()
        assert True, f"Deletion failed as expected: {e}"
    else:
        # Check if rental still exists or if book_id is nullified
        rental_check = db.query(Rental).filter_by(book_id=book.id).first()
        assert rental_check is None, "Rental still references deleted book!"

    # Cleanup
    db.query(Rental).delete()
    db.query(Book).filter(Book.isbn == "DEL456").delete()
    db.commit()