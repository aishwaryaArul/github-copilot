from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Project


class ProjectRepository:
    def create(self, session: Session, project: Project) -> Project:
        session.add(project)
        session.flush()
        return project

    def get_by_id(self, session: Session, tenant_id: str, project_id: int) -> Project | None:
        return session.scalar(
            select(Project).where(Project.tenant_id == tenant_id, Project.id == project_id)
        )

    def get_by_team(self, session: Session, tenant_id: str, team: str) -> list[Project]:
        return list(
            session.scalars(
                select(Project)
                .where(Project.tenant_id == tenant_id, Project.team == team)
                .order_by(Project.id)
            )
        )

    def delete(self, session: Session, project: Project) -> None:
        session.delete(project)
