import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


# ============================================================
# HTTP EXCEPTION HANDLER
# ============================================================

async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "http_error",
                "message": exc.detail,
            },
        },
    )


# ============================================================
# SQLALCHEMY EXCEPTION HANDLER
# ============================================================

async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    logger.exception(
        "Database error occurred while processing %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": "database_error",
                "message": "A database error occurred.",
            },
        },
    )


# ============================================================
# GENERAL EXCEPTION HANDLER
# ============================================================

async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception while processing %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": "internal_server_error",
                "message": "An unexpected error occurred.",
            },
        },
    )