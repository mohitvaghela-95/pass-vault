from fastapi import FastAPI

app = FastAPI(title="Pass Vault")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    pass
