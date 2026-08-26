from pydantic import BaseModel, ConfigDict, Field

from src.models import ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    team: str = Field(min_length=1, max_length=100)
    status: ProjectStatus = ProjectStatus.ACTIVE


class ProjectStatusUpdate(BaseModel):
    status: ProjectStatus


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: str
    name: str
    team: str
    status: ProjectStatus