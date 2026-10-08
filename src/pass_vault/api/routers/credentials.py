from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pass_vault.api.schemas import (
    CredentialCreate,
    CredentialResponse,
    CredentialUpdate,
)
from pass_vault.database import models
from pass_vault.database.db import get_db

router = APIRouter()


@router.get("", response_model=list[CredentialResponse])
async def get_all_credentials(db: Annotated[AsyncSession, Depends(get_db)]):

    # Get credentials for user
    result = await db.execute(
        select(models.Credentials).options(selectinload(models.Credentials.user))
    )
    credentials = result.scalars().all()

    return credentials


@router.get("/u/{user_id}", response_model=list[CredentialResponse])
async def get_user_credentials(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    # Check for user
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Otherwise get credentials for user
    result = await db.execute(
        select(models.Credentials)
        .options(selectinload(models.Credentials.user))
        .where(models.Credentials.user_id == user_id)
    )
    credentials = result.scalars().all()

    return credentials


@router.get("/{credential_id}/u/{user_id}", response_model=CredentialResponse)
async def get_user_credential(
    user_id: int, credential_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):

    # Check for user
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check for user credential
    result = await db.execute(
        select(models.Credentials)
        .options(selectinload(models.Credentials.user))
        .where(models.Credentials.user_id == user_id, models.Credentials.id == credential_id)
    )

    user_credential = result.scalars().first()

    if not user_credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    # Otherwise get credential for user
    return user_credential


@router.post(
    "/u/{user_id}",
    response_model=CredentialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_credential(
    user_id: int, credential: CredentialCreate, db: Annotated[AsyncSession, Depends(get_db)]
):

    # Check for user
    result = await db.execute(select(models.User).where(models.User.id == credential.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check for existing credential
    result = await db.execute(
        select(models.Credentials).where(
            models.Credentials.user_id == credential.user_id,
            models.Credentials.site == credential.site,
            models.Credentials.site_username == credential.site_username,
        )
    )
    credential_exists = result.scalars().first()

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
    await db.commit()
    await db.refresh(new_credential, attribute_names=["user"])

    return new_credential


@router.put("/{credential_id}/u/{user_id}", response_model=CredentialResponse)
async def update_credential(
    user_id: int,  # TODO - dont need this change all endpoints
    credential_id: int,
    credential_data: CredentialCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Check for user credential specific to the user
    result = await db.execute(
        select(models.Credentials).where(
            models.Credentials.user_id == credential_data.user_id,
            models.Credentials.id == credential_id,
        )
    )
    user_credential = result.scalars().first()

    if not user_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential for user not found"
        )

    # Otherwise update credential for user
    user_credential.site = credential_data.site
    user_credential.site_username = credential_data.site_username
    user_credential.site_password = credential_data.site_password
    user_credential.notes = credential_data.notes

    await db.commit()
    await db.refresh(user_credential, attribute_names=["user"])

    # Return new credential
    return user_credential


@router.patch("/{credential_id}/u/{user_id}", response_model=CredentialResponse)
async def patch_credential(
    user_id: int,  # TODO - dont need this change all endpoints
    credential_id: int,
    credential_data: CredentialUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Check for user credential specific to the user
    result = await db.execute(
        select(models.Credentials).where(
            models.Credentials.user_id == credential_data.user_id,
            models.Credentials.id == credential_id,
        )
    )
    user_credential = result.scalars().first()

    if not user_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential for user not found"
        )

    # Otherwise update credential for user
    update_data = credential_data.model_dump(
        exclude_unset=True
    )  # Get all the fields that have been specifically set

    for item, value in update_data.items():
        setattr(user_credential, item, value)  # Set value for each given attribute

    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Site and username combination exist"
        )  # Check that site and username follows unique key constraint

    await db.refresh(user_credential, attribute_names=["user"])

    # Return new credential
    return user_credential


@router.delete("/{credential_id}/u/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    user_id: int,  # TODO - dont need this change all endpoints
    credential_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Check for user credential specific to the user
    result = await db.execute(
        select(models.Credentials).where(
            models.Credentials.user_id == user_id,
            models.Credentials.id == credential_id,
        )
    )
    user_credential = result.scalars().first()

    if not user_credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential for user not found"
        )

    # Otherwise delete credential for user
    await db.delete(user_credential)
    await db.commit()
