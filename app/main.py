import logging
import time

from fastapi import FastAPI, Request

from app.base import Base
from app.database import engine
from app.routers import customers, loans

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


app = FastAPI(title="Loan Application Service", version="1.0.0")


# Create tables
Base.metadata.create_all(bind=engine)


# Middleware logging
@app.middleware("http")
async def log_requests(request: Request, call_next):

    start_time = time.time()

    logger.info(f"Request started: {request.method} {request.url.path}")

    response = await call_next(request)

    end_time = time.time()

    process_time = end_time - start_time

    logger.info(
        f"Request completed: {response.status_code} "
        f"Time taken: {process_time:.4f} seconds"
    )

    return response


# Routers
app.include_router(customers.router, prefix="/api")

app.include_router(loans.router, prefix="/api")


@app.get("/")
def root():

    return {"message": "Loan Application Service is running"}
