"""
This file is responsible for setting up the database connection
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Define the DB url
SQLALCHEMY_DB_URL = "sqlite:///./vault.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DB_URL,
    connect_args={"check_same_thread": False},  # Specific to sqlite and allows for multiple threads
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # So we control commits


class Base(DeclarativeBase):
    pass


# Generator function that is called each time we make a transaction to the db and handles closing
def get_db():
    with SessionLocal() as db:
        yield db
