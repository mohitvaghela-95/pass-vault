from fastapi import FastAPI, HTTPException, status

from pass_vault.api.schemas import CredentialCreate, CredentialResponse

app = FastAPI(title="Pass Vault")

credentials: list[dict] = [
    {
        "id": 1,
        "site": "github.com",
        "username": "mohit",
        "password": "gh-Tr0ub4dor&3",
        "notes": "Personal account",
    },
    {
        "id": 2,
        "site": "gmail.com",
        "username": "mohitoneplus@gmail.com",
        "password": "correct-horse-battery-staple",
        "notes": "",
    },
    {
        "id": 3,
        "site": "netflix.com",
        "username": "mohit.family",
        "password": "N3tfl!x-2026",
        "notes": "Shared with family",
    },
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/credentials", response_model=list[CredentialResponse])
def get_credentials():
    return credentials


@app.post("/api/credentials", response_model=CredentialCreate)
def create_credential(credential: CredentialCreate):
    # Generate a unique ID
    new_id = max([p["id"] for p in credentials]) + 1 if credentials else 1

    # Structure the data
    new_credential = {
        "id": new_id,
        "site": credential.site,
        "username": credential.username,
        "password": credential.password,
        "notes": credential.notes,
    }

    # Add credential to database
    credentials.append(new_credential)


@app.get("/api/credentials/{credential_id}", response_model=CredentialResponse)
def get_credential(credential_id: int):
    for entry in credentials:
        if entry.get("id") == credential_id:
            return entry

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found"
    )


if __name__ == "__main__":
    pass
