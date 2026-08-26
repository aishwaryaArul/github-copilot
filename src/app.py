"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlalchemy.orm import Session

from src.database import Database
from src.models import Project
from src.schemas import ProjectCreate, ProjectResponse, ProjectStatusUpdate
from src.schemas_core import (
    AuditLogCreate,
    AuditLogResponse,
    NotificationCreate,
    NotificationResponse,
)
from src.services.core_service import CoreService, CoreValidationError
from src.services.project_service import (
    ProjectNotFoundError,
    ProjectService,
    ProjectValidationError,
)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")
database = Database()
project_service = ProjectService()
core_service = CoreService()


def get_database_session() -> Generator[Session, None, None]:
    session = database.session()
    try:
        yield session
    finally:
        session.close()


def get_tenant_id(tenant_id: Annotated[str, Header(alias="X-Tenant-ID")]) -> str:
    clean_tenant_id = tenant_id.strip()
    if not clean_tenant_id or len(clean_tenant_id) > 100:
        raise HTTPException(status_code=400, detail="Invalid tenant ID")
    return clean_tenant_id

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Club": {
        "description": "Build soccer skills and compete in friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 24,
        "participants": []
    },
    "Track and Field": {
        "description": "Train for running, jumping, and throwing events",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 30,
        "participants": []
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed-media projects",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Develop acting skills and perform original productions",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Club": {
        "description": "Practice research, public speaking, and argumentation",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": []
    },
    "Mathematics Club": {
        "description": "Solve challenging problems and prepare for competitions",
        "schedule": "Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up for this activity"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants/{email}")
def unregister_from_activity(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=404,
            detail="Student is not signed up for this activity"
        )

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
) -> Project:
    try:
        return project_service.create_project(
            session, tenant_id, payload.name, payload.team, payload.status
        )
    except ProjectValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.patch("/projects/{project_id}/status", response_model=ProjectResponse)
def update_project_status(
    project_id: int,
    payload: ProjectStatusUpdate,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
) -> Project:
    try:
        return project_service.update_project_status(session, tenant_id, project_id, payload.status)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project not found") from error


@app.get("/projects", response_model=list[ProjectResponse])
def get_projects_by_team(
    team: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
) -> list[Project]:
    try:
        return project_service.get_projects_by_team(session, tenant_id, team)
    except ProjectValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
) -> None:
    try:
        project_service.delete_project(session, tenant_id, project_id)
    except ProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail="Project not found") from error


@app.post("/audit-logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def record_audit_log(
    payload: AuditLogCreate,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
) -> AuditLogResponse:
    try:
        return core_service.record_audit(
            session,
            tenant_id,
            payload.actor_id,
            payload.action,
            payload.resource_type,
            payload.resource_id,
            payload.details,
        )
    except CoreValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/audit-logs", response_model=list[AuditLogResponse])
def get_audit_logs(
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
    limit: int = 100,
) -> list[AuditLogResponse]:
    try:
        return core_service.get_audit_logs(session, tenant_id, limit)
    except CoreValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreate,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
) -> NotificationResponse:
    try:
        return core_service.create_notification(
            session,
            tenant_id,
            payload.recipient_id,
            payload.notification_type,
            payload.message,
        )
    except CoreValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/notifications", response_model=list[NotificationResponse])
def get_notifications(
    recipient_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
    limit: int = 100,
) -> list[NotificationResponse]:
    try:
        return core_service.get_notifications(session, tenant_id, recipient_id, limit)
    except CoreValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    recipient_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    session: Annotated[Session, Depends(get_database_session)],
) -> NotificationResponse:
    try:
        return core_service.mark_notification_read(
            session, tenant_id, recipient_id, notification_id
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail="Notification not found") from error
