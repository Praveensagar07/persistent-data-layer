"""Task management API routes."""

from fastapi import APIRouter, Depends, Query, status
from app.schemas.common import DataResponse, MessageData, MessageResponse, PaginatedResponse, PaginationMeta
from app.schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=DataResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Initialize a new work item attached to a project and an optional assignee.",
)
def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(),
) -> DataResponse[TaskResponse]:
    task = service.create_task(payload)
    return DataResponse(data=TaskResponse.model_validate(task))


@router.get(
    "",
    response_model=PaginatedResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List tasks",
    description="Retrieve a paginated collection of tasks matching optional filters (status, priority, project, assignee).",
)
def list_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    status: str | None = Query(None, description="Filter by task status (todo, in-progress, done)"),
    priority: str | None = Query(None, description="Filter by priority (low, medium, high, critical)"),
    project_id: str | None = Query(None, description="Filter by parent project ID"),
    assignee_id: str | None = Query(None, description="Filter by assignee user ID"),
    service: TaskService = Depends(),
) -> PaginatedResponse[TaskResponse]:
    tasks, total = service.list_tasks(
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        project_id=project_id,
        assignee_id=assignee_id,
    )
    return PaginatedResponse(
        data=[TaskResponse.model_validate(t) for t in tasks],
        meta=PaginationMeta(total=total, skip=skip, limit=limit),
    )


@router.get(
    "/{task_id}",
    response_model=DataResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Get task by ID",
    description="Retrieve full details for a single task.",
)
def get_task(
    task_id: str,
    service: TaskService = Depends(),
) -> DataResponse[TaskResponse]:
    task = service.get_task(task_id)
    return DataResponse(data=TaskResponse.model_validate(task))


@router.patch(
    "/{task_id}",
    response_model=DataResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Update task",
    description="Modify task title, description, priority, due date, status, or reassign project/assignee.",
)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    service: TaskService = Depends(),
) -> DataResponse[TaskResponse]:
    task = service.update_task(task_id, payload)
    return DataResponse(data=TaskResponse.model_validate(task))


@router.patch(
    "/{task_id}/status",
    response_model=DataResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Update task status",
    description="Dedicated endpoint to update only the task workflow state (todo, in-progress, done).",
)
def update_task_status(
    task_id: str,
    payload: TaskStatusUpdate,
    service: TaskService = Depends(),
) -> DataResponse[TaskResponse]:
    task = service.update_task_status(task_id, payload.status)
    return DataResponse(data=TaskResponse.model_validate(task))


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete task",
    description="Remove task by identifier.",
)
def delete_task(
    task_id: str,
    service: TaskService = Depends(),
) -> MessageResponse:
    service.delete_task(task_id)
    return MessageResponse(
        data=MessageData(message="Task deleted successfully", id=task_id)
    )
