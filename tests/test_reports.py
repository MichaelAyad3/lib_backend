import pytest
from models import User, Book, Rental
from datetime import datetime, timedelta
from conftest import TestingSessionLocal

def test_rental_report(test_client):
    response = test_client.get("/rental-report")
    assert response.status_code == 200
    assert "summary" in response.json()

def test_rental_report_empty_db(test_client):
    db = TestingSessionLocal()
    db.query(Rental).delete()
    db.commit()

    response = test_client.get("/rental-report")
    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert data["message"] == "Rental report generated"
    assert data["report_lines"] == []
    # summary should show zero counts
    assert "Books Currently Rented: 0" in data["summary"]
    assert "Returned Rentals: 0" in data["summary"]
    assert "Total Rentals: 0" in data["summary"]
    assert "Average Rental Duration: 0 day(s)" in data["summary"]


def test_rental_report_only_returned(test_client):
    db = TestingSessionLocal()
    db.query(Rental).delete()
    db.query(Book).filter(Book.isbn == "999").delete()
    db.commit()

    user = db.query(User).filter_by(username="testuser").first()
    book = Book(title="Returned Book", authors="Author Z", available=True, isbn="999")
    db.add(book)
    db.commit()
    db.refresh(book)

    rental = Rental(
        book_id=book.id,
        user_id=user.id,
        rental_date=datetime.now() - timedelta(days=5),
        return_date=datetime.now() - timedelta(days=1),
    )
    db.add(rental)
    db.commit()

    response = test_client.get("/rental-report")
    assert response.status_code == 200
    data = response.json()

    assert data["report_lines"] == []  # no active rentals
    assert any("Returned Rentals: 1" in s for s in data["summary"])
    assert any("Books Currently Rented: 0" in s for s in data["summary"])


def test_rental_report_with_active_rentals(test_client):
    db = TestingSessionLocal()
    db.query(Rental).delete()
    db.commit()

    user = db.query(User).filter_by(username="testuser").first()
    book = Book(title="Active Rental Book", authors="Author A", available=False, isbn="888")
    db.add(book)
    db.commit()
    db.refresh(book)

    rental = Rental(
        book_id=book.id,
        user_id=user.id,
        rental_date=datetime.now() - timedelta(days=3),
        return_date=None,
    )
    db.add(rental)
    db.commit()

    response = test_client.get("/rental-report")
    assert response.status_code == 200
    data = response.json()

    assert len(data["report_lines"]) == 1
    assert any("Books Currently Rented: 1" in s for s in data["summary"])
    assert any("Returned Rentals: 0" in s for s in data["summary"])