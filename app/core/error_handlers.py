"""Centralized error handling and standardized JSON error responses."""

import logging
from typing import Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException

logger = logging.getLogger("persistent_data_layer")


def _format_pydantic_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert Pydantic validation error objects into clean, readable client dictionaries."""
    formatted: list[dict[str, Any]] = []
    for err in errors:
        loc = ".".join(str(part) for part in err.get("loc", []))
        formatted.append({
            "field": loc if loc else "unknown",
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "validation_error"),
        })
    return formatted


def register_error_handlers(app: FastAPI) -> None:
    """Register all centralized exception handlers to the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "AppException [%s]: %s (Path: %s)",
            exc.code,
            exc.message,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = _format_pydantic_errors(exc.errors())
        logger.info(
            "Validation failed for request %s %s: %s",
            request.method,
            request.url.path,
            details,
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": details,
                }
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """Handle relational database constraint violations safely without leaking credentials."""
        orig_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        logger.warning("Database IntegrityError on %s %s: %s", request.method, request.url.path, orig_msg)

        # Check for unique constraint violation
        if "unique" in orig_msg.lower():
            return JSONResponse(
                status_code=409,
                content={
                    "error": {
                        "code": "DUPLICATE_RESOURCE",
                        "message": "A resource with these unique properties already exists.",
                        "details": [],
                    }
                },
            )

        # Check for foreign key constraint violation
        if "foreign key" in orig_msg.lower():
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "FOREIGN_KEY_VIOLATION",
                        "message": "Referenced entity does not exist or operation violates relational constraints.",
                        "details": [],
                    }
                },
            )

        # Check constraint violation
        if "check" in orig_msg.lower():
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "CHECK_CONSTRAINT_VIOLATION",
                        "message": "Value violates database schema validation check constraint.",
                        "details": [],
                    }
                },
            )

        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "DATABASE_CONSTRAINT_ERROR",
                    "message": "The requested operation violates database constraints.",
                    "details": [],
                }
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle general database errors without leaking internal database structure."""
        logger.error("Database error on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "A database error occurred while processing your request.",
                    "details": [],
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code_map = {
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code,
                    "message": str(exc.detail),
                    "details": [],
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Uncaught server exception at %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected internal server error occurred",
                    "details": [],
                }
            },
        )
