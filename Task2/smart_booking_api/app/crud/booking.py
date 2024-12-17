from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.booking import Booking
from app.schemas.user import User
from app.enums.user_role import Role
from app.schemas.booking import BookingCreate, BookingUpdate
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from datetime import date


async def check_availability(
    db: AsyncSession,
    property_id: int,
    start_date: date,
    end_date: date,
    booking_id: int = None,
) -> bool:
    """
    Check if a property is available for booking in the given date range.
    """
    if start_date >= end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be before the end date."
        )

    result = await db.execute(
        select(Booking)
        .filter(Booking.property_id == property_id)
        .filter(Booking.start_date < end_date)
        .filter(Booking.end_date > start_date)
        .filter(Booking.id != booking_id)
    )
    overlapping_bookings = result.scalars().all()

    return len(overlapping_bookings) == 0


async def create_booking(db: AsyncSession, booking: BookingCreate, user: User):
    """Create a new booking."""
    if not await check_availability(
        db, booking.property_id, booking.start_date, booking.end_date
    ):
        raise HTTPException(
            status_code=400, detail="Property is not available for booking."
        )

    new_booking = Booking(**booking.model_dump(), user_id=user.id)
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking


async def update_booking(
    db: AsyncSession, booking_id: int, booking: BookingUpdate, user: User
):
    """Update booking details."""
    db_booking = await get_booking(db, booking_id, user)

    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if db_booking.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to update this booking."
        )

    if booking.start_date or booking.end_date:
        start_date = booking.start_date or db_booking.start_date
        end_date = booking.end_date or db_booking.end_date

        if not await check_availability(
            db, db_booking.property_id, start_date, end_date, booking_id
        ):
            raise HTTPException(
                status_code=400, detail="Property is not available for booking."
            )

    for key, value in booking.model_dump().items():
        setattr(db_booking, key, value)

    await db.commit()
    await db.refresh(db_booking)
    return db_booking


async def delete_booking(db: AsyncSession, booking_id: int, user: User):
    """Delete a booking."""
    db_booking = await get_booking(db, booking_id, user)
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if db_booking.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to delete this booking."
        )
    delete_query = delete(Booking).where(Booking.id == booking_id).returning(Booking)
    result = await db.execute(delete_query)
    deleted_booking = result.scalar_one()
    await db.commit()
    return deleted_booking


async def get_booking(db: AsyncSession, booking_id: int, user: User):
    """Retrieve a booking by ID."""
    query = (
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.property))
    )
    result = await db.execute(query)
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user.role == Role.USER and booking.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to view this booking."
        )
    elif user.role == Role.OWNER and booking.property.owner_id != user.id:
        raise HTTPException(
            status_code=403, detail="You are not allowed to view this booking."
        )
    return booking
