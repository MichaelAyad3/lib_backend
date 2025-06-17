import csv
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Book


def load_books_from_csv(csv_path: str):
    db: Session = SessionLocal()

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        
        for row in reader:
            if db.query(Book).filter_by(id=int(row['Id'])).first():
                continue  # Skip if book already exists

            book = Book(
                id=int(row['Id']),
                isbn=row['ISBN'],
                authors=row['Authors'],
                publication_year=int(row['Publication Year']),
                title=row['Title'],
                language=row['Language']
            )
            db.add(book)
        db.commit()

        db.close()
        print("Books imported successfully.")

if __name__ == "__main__":
    load_books_from_csv("books.csv") 
