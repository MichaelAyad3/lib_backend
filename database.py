from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database stored locally in this file
DATABASE_URL = "sqlite:///./library.db?check_same_thread=False"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 3}  # wait 30 seconds if locked
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
