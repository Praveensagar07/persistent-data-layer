# Persistent Data Layer

## Overview

**Persistent Data Layer** is the official **Week 3 / Task 3** milestone of the **Innovation Hacks Full Stack Development Internship**.

This project establishes an enterprise-grade relational database architecture extending the Week 2 REST API. In-memory data collections have been completely replaced with a persistent, transactional database layer using **PostgreSQL**, **SQLAlchemy 2.x**, and **Alembic**, providing ACID guarantees, database-level schema constraints, cascade relationship policies, database migrations, connection pooling, and secure environment configuration.

---

## Objective

The objective of Week 3 is to integrate a **real relational database** into the REST API so that User, Project, and Task data persist reliably across service lifecycles, with relationships modeled intentionally, validation enforced at both the API and database levels, and credentials handled securely through environment variables.

This project serves as the production-ready backend and persistent database foundation for **Week 4: AI-Powered Project & Task Management Platform**.

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

## Tech Stack

- **Language:** Python 3.14+
- **API Framework:** FastAPI 0.110+
- **ORM / Database Toolkit:** SQLAlchemy 2.0+ (Declarative Mappings, Typed Queries)
- **Database Driver:** `psycopg` (psycopg 3 binary driver for PostgreSQL)
- **Migrations:** Alembic 1.13+
- **Data Validation & Serialization:** Pydantic v2 (ConfigDict, field validators)
- **ASGI Web Server:** Uvicorn (standard async event loop)
- **Testing Suite:** Pytest 8+, HTTPX, TestClient

---

## Database Schema & Relationships

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

## Prerequisites

- **Python 3.10+** (Python 3.14 tested and verified)
- **PostgreSQL 14+** (or SQLite for offline/development use)
- **Git**

---

## Environment Variables

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

| Variable | Default Value | Description |
|---|---|---|
| `APP_NAME` | `Persistent Data Layer` | Display name of the application |
| `APP_ENV` | `development` | Environment name (`development`, `staging`, `production`) |
| `APP_VERSION` | `1.0.0` | Semantic version identifier |
| `DEBUG` | `true` | Debug mode toggle |
| `API_PREFIX` | `/api/v1` | URL route prefix for REST endpoints |
| `HOST` | `0.0.0.0` | ASGI bind interface |
| `PORT` | `8000` | ASGI bind port |
| `DATABASE_URL` | `postgresql+psycopg://<user>:<pwd>@localhost:5432/<db>` | Database connection URI |
| `DB_POOL_SIZE` | `10` | SQLAlchemy connection pool size |
| `DB_MAX_OVERFLOW` | `20` | Max overflow connections allowed |
| `DB_POOL_TIMEOUT` | `30` | Connection pool wait timeout (seconds) |
| `DB_POOL_PRE_PING` | `true` | Test connection liveness before checking out |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed CORS origins |
| `SEED_DATA_ON_STARTUP` | `true` | Auto-populate development seed records if DB is empty |

> [!NOTE]
> Never commit real database passwords or credentials to version control. The repository `.gitignore` strictly excludes `.env` and all database files.

---

## Installation

1. Clone repository and navigate to project folder:
   ```bash
   git clone https://github.com/Praveensagar07/persistent-data-layer.git
   cd persistent-data-layer
   ```

2. Create and activate a virtual environment:
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

## Database Setup & Migrations

### Setting up PostgreSQL Database
Create a new database in PostgreSQL using `psql`:
```sql
CREATE DATABASE persistent_db;
```

Update `DATABASE_URL` in `.env`:
```ini
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/persistent_db
```

*(Alternatively, to run locally with zero external setup, leave `DATABASE_URL=sqlite:///./persistent_data.db`)*

### Applying Migrations
Run Alembic to apply all migrations up to head:
```bash
python -m alembic upgrade head
```

To rollback a migration:
```bash
python -m alembic downgrade -1
```

---

## Running the API

Start the ASGI server with hot reloading enabled:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **API Root:** `http://localhost:8000/`
- **Health Check:** `http://localhost:8000/health`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`

---

## Seeding Development Data

To manually populate the database with realistic development data (4 users, 4 projects, 11 tasks):
```bash
python -m app.db.seed
```
*(The API will also automatically seed the database on first startup if `SEED_DATA_ON_STARTUP=true`)*

---

## Testing

Run the comprehensive test suite with Pytest:
```bash
pytest -v
```

### Official 10-Step Persistence Verification Test
To run the dedicated persistence verification test that writes data, terminates the API session and engine, cold-restarts from disk, and verifies 100% data integrity:
```bash
python scripts/verify_persistence.py
```

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

## Example API Requests

### 1. Create a User
```http
POST /api/v1/users HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "name": "Sarah Connor",
  "email": "sarah.connor@example.com",
  "role": "lead_architect"
}
```
**Response (201 Created):**
```json
{
  "data": {
    "id": "usr_7a8b9c0d1e2f3a4b",
    "name": "Sarah Connor",
    "email": "sarah.connor@example.com",
    "role": "lead_architect",
    "created_at": "2026-09-20T12:00:00Z",
    "updated_at": "2026-09-20T12:00:00Z"
  }
}
```

### 2. Create a Project
```http
POST /api/v1/projects HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "name": "Developer Productivity Platform",
  "description": "Unified metrics and task management dashboard.",
  "status": "active",
  "priority": "critical",
  "owner_id": "usr_7a8b9c0d1e2f3a4b"
}
```

### 3. Create a Task
```http
POST /api/v1/tasks HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "title": "Implement Database Migrations",
  "description": "Configure Alembic versioning for users, projects, and tasks.",
  "project_id": "prj_9a8b7c6d5e4f3a2b",
  "assignee_id": "usr_7a8b9c0d1e2f3a4b",
  "status": "in-progress",
  "priority": "high"
}
```

### 4. Progress Task Status
```http
PATCH /api/v1/tasks/tsk_1a2b3c4d5e6f7a8b/status HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "status": "done"
}
```

---

## Internship Information

- **Internship:** Innovation Hacks — Full Stack Development Internship
- **Stage:** Week 3 — Task 3
- **Official Task:** Database Integration — Persistent Data Layer
- **Repository:** [https://github.com/Praveensagar07/persistent-data-layer](https://github.com/Praveensagar07/persistent-data-layer)
- **Author:** Praveensagar07
