# Persistent Data Layer

## Overview

**Persistent Data Layer** is the official **Week 3 / Task 3** milestone of the **Innovation Hacks Full Stack Development Internship**.

This project establishes an enterprise-grade relational database architecture extending the Week 2 REST API. In-memory data collections have been completely replaced with a persistent, transactional database layer using **PostgreSQL**, **SQLAlchemy 2.x**, and **Alembic**, providing ACID guarantees, database-level schema constraints, cascade relationship policies, database migrations, connection pooling, and secure environment configuration.

---

## Week 3 Internship Objective

The objective of Week 3 is to integrate a **real relational database** into the REST API so that User, Project, and Task data persist reliably across service lifecycles, with relationships modeled intentionally, validation enforced at both the API and database levels, and credentials handled securely through environment variables.

This project serves as the production-ready backend and persistent database foundation for **Week 4: AI-Powered Project & Task Management Platform**.

### Critical Task 3 Requirements
- **User Data Storage:** Persistent user accounts with unique email addresses and role assignments.
- **Project Data Storage:** Persistent project initiatives linked to user owners.
- **Task Data Storage:** Persistent work items linked to projects and assigned users.
- **Full CRUD Operations:** Complete Create, Read, Update, Delete across all entities.
- **Schema-Level Validation:** Database constraints (CHECK, NOT NULL, UNIQUE, FOREIGN KEY) in addition to API payload validation.
- **Relational Integrity:** Foreign key constraints with defined deletion semantics (cascade on project deletion; set-null on user deletion).
- **Secure Configuration:** Zero hard-coded credentials; 100% environment-driven settings.

---

## Features

- **Relational Data Persistence:** Full ACID transactions across PostgreSQL and SQLite.
- **Relational Integrity & Foreign Keys:**
  - `users` $1 \to N$ `projects` (owns; cascade on delete)
  - `projects` $1 \to N$ `tasks` (contains; cascade on delete)
  - `users` $1 \to N$ `tasks` (assigned; set null on delete)
- **Schema-Level Validation:**
  - `UNIQUE` constraint on user email with case-insensitive normalization.
  - Database `CHECK` constraint on project status (`planning`, `active`, `completed`, `archived`).
  - Database `CHECK` constraint on project priority (`low`, `medium`, `high`, `critical`).
  - Database `CHECK` constraint on task status (`todo`, `in-progress`, `done`).
  - Database `CHECK` constraint on task priority (`low`, `medium`, `high`, `critical`).
- **Complete CRUD Endpoints:** Full Create, Read, Update, Delete across Users, Projects, and Tasks.
- **Dedicated Task Workflow:** Dedicated `/tasks/{id}/status` endpoint for granular lifecycle progression (`todo` $\to$ `in-progress` $\to$ `done`).
- **Filtering & Pagination:** Query tasks by `status`, `priority`, `project_id`, `assignee_id`; query projects by `owner_id`, `status`; query users by `role`.
- **Database Migrations:** Reproducible schema migrations managed via Alembic.
- **Connection Management:** Connection pooling with `pool_pre_ping=True`, request-scoped transactional sessions, and automatic rollback on failure.
- **Enterprise Error Handling:** Standardized `{ "error": { "code", "message", "details" } }` envelopes without credential or stack trace leaks.
- **Zero-Credential Security:** Pure environment-based configuration; `.env.example` contains placeholders only.
- **Interactive API Documentation:** Auto-generated Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## Architecture

The official multi-tier architecture is structured as follows:

$$\text{Frontend} \longrightarrow \text{REST API (FastAPI)} \longrightarrow \text{Backend (Repositories/Services)} \longrightarrow \text{Database (PostgreSQL / SQLite)}$$

