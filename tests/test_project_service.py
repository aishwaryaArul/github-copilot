import pytest

from src.database import Database
from src.models import ProjectStatus
from src.services.project_service import (
    ProjectNotFoundError,
    ProjectService,
    ProjectValidationError,
)


@pytest.fixture
def project_service(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'projects.sqlite3'}")
    session = database.session()
    yield ProjectService(), session
    session.close()


def test_create_project_persists_project(project_service):
    service, session = project_service
    project = service.create_project(session, "tenant-a", "Website", "Platform")

    assert project.id > 0
    assert project.tenant_id == "tenant-a"
    assert project.name == "Website"
    assert project.team == "Platform"
    assert project.status == ProjectStatus.ACTIVE


def test_update_project_status(project_service):
    service, session = project_service
    project = service.create_project(session, "tenant-a", "Website", "Platform")

    updated_project = service.update_project_status(
        session, "tenant-a", project.id, ProjectStatus.COMPLETED
    )

    assert updated_project == project.__class__(
        id=project.id,
        name="Website",
        team="Platform",
        status=ProjectStatus.COMPLETED,
    )


def test_get_projects_by_team_returns_matching_projects(project_service):
    service, session = project_service
    platform_project = service.create_project(session, "tenant-a", "Website", "Platform")
    service.create_project(session, "tenant-a", "Mobile App", "Mobile")
    second_platform_project = service.create_project(session, "tenant-a", "API", "Platform")
    service.create_project(session, "tenant-b", "Other", "Platform")

    projects = service.get_projects_by_team(session, "tenant-a", "Platform")

    assert projects == [platform_project, second_platform_project]


def test_delete_project_removes_project(project_service):
    service, session = project_service
    project = service.create_project(session, "tenant-a", "Website", "Platform")

    service.delete_project(session, "tenant-a", project.id)

    assert service.get_projects_by_team(session, "tenant-a", "Platform") == []


@pytest.mark.parametrize("operation", ["update", "delete"])
def test_missing_project_raises_not_found(project_service, operation):
    service, session = project_service
    with pytest.raises(ProjectNotFoundError):
        if operation == "update":
            service.update_project_status(session, "tenant-a", 999, ProjectStatus.COMPLETED)
        else:
            service.delete_project(session, "tenant-a", 999)


def test_cross_tenant_project_cannot_be_updated_or_deleted(project_service):
    service, session = project_service
    project = service.create_project(session, "tenant-a", "Website", "Platform")

    with pytest.raises(ProjectNotFoundError):
        service.update_project_status(
            session, "tenant-b", project.id, ProjectStatus.COMPLETED
        )
    with pytest.raises(ProjectNotFoundError):
        service.delete_project(session, "tenant-b", project.id)


def test_invalid_project_fields_are_rejected(project_service):
    service, session = project_service

    with pytest.raises(ProjectValidationError):
        service.create_project(session, "tenant-a", " ", "Platform")
    with pytest.raises(ProjectValidationError):
        service.get_projects_by_team(session, "tenant-a", " ")
