"""
This file is responsible for setting up the database connection
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Define the DB url
SQLALCHEMY_DB_URL = "sqlite+aiosqlite:///./vault.db"

# Create engine
engine = create_async_engine(
    SQLALCHEMY_DB_URL,
    connect_args={"check_same_thread": False},  # Specific to sqlite and allows for multiple threads
)


AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)  # So we control commits


class Base(DeclarativeBase):
    pass


# Generator function that is called to get async session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
