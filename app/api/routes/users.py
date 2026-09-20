"""User management API routes."""

from fastapi import APIRouter, Depends, Query, status
from app.schemas.common import DataResponse, MessageData, MessageResponse, PaginatedResponse, PaginationMeta
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Register a new user account with unique email address validation.",
)
def create_user(
    payload: UserCreate,
    service: UserService = Depends(),
) -> DataResponse[UserResponse]:
    user = service.create_user(payload)
    return DataResponse(data=UserResponse.model_validate(user))


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Retrieve a paginated collection of users with optional role filtering.",
)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    role: str | None = Query(None, description="Filter by user role"),
    service: UserService = Depends(),
) -> PaginatedResponse[UserResponse]:
    users, total = service.list_users(skip=skip, limit=limit, role=role)
    return PaginatedResponse(
        data=[UserResponse.model_validate(u) for u in users],
        meta=PaginationMeta(total=total, skip=skip, limit=limit),
    )


@router.get(
    "/{user_id}",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve specific user details by their unique identifier.",
)
def get_user(
    user_id: str,
    service: UserService = Depends(),
) -> DataResponse[UserResponse]:
    user = service.get_user(user_id)
    return DataResponse(data=UserResponse.model_validate(user))


@router.patch(
    "/{user_id}",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Modify specific user properties (name, email, role).",
)
def update_user(
    user_id: str,
    payload: UserUpdate,
    service: UserService = Depends(),
) -> DataResponse[UserResponse]:
    user = service.update_user(user_id, payload)
    return DataResponse(data=UserResponse.model_validate(user))


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Remove user by identifier.",
)
def delete_user(
    user_id: str,
    service: UserService = Depends(),
) -> MessageResponse:
    service.delete_user(user_id)
    return MessageResponse(
        data=MessageData(message="User deleted successfully", id=user_id)
    )
