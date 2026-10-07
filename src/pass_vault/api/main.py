"""
This file is the main api entrypoint
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from pass_vault.api.schemas import (
    CredentialCreate,
    CredentialResponse,
    CredentialUpdate,
    UserCreate,
    UserResponse,
)
from pass_vault.database import models
from pass_vault.database.db import Base, engine, get_db

# Create db objects if not exists
Base.metadata.create_all(bind=engine)

# Initiate fast api app
app = FastAPI(title="Pass Vault")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):

    # Check for user
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Otherwise return user
    return user


@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):

    # Check if username exists
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username exists")

    # Check if email exists
    result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    # Create user in db
    new_user = models.User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh model

    return new_user


@app.get("/api/users/{user_id}/credentials", response_model=list[CredentialResponse])
def get_user_credentials(user_id: int, db: Annotated[Session, Depends(get_db)]):

    # Check for user
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Otherwise get credentials for user
    result = db.execute(select(models.Credentials).where(models.Credentials.user_id == user_id))
    credentials = result.scalars().all()

    return credentials


@app.get("/api/users/{user_id}/credentials/{credential_id}", response_model=CredentialResponse)
def get_user_credential(user_id: int, credential_id: int, db: Annotated[Session, Depends(get_db)]):

    # Check for user
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check for user credential
    user_credential = (
        db.execute(
            select(models.Credentials).where(
                models.Credentials.user_id == user_id, models.Credentials.id == credential_id
            )
        )
        .scalars()
        .first()
    )

    if not user_credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    # Otherwise get credential for user
    return user_credential


@app.post(
    "/api/users/{user_id}/credentials",
    response_model=CredentialResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_credential(
    user_id: int, credential: CredentialCreate, db: Annotated[Session, Depends(get_db)]
):

    # Check for user
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check for existing credential
    credential_exists = (
        db.execute(
            select(models.Credentials).where(
                models.Credentials.user_id == credential.user_id,
                models.Credentials.site == credential.site,
                models.Credentials.site_username == credential.site_username,
            )
        )
        .scalars()
        .first()
    )
    if credential_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Credential for this site and username already exists",
        )

    # Otherwise add the credential
    new_credential = models.Credentials(
        user_id=user.id,
        site=credential.site,
        site_username=credential.site_username,
        site_password=credential.site_password,
        notes=credential.notes,
    )

    db.add(new_credential)
    db.commit()
    db.refresh(new_credential)

    return new_credential


@app.put("/api/users/{user_id}/credentials/{credential_id}", response_model=CredentialResponse)
def update_credential(
    user_id: int,  # TODO - dont need this change all endpoints
    credential_id: int,
    credential_data: CredentialCreate,
    db: Annotated[Session, Depends(get_db)],
):

    # Check for user
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check for user credential
    user_credential = (
        db.execute(
            select(models.Credentials).where(
                models.Credentials.user_id == user_id, models.Credentials.id == credential_id
            )
        )
        .scalars()
        .first()
    )

    if not user_credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    # Otherwise update credential for user
    return user_credential  # TODO


if __name__ == "__main__":
    pass
