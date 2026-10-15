import logging
import time

from fastapi import FastAPI, Request

from app.routers import auth, customers, loans

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Loan Application Service", version="1.0.0")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    user_id = getattr(request.state, "user_id", None)
    user_context = f"user_id={user_id}" if user_id is not None else "user_id=anonymous"

    logger.info(
        "Request completed: %s %s status=%s %s time_taken=%.4f seconds",
        request.method,
        request.url.path,
        response.status_code,
        user_context,
        process_time,
    )

    return response


app.include_router(customers.router, prefix="/api")
app.include_router(loans.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Loan Application Service is running"}
