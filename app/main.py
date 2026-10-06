from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine
app = FastAPI()
@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok",
                "database": "connected"}
    except Exception:
        return {"status": "error",
                "database": "not connected"}
