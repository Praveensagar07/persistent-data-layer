"""Project management API routes."""

from fastapi import APIRouter, Depends, Query, status
from app.schemas.common import DataResponse, MessageData, MessageResponse, PaginatedResponse, PaginationMeta
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=DataResponse[ProjectResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Initialize a new project owned by a valid registered user.",
)
def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(),
) -> DataResponse[ProjectResponse]:
    project = service.create_project(payload)
    return DataResponse(data=ProjectResponse.model_validate(project))


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List projects",
    description="Retrieve a paginated collection of projects with optional owner or status filtering.",
)
def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    owner_id: str | None = Query(None, description="Filter projects by owner ID"),
    status: str | None = Query(None, description="Filter projects by lifecycle status"),
    service: ProjectService = Depends(),
) -> PaginatedResponse[ProjectResponse]:
    projects, total = service.list_projects(
        skip=skip,
        limit=limit,
        owner_id=owner_id,
        status=status,
    )
    return PaginatedResponse(
        data=[ProjectResponse.model_validate(p) for p in projects],
        meta=PaginationMeta(total=total, skip=skip, limit=limit),
    )


@router.get(
    "/{project_id}",
    response_model=DataResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Get project by ID",
    description="Retrieve detailed metadata for a specific project.",
)
def get_project(
    project_id: str,
    service: ProjectService = Depends(),
) -> DataResponse[ProjectResponse]:
    project = service.get_project(project_id)
    return DataResponse(data=ProjectResponse.model_validate(project))


@router.patch(
    "/{project_id}",
    response_model=DataResponse[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Update project",
    description="Modify project properties (name, description, status, priority, owner).",
)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    service: ProjectService = Depends(),
) -> DataResponse[ProjectResponse]:
    project = service.update_project(project_id, payload)
    return DataResponse(data=ProjectResponse.model_validate(project))


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete project",
    description="Remove project by identifier (cascades to child tasks).",
)
def delete_project(
    project_id: str,
    service: ProjectService = Depends(),
) -> MessageResponse:
    service.delete_project(project_id)
    return MessageResponse(
        data=MessageData(message="Project deleted successfully", id=project_id)
    )
