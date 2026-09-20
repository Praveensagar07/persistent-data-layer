"""Main FastAPI application entrypoint."""

import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers
from app.db.base import Base
import app.models  # noqa: F401
from app.db.seed import seed_database
from app.db.session import SessionLocal, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager handling startup and teardown routines."""
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)

    # Startup: seed database with development dataset if enabled
    if settings.seed_data_on_startup:
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
    yield
    # Teardown logic
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# Persistent Data Layer REST API

Welcome to the **Persistent Data Layer** built for **Week 3 — Task 3** of the **Innovation Hacks Full Stack Development Internship**.

### Internship Roadmap
- **Week 1 (Task 1):** Frontend Developer Productivity Dashboard (React/Tailwind)
- **Week 2 (Task 2):** RESTful Backend API (Python / FastAPI / In-Memory Repository)
- **Week 3 (Task 3 - Current):** Database Integration — Persistent Data Layer (PostgreSQL / SQLAlchemy 2.x / Alembic)
- **Week 4 (Task 4):** AI-Powered Project & Task Management Platform

### Key Capabilities
- **Relational Persistence:** Robust persistent storage for Users, Projects, and Tasks with ACID transactions.
- **Relational Integrity:** Foreign key constraints, cascade deletion on projects -> tasks, and set-null reassignment on user deletion.
- **Schema-Level Validation:** Database-level CHECK constraints for statuses and priorities, UNIQUE constraints for email.
- **Dedicated Task Workflow:** Granular task lifecycle progression (`todo`, `in-progress`, `done`).
- **Standardized Envelopes:** Structured `{ "data": ... }` envelopes, paginated collections, and consistent error payloads.
- **Enterprise Error Handling:** Safe trapping of constraint violations and database errors without credential leaks.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 1. Centralized Error Handlers
register_error_handlers(app)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


# 3. Observability Middlewares (Request ID & Latency)
@app.middleware("http")
async def add_observability_headers(request: Request, call_next) -> Response:
    """Inject correlation ID and response execution time headers."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
    return response


# 4. Root & Health Endpoints
@app.get(
    "/",
    tags=["System"],
    summary="API Root Information",
    description="Provides basic metadata, version info, and navigation links.",
)
def root_info() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.api_prefix,
    }


@app.get(
    "/health",
    tags=["System"],
    summary="Health Status Check",
    description="Returns service health status, UTC timestamp, and version indicator.",
)
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.app_version,
        "environment": settings.app_env,
    }


# 5. Versioned API Router Inclusion
app.include_router(api_router, prefix=settings.api_prefix)