### Layered Separation of Concerns
```
app/
├── core/              # Environment config, custom exceptions, error handlers
├── db/                # Engine, connection pooling, transactional session, declarative base
├── models/            # SQLAlchemy 2.0 relational domain models (users, projects, tasks)
├── schemas/           # Pydantic v2 schemas for request validation & response envelopes
├── repositories/      # Data access layer executing SQLAlchemy queries
├── services/          # Business logic orchestrating invariants and relational checks
├── api/
│   ├── routes/        # RESTful API route endpoints (/users, /projects, /tasks)
│   └── router.py      # Versioned router aggregator (/api/v1)
├── utils/             # Unique prefixed ID generators (usr_, prj_, tsk_)
└── main.py            # FastAPI lifespan, CORS, error handling, observability
alembic/               # Database versioning and automated schema migrations
scripts/               # Standalone 10-step persistence verification suite
tests/                 # Pytest test suites (CRUD, constraints, relationships, persistence)
```

---

## Tech Stack

- **Language:** Python 3.14+ (Python 3.10+ supported)
- **API Framework:** FastAPI 0.110+
- **ORM / Database Toolkit:** SQLAlchemy 2.0+ (Declarative Mappings, Typed Queries)
- **Database Driver:** `psycopg` (psycopg 3 binary driver for PostgreSQL)
- **Migrations:** Alembic 1.13+
- **Data Validation & Serialization:** Pydantic v2 (ConfigDict, field validators)
- **ASGI Web Server:** Uvicorn (standard async event loop)
- **Testing Suite:** Pytest 8+, HTTPX, TestClient

---

## Database Schema

### Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : "owns (1:N, cascade delete)"
    USERS ||--o{ TASKS : "assigned (1:N, set null on delete)"
    PROJECTS ||--o{ TASKS : "contains (1:N, cascade delete)"

    USERS {
        string id PK "usr_... (String 64)"
        string name "not null, 1-100 chars"
        string email UK "not null, unique index"
        string role "not null, default 'developer'"
        timestamp created_at "not null, timezone-aware"
        timestamp updated_at "not null, timezone-aware"
    }

    PROJECTS {
        string id PK "prj_... (String 64)"
        string owner_id FK "users.id, not null, indexed"
        string name "not null, 1-120 chars"
        string description "nullable, up to 1000 chars"
        string status "planning | active | completed | archived"
        string priority "low | medium | high | critical"
        timestamp created_at "not null, timezone-aware"
        timestamp updated_at "not null, timezone-aware"
    }

    TASKS {
        string id PK "tsk_... (String 64)"
        string project_id FK "projects.id, not null, indexed"
        string assignee_id FK "users.id, nullable, indexed"
        string title "not null, 1-150 chars"
        string description "nullable, up to 2000 chars"
        string status "todo | in-progress | done"
        string priority "low | medium | high | critical"
        timestamp due_date "nullable, timezone-aware"
        timestamp created_at "not null, timezone-aware"
        timestamp updated_at "not null, timezone-aware"
    }
```

### Relational Deletion Semantics
- **Project Deletion:** When a project is removed, its child tasks are automatically deleted (`ondelete="CASCADE"`). Tasks cannot exist without their parent project.
- **User Deletion (Owned Projects):** When a user is deleted, their personal projects are cascade-deleted (`ondelete="CASCADE"`), preventing invalid orphan projects.
- **User Deletion (Assigned Tasks):** When an assignee user is deleted, any assigned tasks remain intact under their project, and `Task.assignee_id` is safely set to `NULL` (`ondelete="SET NULL"`). This protects historical task records from accidental loss.

---

## API Endpoints

### Users (`/api/v1/users`)
| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/api/v1/users` | Create user with unique email validation | 201 Created |
| `GET` | `/api/v1/users` | List users with pagination and role filter | 200 OK |
| `GET` | `/api/v1/users/{id}` | Get user by unique ID | 200 OK |
| `PATCH` | `/api/v1/users/{id}` | Update user name, email, or role | 200 OK |
| `DELETE` | `/api/v1/users/{id}` | Delete user (cascades owned projects; unassigns tasks) | 200 OK |

### Projects (`/api/v1/projects`)
| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/api/v1/projects` | Create project (validates owner exists) | 201 Created |
| `GET` | `/api/v1/projects` | List projects with owner/status filtering | 200 OK |
| `GET` | `/api/v1/projects/{id}` | Get project by unique ID | 200 OK |
| `PATCH` | `/api/v1/projects/{id}` | Update project metadata or transfer owner | 200 OK |
| `DELETE` | `/api/v1/projects/{id}` | Delete project (cascades to all child tasks) | 200 OK |

### Tasks (`/api/v1/tasks`)
| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/api/v1/tasks` | Create task attached to project & optional assignee | 201 Created |
| `GET` | `/api/v1/tasks` | List tasks with multi-field filters & pagination | 200 OK |
| `GET` | `/api/v1/tasks/{id}` | Get full task details by ID | 200 OK |
| `PATCH` | `/api/v1/tasks/{id}` | Update task title, description, due date, priority | 200 OK |
| `PATCH` | `/api/v1/tasks/{id}/status` | Dedicated lifecycle status update (`todo`, `in-progress`, `done`) | 200 OK |
| `DELETE` | `/api/v1/tasks/{id}` | Delete task by ID | 200 OK |

---

## Database Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Configure your `DATABASE_URL` for PostgreSQL:
   ```ini
   DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/developer_productivity
   ```
3. Run Alembic migrations to construct the database schema:
   ```bash
   python -m alembic upgrade head
   ```

---

## Environment Variables

| Variable | Default Value | Description |
|---|---|---|
| `APP_NAME` | `Persistent Data Layer` | Display name of the application |
| `APP_ENV` | `development` | Environment name (`development`, `staging`, `production`) |
| `APP_VERSION` | `1.0.0` | Semantic version identifier |
| `DEBUG` | `true` | Debug mode toggle |
| `API_PREFIX` | `/api/v1` | URL route prefix for REST endpoints |
| `HOST` | `0.0.0.0` | ASGI bind interface |
| `PORT` | `8000` | ASGI bind port |
| `DATABASE_URL` | `postgresql+psycopg://username:password@localhost:5432/developer_productivity` | Database connection URI |
| `DB_POOL_SIZE` | `10` | SQLAlchemy connection pool size |
| `DB_MAX_OVERFLOW` | `20` | Max overflow connections allowed |
| `DB_POOL_TIMEOUT` | `30` | Connection pool wait timeout (seconds) |
| `DB_POOL_PRE_PING` | `true` | Test connection liveness before checking out |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed CORS origins |
| `SEED_DATA_ON_STARTUP` | `true` | Auto-populate development seed records if DB is empty |

> [!NOTE]
> Never commit real database passwords or credentials to version control. The repository `.gitignore` strictly excludes `.env` and all database files.

---

## Alembic Migrations

Migrations are managed with Alembic for full version control and schema reproducibility:

- **Apply all migrations:**
  ```bash
  python -m alembic upgrade head
  ```
- **Rollback one migration:**
  ```bash
  python -m alembic downgrade -1
  ```
- **Create a new migration:**
  ```bash
  python -m alembic revision --autogenerate -m "description_of_change"
  ```

---

## Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Praveensagar07/persistent-data-layer.git
   cd persistent-data-layer
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the API

Start the FastAPI application with Uvicorn:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

When started, the API exposes:
- **API Root:** [http://localhost:8000/](http://localhost:8000/)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Running Tests

Run the complete 36-test automated test suite:
```bash
python -m pytest -v
```

Or for concise output:
```bash
python -m pytest -q
```

### Official 10-Step Persistence Verification Test
Verify actual cold-restart persistence across complete process/engine shutdown:
```bash
python scripts/verify_persistence.py
```

---

## PostgreSQL Setup

### Creating PostgreSQL Database
Connect to your local or hosted PostgreSQL instance via `psql`:
```sql
-- Connect to PostgreSQL CLI
psql -U postgres

-- Create dedicated database
CREATE DATABASE developer_productivity;

-- Grant permissions if using dedicated user
GRANT ALL PRIVILEGES ON DATABASE developer_productivity TO postgres;
```

Update your `.env` file:
```ini
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/developer_productivity
```

Then run the initial migration:
```bash
python -m alembic upgrade head
```

---

## Deployment

The application is container-ready and configured for production deployment on platforms such as Render, Railway, AWS ECS, or Fly.io:

1. **Procfile / Start Command:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
2. **Environment Variables:** Set `DATABASE_URL` to your managed PostgreSQL connection URI (e.g., Supabase, Neon, AWS RDS, or Render PostgreSQL).
3. **Release Command:** Execute database migrations automatically before booting:
   ```bash
   alembic upgrade head
   ```

---

## Project Structure

```
persistent-data-layer/
├── alembic.ini                   # Alembic configuration
├── alembic/                      # Database migrations
│   ├── env.py                    # Migration environment runner
│   ├── script.py.mako            # Migration template
│   └── versions/
│       └── 001_initial_schema.py # Initial relational schema migration
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entrypoint, lifespan, middlewares
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py             # Versioned router aggregator
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── users.py          # User CRUD routes (/api/v1/users)
│   │       ├── projects.py       # Project CRUD routes (/api/v1/projects)
│   │       └── tasks.py          # Task CRUD routes (/api/v1/tasks)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Environment configuration and settings
│   │   ├── error_handlers.py     # Centralized exception handlers
│   │   └── exceptions.py         # Custom domain exceptions
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py               # DeclarativeBase definition
│   │   ├── seed.py               # Development dataset seeder
│   │   └── session.py            # Engine, pooling, and get_db session dependency
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py               # User SQLAlchemy model
│   │   ├── project.py            # Project SQLAlchemy model
│   │   └── task.py               # Task SQLAlchemy model
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repository.py    # User data access layer
│   │   ├── project_repository.py # Project data access layer
│   │   └── task_repository.py    # Task data access layer
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py             # Common response envelopes and pagination
│   │   ├── user.py               # User Pydantic request/response schemas
│   │   ├── project.py            # Project Pydantic request/response schemas
│   │   └── task.py               # Task Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py       # User business logic
│   │   ├── project_service.py    # Project business logic
│   │   └── task_service.py       # Task business logic
│   └── utils/
│       ├── __init__.py
│       └── ids.py                # Prefixed UUID generators (usr_, prj_, tsk_)
├── scripts/
│   └── verify_persistence.py     # Standalone 10-step persistence verification test
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Test database fixtures and test client
│   ├── test_constraints.py       # Database-level constraint tests
│   ├── test_demo_workflow.py     # End-to-end integration workflow tests
│   ├── test_errors.py            # Error format and status code tests
│   ├── test_filters_and_pagination.py # Filter and pagination tests
│   ├── test_persistence.py       # Cold-restart persistence tests
│   ├── test_projects.py          # Project CRUD and relationship tests
│   ├── test_relationships.py     # Foreign key cascade and set-null tests
│   ├── test_tasks.py             # Task CRUD and status workflow tests
│   └── test_users.py             # User CRUD and email uniqueness tests
├── .env.example                  # Safe configuration placeholders
├── .gitignore                    # Secrets, caches, and DB file exclusions
├── requirements.txt              # Production and testing dependencies
└── README.md                     # Comprehensive documentation
```

---

## Swagger Documentation

FastAPI automatically generates interactive OpenAPI documentation:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
  Provides an interactive interface to execute live queries against the persistent database, test CRUD operations, and verify validation rules.
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
  Provides clean, readable API specification documentation.
- **OpenAPI JSON Schema:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## Internship Information

- **Internship:** Innovation Hacks — Full Stack Development Internship
- **Stage:** Week 3 — Task 3
- **Official Task:** Database Integration — Persistent Data Layer
- **Repository:** [https://github.com/Praveensagar07/persistent-data-layer](https://github.com/Praveensagar07/persistent-data-layer)
- **Author:** Praveensagar07