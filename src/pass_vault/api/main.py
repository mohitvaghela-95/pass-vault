"""
This file is the main api entrypoint
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from pass_vault.api.routers import credentials, users
from pass_vault.database.db import Base, engine


# Create db objects if not exists
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # Application runs

    # Shutdown
    await engine.dispose()


# Initiate fast api app
app = FastAPI(title="Pass Vault", lifespan=lifespan)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(credentials.router, prefix="/api/credentials", tags=["credentials"])


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    pass
