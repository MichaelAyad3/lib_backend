# 📚 Library Backend

A FastAPI-based backend system for managing a small library, including book rentals, user management, and reporting. The task took about 7 hours, and listed possible improvements/extensions where applicable to show my consideration for these features.
---

## Tech Stack

- Python 3.x
- FastAPI
- Uvicorn

- SQLite

- SQLAlchemy
- Pydantic

- Pytest
- TestClient

---

## Specification
*MINIMUM*
- ✅ An endpoint that allows the searching by title and by author, returning books and their availability.
- ✅ Add/remove unavailable books to/from a wishlist such that they are notified when they become available
- ✅ Change the rental status (available/borrowed) for a book which should also trigger the email notifications to users with the book in their wishlist. No real email is required to be sent, the implementation could be printing the email text or logging to file.
- ✅ Generate a report on the number of books being rented and how many days they’ve been rented for.
- 🟡 The frontend of the library website displays affiliate links to copies of the book available on Amazon for each book. An endpoint is required that will update the Amazon IDs stored in the database for all the books.
- ✅ Implement unit tests. There are no specific requirements around test coverage.
  
*OPTIONAL*
- ❌ Build a simple frontend for example, a simple page of showing the user’s wishlist.
- ✅ Performance considerations around sending emails to large number of book subscribers.
- 🟡 Using the OpenLibrary API (https://openlibrary.org/dev/docs/api/search , No API key is required) to retrieve the Amazon IDs(asin) programmatically
---

## Performance Considerations

- FastAPI is lightweight and scalable. Also suitable for async/await support, for example multiple users sending requests or sending multiple emails at the same time to a list of users when a book on their wishlist becomes available.
- Using PATCH endpoints instead of PUT to only update specific fields rather than the entire entry.
- Normalised relational databases with cascading changes (e.g. on field delete), to avoid data redundancy and maintain integrity.
- Selective queries to only fetch the relevant information.

---

## 🟡 OpenLibrary API

I was unable to find any Amazon ASINs using the OpenLibrary API - I could not find this field (or anything similar). I included the amazon_id field in the books table and have written a script *(scripts/update_amazon_ids.py)* however had no luck.

---

## Endpoints

### Books

#### GET "/books"
-  Gets all useful book information - id, title, authors, availability
```http
GET /books  # get book information
```

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
  *Improvement: automatically remove the listed book from the borrowing user's wishlist*
  
#### PATCH "/rentals/{rental_id}/return"
-  Return a borrowed book
```http
PATCH /rentals/3/return  # return the 3rd rental book
```

#### GET "/rentals-report"
-  Generates a report of all books currently being rented and how long they have been rented for. Includes total number of books rented, with some other metrics. Output can be found in *rental_report.txt*
```http
GET /rentals-report  # generate rental report
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

## Running Tests

```bash
pytest
```

Tests cover core functionality including some edge cases. In order to abide by some of the spec and to simulate some features that were beyond the scope of this task, the following text files were created:

**notifications.txt**: Stores simple messages whenever a book on a user's wishlist becomes available. Created to accommodate for the automatic email functionality mentioned in the spec.

**rental_log.txt**: A text log file automatically updated whenever a user borrows or returns a book. Information includes book title, book ID, username, userID, and datetime of event.

**availability_log.txt**: Stores every event of the availability status of a book changing. Includes the endpoint that caused this change.

---

## Directory Overview

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
├── *.db                    # Databases
└── requirements.txt        # Python dependencies
```
