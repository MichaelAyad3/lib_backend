import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Base, Book, User
from main import app, get_db

# Use a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db?check_same_thread=False"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 3}
)
Base.metadata.bind = test_engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override get_db to use test DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def test_client():
    return client

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    # Create sample user and book
    db = TestingSessionLocal()
    user = User(username="testuser")
    book = Book(id=1, title="Test Book", authors="Author A", available=True, isbn="123")
    db.add(user)
    db.add(book)
    db.commit()
    db.refresh(user)
    db.refresh(book)
    yield
    db.close()
