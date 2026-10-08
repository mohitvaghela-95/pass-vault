from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pass_vault.api.schemas import (
    CredentialCreate,
    CredentialResponse,
    CredentialUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from pass_vault.database import models
from pass_vault.database.db import Base, engine, get_db

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(models.User))
    users = result.scalars().all()

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    # Check for user
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Otherwise return user
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):

    # Check if username exists
    result = await db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username exists")

    # Check if email exists
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    # Create user in db
    new_user = models.User(username=user.username, email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  # Refresh model

    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_data: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):

    # Check for user
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if username or email taken
    # Filter based on what is passed
    conditions = []
    if user_data.username is not None:
        conditions.append(models.User.username == user_data.username)
    if user_data.email is not None:
        conditions.append(models.User.email == user_data.email)

    if conditions:
        result = await db.execute(select(models.User).where(or_(*conditions)))
        found = result.scalars().first()
        if found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and/or username exists",
            )

    updated_fields = user_data.model_dump(exclude_unset=True)
    for col, value in updated_fields.items():
        setattr(user, col, value)

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,  # TODO - dont need this change all endpoints
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Check for user credential specific to the user
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Otherwise delete user
    await db.delete(user)
    await db.commit()
