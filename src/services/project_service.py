import logging

from sqlalchemy.orm import Session

from src.models import Project, ProjectStatus
from src.repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)

class ProjectNotFoundError(LookupError):
    """Raised when a project is not found within the current tenant."""


class ProjectValidationError(ValueError):
    """Raised when project input is invalid."""


class ProjectService:
    def __init__(self, repository: ProjectRepository | None = None) -> None:
        self.repository = repository or ProjectRepository()

    def create_project(
        self,
        session: Session,
        tenant_id: str,
        name: str,
        team: str,
        status: ProjectStatus = ProjectStatus.ACTIVE,
    ) -> Project:
        project = Project(
            tenant_id=tenant_id,
            name=self._required_text(name, "name", 200),
            team=self._required_text(team, "team", 100),
            status=status,
        )
        self.repository.create(session, project)
        session.commit()
        logger.info("project_created", extra={"tenant_id": tenant_id, "project_id": project.id})
        return project

    def update_project_status(
        self, session: Session, tenant_id: str, project_id: int, status: ProjectStatus
    ) -> Project:
        project = self._get_project(session, tenant_id, project_id)
        project.status = status
        session.commit()
        logger.info("project_status_updated", extra={"tenant_id": tenant_id, "project_id": project_id})
        return project

    def get_projects_by_team(self, session: Session, tenant_id: str, team: str) -> list[Project]:
        return self.repository.get_by_team(session, tenant_id, self._required_text(team, "team", 100))

    def delete_project(self, session: Session, tenant_id: str, project_id: int) -> None:
        project = self._get_project(session, tenant_id, project_id)
        self.repository.delete(session, project)
        session.commit()
        logger.info("project_deleted", extra={"tenant_id": tenant_id, "project_id": project_id})

    def _get_project(self, session: Session, tenant_id: str, project_id: int) -> Project:
        project = self.repository.get_by_id(session, tenant_id, project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} was not found")
        return project

    @staticmethod
    def _required_text(value: str, field_name: str, max_length: int) -> str:
        clean_value = value.strip()
        if not clean_value or len(clean_value) > max_length:
            raise ProjectValidationError(f"{field_name} must be between 1 and {max_length} characters")
        return clean_value
