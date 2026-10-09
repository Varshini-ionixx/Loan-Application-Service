from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({"field": error["loc"][-1], "message": error["msg"]})
    return JSONResponse(
        status_code=400,
        content={"status": 400, "detail": "validation failed", "errors": errors},
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": 500, "detail": "Internal Server Error."},
    )
