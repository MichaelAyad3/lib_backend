# 📚 Library Backend

A FastAPI-based backend system for managing a small library, including book rentals, user management, and reporting.

---

## Specification
*MINIMUM*
- ✅ An endpoint that allows the searching by title and by author, returning books and their availability.
- ✅ Add/remove unavailable books to/from a wishlist such that they are notified when they become available
- ✅ Change the rental status (available/borrowed) for a book which should also trigger the email notifications to users with the book in their wishlist. No real email is required to be sent, the implementation could be printing the email text or logging to file.
- ✅ Generate a report on the number of books being rented and how many days they’ve been rented for.
- ❌ The frontend of the library website displays affiliate links to copies of the book available on Amazon for each book. An endpoint is required that will update the Amazon IDs stored in the database for all the books.
- ✅ Implement unit tests. There are no specific requirements around test coverage.
  
*OPTIONAL*
- ❓ Build a simple frontend for example, a simple page of showing the user’s wishlist.
- ✅ Performance considerations around sending emails to large number of book subscribers.
- ❓ Using the OpenLibrary API (https://openlibrary.org/dev/docs/api/search , No API key is required) to retrieve the Amazon IDs(asin) programmatically
---

## Endpoints

### Books

#### GET "/books"
-  Gets all useful book information - id, title, authors, availability

#### GET "/books/search"
-  Searches for books by title or author, or both.
```http
GET /books/search?title=the hobbit         # by title
GET /books/search?author=george orwell     # by author
GET /books/search?title=1984&author=orwell # by title and author
```

#### PATCH "/books/{book_id}/availability"
-  Manually update the availability of a book. Useful for testing or for library staff to make changes
```http
PATCH /books/34/0  # set book 34 to unavailable
```

#### POST "/users"
-  Creates a new user
```http
POST /users/?username=johndoe  # create user johndoe
```

#### POST "/wishlist/{user_id}/{book_id}"
-  Adds a book to the wishlist of a user
```http
POST /wishlist/12/34  # add book 34 to user 12's wishlist
```
  *Improvement: using a logged in user's details after authentication (e.g. JWT) to omit user_id from the endpoint*
  
#### GET "/wishlist/{user_id}/"
-  Retrieve's a user's wishlist
```http
GET /wishlist/12  # get the wishlist of user 12
```
  *Improvement: using a logged in user's details after authentication (e.g. JWT) to omit user_id from the endpoint*

#### DELETE "/wishlist/{user_id}/{book_id}"
-  Remove a book from a user's wishlist
```http
DELETE /wishlist/12/34  # remove book 34 from user 12's wishlist
```
  *Improvement: using a logged in user's details after authentication (e.g. JWT) to omit user_id from the endpoint*
  
#### POST "/rentals"
-  Initiate the rental of a book. Parameters are within the request body. Takes a user_id and book_id
```http
POST /rentals
```
---

## Setup Instructions

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

The databases have already been included with sample data, however scripts to upload books and users are included if interested.

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
