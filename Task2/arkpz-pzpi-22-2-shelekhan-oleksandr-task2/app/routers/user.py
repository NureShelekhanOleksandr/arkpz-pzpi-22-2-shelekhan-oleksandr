from fastapi import APIRouter, Depends, HTTPException, status
from app.crud import user as user_crud
from app.schemas.user import UserCreate, User, UserUpdate, UserBase
from app.core.database import get_db
from app.dependencies import role_required, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.user_role import Role

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me", response_model=UserBase)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Retrieve the current authenticated user."""
    return current_user


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user."""
    if user.role == Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to create an admin user.",
        )
    return await user_crud.create_user(db, user)


@router.post("/admin", response_model=User)
async def create_admin_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN])),
):
    """Create a new admin user."""
    return await user_crud.create_user(db, user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user."""
    return await user_crud.update_user(db, user_id, user, current_user)


@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a user."""
    return await user_crud.delete_user(db, user_id, current_user)
