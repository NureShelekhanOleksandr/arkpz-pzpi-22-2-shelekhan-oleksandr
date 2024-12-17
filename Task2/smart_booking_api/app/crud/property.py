from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Property
from app.models.user import User, Role
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.schemas.user import User
from sqlalchemy import select, delete
from fastapi import HTTPException


async def create_property(
    db: AsyncSession, property_data: PropertyCreate, user: User
):
    """Create a new property."""
    new_property = Property(**property_data.model_dump(), owner_id=user.id)
    db.add(new_property)
    await db.commit()
    await db.refresh(new_property)

    return new_property


async def update_property(
    db: AsyncSession, property_id: int, property_data: PropertyUpdate, user: User
):
    """Update an existing property."""

    result = await db.execute(select(Property).filter(Property.id == property_id))
    property = result.scalar_one_or_none()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found.")

    if property.owner_id != user.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this property."
        )

    for key, value in property_data.model_dump(exclude_none=True).items():
        setattr(property, key, value)

    await db.commit()
    await db.refresh(property)

    return property


async def delete_property(db: AsyncSession, property_id: int, user: User):
    """Delete a property."""

    result = await db.execute(select(Property).filter(Property.id == property_id))
    property = result.scalar_one_or_none()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found.")

    if property.owner_id != user.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to delete this property."
        )

    await db.execute(delete(Property).filter(Property.id == property_id))
    await db.commit()

    return property


async def get_property(db: AsyncSession, property_id: int):
    """Read a property by ID."""
    result = await db.execute(select(Property).filter(Property.id == property_id))
    property = result.scalar_one_or_none()

    if not property:
        raise HTTPException(status_code=404, detail="Property not found.")

    return property


async def get_properties(db: AsyncSession):
    """Read all properties."""
    result = await db.execute(select(Property))
    properties = result.scalars().all()

    return properties
