"""
This file contains the database models for sqlalchemy
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pass_vault.database.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    credentials: Mapped[list[Credentials]] = relationship(
        "Credentials", back_populates="user", cascade="all, delete-orphan"
    )


class Credentials(Base):
    __tablename__ = "credentials"
    __table_args__ = (UniqueConstraint("user_id", "site", "site_username", name="uix_site_usr"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    site: Mapped[str] = mapped_column(String(1000), nullable=False)
    site_username: Mapped[str] = mapped_column(String(120), nullable=False)
    site_password: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True, default="")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    date_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    user: Mapped[User] = relationship("User", back_populates="credentials")
