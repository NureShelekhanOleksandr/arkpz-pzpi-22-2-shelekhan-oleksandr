from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate, User
from sqlalchemy import select, delete
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException
from app.enums.user_role import Role


async def create_user(db: AsyncSession, user: UserCreate):
    """Create a new user."""
    user.password = get_password_hash(user.password)
    new_user = UserModel(**user.model_dump())
    db.add(new_user)
    await db.commit()
    return new_user


async def update_user(
    db: AsyncSession, user_id: int, user: UserUpdate, current_user: User
):
    """Update a user."""
    if user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this user."
        )
    query = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password:
        user.password = get_password_hash(user.password)
    for key, value in user.model_dump(exclude_none=True).items():
        setattr(db_user, key, value)
    await db.commit()
    return db_user


async def delete_user(db: AsyncSession, user_id: int, current_user: User):
    """Delete a user."""
    if user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=403, detail="You are not allowed to delete this user."
        )
    query = delete(UserModel).where(UserModel.id == user_id).returning(UserModel)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user(db: AsyncSession, user_id: int):
    """Retrieve a user by ID."""
    query = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """Authenticate a user by email and password."""
    query = select(UserModel).where(UserModel.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return user
