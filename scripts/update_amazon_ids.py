from sqlalchemy.orm import Session
from models import Book
from database import Base, SessionLocal
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fetch_amazon_asin(title: str, author: str):
    query = f"https://openlibrary.org/search.json?title={title}&author={author}"
    response = requests.get(query)
    if response.status_code != 200:
        print(f"Failed to fetch data for {title} by {author}")
        return None
    
    data = response.json()
    docs = data.get('docs', [])
    
    if not docs:
        print(f"No docs found for {title} by {author}")
        return None
    
    for doc in docs:
        print(f"Checking doc: {doc}") 
        identifiers = doc.get('identifier') or {}
        if 'amazon' in identifiers:
            return identifiers['amazon'][0]
        if 'asin' in identifiers:
            return identifiers['asin'][0]
    print(f"No ASIN found for {title} by {author}")
    return None


def update_books_amazon_id():
    db: Session = SessionLocal()
    try:
        books = db.query(Book).filter(Book.amazon_id == None).all()
        for book in books:
            asin = fetch_amazon_asin(book.title, book.authors)
            if asin:
                book.amazon_id = asin
                db.add(book)
                print(f"Updated {book.title} with Amazon ASIN: {asin}")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    update_books_amazon_id()
