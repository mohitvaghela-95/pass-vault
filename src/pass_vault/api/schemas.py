from pydantic import BaseModel, ConfigDict, Field


class CredentialBase(BaseModel):
    site: str = Field(max_length=150, min_length=1)
    username: str = Field(max_length=150, min_length=1)
    password: str = Field(max_length=150, min_length=1)
    notes: str = Field(max_length=2000, default="")


class CredentialCreate(CredentialBase):
    pass


class CredentialResponse(CredentialBase):
    model_config = ConfigDict(from_attributes=True)
