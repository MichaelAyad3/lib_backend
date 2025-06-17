# 📚 Library Backend

A FastAPI-based backend system for managing a small library, including book rentals, user management, and reporting.

---

## 🚀 Features

- Search and manage books
- Track user rentals
- Automatic rental and availability logging
- Wishlist notifications (via logs)
- Testing suite with pytest

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/MichaelAyad3/lib_backend.git
cd lib_backend
```

### 2. Create & Activate a Virtual Environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# .\venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database

```bash
# Optional: delete existing DB if you'd like a fresh start
rm library.db test.db

# Run the script to import books and users
python scripts/import_books.py
python scripts/import_users.py
```

### 5. Run the App

```bash
uvicorn main:app --reload
```

API will be available at:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)  
Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ✅ Running Tests

```bash
pytest
```

You can view rental logs and notification outputs in:
- `rental_log.txt`
- `availability_log.txt`
- `notifications.txt`

---

## 📁 Directory Overview

```
lib_backend/
│
├── main.py                 # FastAPI entry point
├── models.py               # SQLAlchemy models
├── database.py             # DB connection logic
├── books.csv               # Initial book data
├── scripts/                # Utility scripts for import
├── tests/                  # Pytest test suite
├── *.txt                   # Output logs and reports
└── requirements.txt        # Python dependencies
```
