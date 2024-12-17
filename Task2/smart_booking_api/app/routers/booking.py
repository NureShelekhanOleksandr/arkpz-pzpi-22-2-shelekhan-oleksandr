from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.booking import BookingCreate, Booking, BookingUpdate
from app.crud import booking as booking_crud
from app.core.database import get_db
from app.dependencies import get_current_user, role_required
from app.enums.user_role import Role

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.post("/", response_model=Booking)
async def create_new_booking(
    booking: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(role_required([Role.USER])),
):
    return await booking_crud.create_booking(db, booking, current_user)


@router.get("/{booking_id}", response_model=Booking)
async def read_booking(booking_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await booking_crud.get_booking(db, booking_id, current_user)


@router.put("/{booking_id}", response_model=Booking)
async def update_booking_details(
    booking_id: int,
    booking: BookingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await booking_crud.update_booking(db, booking_id, booking, current_user)


@router.delete("/{booking_id}", response_model=Booking)
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await booking_crud.delete_booking(db, booking_id, current_user)
