import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import User


db = SessionLocal()
db.add_all([
    User(username="alice"),
    User(username="bob"),
])
db.commit()
db.close()
