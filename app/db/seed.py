"""Database development seeder for demonstration and testing."""

import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.project import Project
from app.models.task import Task
from app.models.user import User

logger = logging.getLogger("persistent_data_layer.seed")


def seed_database(db: Session) -> None:
    """Populate database with realistic development entities if database is empty."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Check if users already exist
    existing_user = db.query(User).first()
    if existing_user:
        logger.info("Database already contains data; skipping seed.")
        return

    now = datetime.now(timezone.utc)

    # ----------------------------------------------------
    # 1. Users
    # ----------------------------------------------------
    users = [
        User(
            id="usr_alex_rivera",
            name="Alex Rivera",
            email="alex.rivera@example.com",
            role="admin",
            created_at=now - timedelta(days=14),
            updated_at=now - timedelta(days=14),
        ),
        User(
            id="usr_jordan_lee",
            name="Jordan Lee",
            email="jordan.lee@example.com",
            role="lead_architect",
            created_at=now - timedelta(days=12),
            updated_at=now - timedelta(days=12),
        ),
        User(
            id="usr_samira_khan",
            name="Samira Khan",
            email="samira.khan@example.com",
            role="developer",
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=10),
        ),
        User(
            id="usr_taylor_chen",
            name="Taylor Chen",
            email="taylor.chen@example.com",
            role="qa_engineer",
            created_at=now - timedelta(days=8),
            updated_at=now - timedelta(days=8),
        ),
    ]
    for u in users:
        db.add(u)
    db.flush()

    # ----------------------------------------------------
    # 2. Projects
    # ----------------------------------------------------
    projects = [
        Project(
            id="prj_dev_dashboard",
            name="Developer Productivity Dashboard",
            description="Modern unified metrics, work analytics, and task tracking frontend platform.",
            status="active",
            priority="critical",
            owner_id="usr_alex_rivera",
            created_at=now - timedelta(days=14),
            updated_at=now - timedelta(days=5),
        ),
        Project(
            id="prj_mobile_app",
            name="Mobile Companion App",
            description="Cross-platform Flutter/React Native companion app for on-the-go progress tracking.",
            status="planning",
            priority="high",
            owner_id="usr_jordan_lee",
            created_at=now - timedelta(days=9),
            updated_at=now - timedelta(days=9),
        ),
        Project(
            id="prj_cicd_pipeline",
            name="Automated CI/CD Pipeline",
            description="Standardized GitHub Actions workflow with linting, unit tests, and security scans.",
            status="active",
            priority="medium",
            owner_id="usr_samira_khan",
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(days=2),
        ),
        Project(
            id="prj_design_system",
            name="Enterprise Design System",
            description="Accessible UI tokens, component library, and Figma typography specifications.",
            status="completed",
            priority="low",
            owner_id="usr_taylor_chen",
            created_at=now - timedelta(days=14),
            updated_at=now - timedelta(days=1),
        ),
    ]
    for p in projects:
        db.add(p)
    db.flush()

    # ----------------------------------------------------
    # 3. Tasks
    # ----------------------------------------------------
    tasks = [
        Task(
            id="tsk_dashboard_auth",
            title="Design JWT token refresh workflow",
            description="Specify secure token renewal headers and automatic retry interceptors.",
            project_id="prj_dev_dashboard",
            assignee_id="usr_jordan_lee",
            status="done",
            priority="high",
            due_date=now - timedelta(days=2),
            created_at=now - timedelta(days=13),
            updated_at=now - timedelta(days=3),
        ),
        Task(
            id="tsk_dashboard_metrics",
            title="Integrate velocity chart widget",
            description="Connect Chart.js components to aggregate weekly sprint velocity metrics.",
            project_id="prj_dev_dashboard",
            assignee_id="usr_samira_khan",
            status="in-progress",
            priority="critical",
            due_date=now + timedelta(days=3),
            created_at=now - timedelta(days=8),
            updated_at=now - timedelta(days=1),
        ),
        Task(
            id="tsk_dashboard_filter",
            title="Add task status multi-filter bar",
            description="Allow dashboard operators to filter tasks by multiple states simultaneously.",
            project_id="prj_dev_dashboard",
            assignee_id="usr_samira_khan",
            status="todo",
            priority="medium",
            due_date=now + timedelta(days=6),
            created_at=now - timedelta(days=4),
            updated_at=now - timedelta(days=4),
        ),
        Task(
            id="tsk_mobile_wireframes",
            title="Finalize mobile UI wireframes",
            description="Review Figma prototypes with product management team.",
            project_id="prj_mobile_app",
            assignee_id="usr_taylor_chen",
            status="done",
            priority="high",
            due_date=now - timedelta(days=1),
            created_at=now - timedelta(days=8),
            updated_at=now - timedelta(days=1),
        ),
        Task(
            id="tsk_mobile_offline_sync",
            title="Architect offline data synchronization",
            description="Design conflict resolution strategies using SQLite and local timestamps.",
            project_id="prj_mobile_app",
            assignee_id="usr_jordan_lee",
            status="in-progress",
            priority="critical",
            due_date=now + timedelta(days=5),
            created_at=now - timedelta(days=6),
            updated_at=now - timedelta(days=2),
        ),
        Task(
            id="tsk_mobile_push_notifs",
            title="Configure FCM push notifications",
            description="Setup Firebase Cloud Messaging credentials and payload handlers.",
            project_id="prj_mobile_app",
            assignee_id="usr_samira_khan",
            status="todo",
            priority="low",
            due_date=now + timedelta(days=12),
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=5),
        ),
        Task(
            id="tsk_ci_runner",
            title="Configure self-hosted GitHub Actions runner",
            description="Provision isolated Linux runners with pre-cached Docker layers.",
            project_id="prj_cicd_pipeline",
            assignee_id="usr_alex_rivera",
            status="done",
            priority="high",
            due_date=now - timedelta(days=3),
            created_at=now - timedelta(days=7),
            updated_at=now - timedelta(days=3),
        ),
        Task(
            id="tsk_ci_security_scan",
            title="Add automated Trivy security vulnerability scanner",
            description="Trap high and critical vulnerabilities in container images before merge.",
            project_id="prj_cicd_pipeline",
            assignee_id="usr_taylor_chen",
            status="in-progress",
            priority="medium",
            due_date=now + timedelta(days=2),
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=1),
        ),
        Task(
            id="tsk_ci_slack_webhook",
            title="Post build status notifications to Slack",
            description="Send color-coded deployment status alerts into #deployments channel.",
            project_id="prj_cicd_pipeline",
            assignee_id="usr_samira_khan",
            status="todo",
            priority="low",
            due_date=now + timedelta(days=8),
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=3),
        ),
        Task(
            id="tsk_design_tokens",
            title="Publish color tokens v2",
            description="Export dark and light theme HEX and HSL tokens to npm package.",
            project_id="prj_design_system",
            assignee_id="usr_taylor_chen",
            status="done",
            priority="medium",
            due_date=now - timedelta(days=4),
            created_at=now - timedelta(days=14),
            updated_at=now - timedelta(days=4),
        ),
        Task(
            id="tsk_design_accessibility",
            title="WCAG 2.1 AA accessibility audit",
            description="Perform automated screen reader and contrast ratio verification.",
            project_id="prj_design_system",
            assignee_id="usr_taylor_chen",
            status="done",
            priority="critical",
            due_date=now - timedelta(days=1),
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=1),
        ),
    ]
    for t in tasks:
        db.add(t)

    db.commit()
    logger.info("Database successfully seeded with %d users, %d projects, and %d tasks.", len(users), len(projects), len(tasks))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session = SessionLocal()
    try:
        seed_database(session)
        print("Seed completed successfully.")
    finally:
        session.close()
