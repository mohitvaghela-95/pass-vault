"""
This file stores the pydantic models for our expected requests and responses for api validation
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(
        max_length=120
    )  # Dont need min len because EmailStr validates not empty


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    # TODO: email is sent back which is a privacy risk, create public and private responses
    id: int


class CredentialBase(BaseModel):
    site: str = Field(max_length=150, min_length=1)
    site_username: str = Field(max_length=120, min_length=1)
    site_password: str = Field(max_length=120, min_length=1)
    notes: str = Field(default="")


class CredentialCreate(CredentialBase):
    user_id: int  # TODO - TEMPORARY - get user from session auth


class CredentialUpdate(BaseModel):
    site: str | None = Field(default=None, max_length=150, min_length=1)
    site_username: str | None = Field(default=None, max_length=120, min_length=1)
    site_password: str | None = Field(default=None, max_length=120, min_length=1)
    notes: str | None = Field(default=None)
    user_id: int


class CredentialResponse(CredentialBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_created: datetime
    user: UserResponse
