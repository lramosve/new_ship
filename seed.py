"""Seed the database with a demo account and sample data."""
import sys
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.security import hash_password, utc_now
from app.db import SessionLocal, engine, Base
from app.models import Project, Document, User, Issue, Plan, Task


DEMO_EMAIL = "dev@ship.dev"
DEMO_PASSWORD = "admin123"

TEAM = [
    ("Dev User", DEMO_EMAIL),
    ("Alice Chen", "alice.chen@ship.dev"),
    ("Bob Martinez", "bob.martinez@ship.dev"),
    ("Carol Williams", "carol.williams@ship.dev"),
    ("David Kim", "david.kim@ship.dev"),
    ("Emma Johnson", "emma.johnson@ship.dev"),
]


def seed(db: Session) -> None:
    # Skip if already seeded
    if db.query(User).filter(User.email == DEMO_EMAIL).first():
        print("[seed] demo user already exists, skipping")
        return

    hashed = hash_password(DEMO_PASSWORD)
    now = utc_now()

    # --- Users ---
    users = []
    for name, email in TEAM:
        u = User(name=name, email=email, hashed_password=hashed,
                 created_at=now, updated_at=now)
        db.add(u)
        users.append(u)
    db.flush()
    print(f"[seed] created {len(users)} users")

    dev_user = users[0]

    # --- Projects ---
    projects_data = [
        ("Ship Platform", "Core project management platform for government teams"),
        ("FleetGraph Agent", "AI-powered project intelligence and anomaly detection"),
        ("Infrastructure", "Cloud infrastructure, CI/CD, and deployment automation"),
    ]
    projects = []
    for pname, pdesc in projects_data:
        p = Project(name=pname, description=pdesc)
        db.add(p)
        projects.append(p)
    db.flush()
    print(f"[seed] created {len(projects)} projects")

    # --- Documents ---
    docs_data = [
        ("Architecture Decision Record", "spec",
         "# ADR-001: Unified Document Model\n\n"
         "## Status\nAccepted\n\n"
         "## Context\nWe need a flexible data model that supports multiple document types.\n\n"
         "## Decision\nUse a single documents table with a type discriminator and JSONB properties."),
        ("Sprint 12 Plan", "report",
         "## Sprint 12 Goals\n- Complete task management backend\n"
         "- Deploy analytics dashboard\n- Fix outstanding auth bugs"),
        ("API Reference", "spec",
         "# Ship API Reference\n\n"
         "## Authentication\nPOST /auth/login - Returns JWT token\n\n"
         "## Projects\nGET /projects/ - List all projects\n"
         "POST /projects/ - Create a project"),
        ("Onboarding Guide", "markdown",
         "# Welcome to Ship\n\nThis guide will help you get started with the platform.\n\n"
         "## First Steps\n1. Log in with your team credentials\n"
         "2. Navigate to your assigned project\n3. Review open issues"),
    ]
    documents = []
    for title, dtype, content in docs_data:
        d = Document(title=title, type=dtype, content=content,
                     owner_id=dev_user.id, created_at=now, updated_at=now)
        db.add(d)
        documents.append(d)
    db.flush()
    print(f"[seed] created {len(documents)} documents")

    # --- Issues ---
    today = date.today()
    issues_data = [
        ("Login timeout on slow connections", "Requests hang for >30s on poor networks", "in_progress"),
        ("Dashboard chart labels overlap", "Bar chart labels unreadable at narrow widths", "open"),
        ("Missing CSRF protection on POST endpoints", "Security audit flagged missing tokens", "open"),
        ("Kanban drag-drop fails on mobile", "Touch events not handled in dnd-kit config", "in_progress"),
        ("Add bulk issue export to CSV", "Users need to export filtered issue lists", "closed"),
        ("Fix timezone display in activity feed", "Timestamps show UTC instead of local", "blocked"),
    ]
    issues = []
    for ititle, idesc, istatus in issues_data:
        i = Issue(title=ititle, description=idesc, status=istatus,
                  document_id=documents[0].id, created_at=now, updated_at=now)
        db.add(i)
        issues.append(i)
    db.flush()
    print(f"[seed] created {len(issues)} issues")

    # --- Plans ---
    plans_data = [
        ("Complete task management backend and write integration tests", 12),
        ("Deploy analytics dashboard with server-side filtering", 12),
        ("Ship real-time WebSocket updates for project management", 13),
        ("Conduct security review and fix auth vulnerabilities", 13),
    ]
    plans = []
    for pdesc, week in plans_data:
        pl = Plan(description=pdesc, week_number=week,
                  document_id=documents[1].id, created_at=now, updated_at=now)
        db.add(pl)
        plans.append(pl)
    db.flush()
    print(f"[seed] created {len(plans)} plans")

    # --- Tasks ---
    tasks_data = [
        ("Implement JWT refresh tokens", "Add token refresh endpoint and auto-renewal",
         "in_progress", "high", 60, 0, 1, today - timedelta(days=3), today + timedelta(days=4)),
        ("Write analytics aggregation tests", "Unit tests for trend and distribution queries",
         "todo", "medium", 0, 0, 2, today, today + timedelta(days=2)),
        ("Set up Docker health checks", "Add health check to docker-compose services",
         "done", "low", 100, 0, 3, today - timedelta(days=5), today - timedelta(days=2)),
        ("Design Kanban board component", "React component with drag-and-drop columns",
         "in_review", "high", 90, 0, 4, today - timedelta(days=7), today - timedelta(days=1)),
        ("Configure CI/CD pipeline", "GitHub Actions for build, test, and deploy",
         "done", "medium", 100, 2, 5, today - timedelta(days=10), today - timedelta(days=5)),
        ("Add WebSocket authentication", "Validate JWT on WebSocket connect",
         "in_progress", "high", 40, 1, 1, today - timedelta(days=1), today + timedelta(days=3)),
        ("Create seed data script", "Populate database with demo users and sample data",
         "in_progress", "medium", 80, 0, 2, today - timedelta(days=2), today),
        ("Write E2E smoke tests", "Playwright tests for login and dashboard load",
         "todo", "low", 0, 1, 3, today + timedelta(days=1), today + timedelta(days=5)),
        ("Fix pagination on issues list", "Offset-based pagination returns wrong count",
         "todo", "medium", 0, 2, 4, today, today + timedelta(days=3)),
        ("Deploy staging environment", "Railway deployment with PostgreSQL",
         "todo", "urgent", 0, 0, 5, today, today + timedelta(days=1)),
    ]
    for ttitle, tdesc, tstatus, tpri, tprog, proj_idx, user_idx, start, due in tasks_data:
        t = Task(
            title=ttitle, description=tdesc, status=tstatus,
            priority=tpri, progress=tprog,
            project_id=projects[proj_idx].id,
            assignee_id=users[user_idx].id,
            start_date=start, due_date=due,
            created_at=now, updated_at=now,
        )
        db.add(t)
    db.flush()
    print(f"[seed] created {len(tasks_data)} tasks")

    db.commit()
    print(f"[seed] done — login with {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    except Exception as exc:
        db.rollback()
        print(f"[seed] error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()
