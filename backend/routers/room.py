from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.room import RoomDB
from models.bed import BedDB
from models.hospital import HospitalDB
from models.department import DepartmentDB

from schema.room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
)

from utils.dependencies import (
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)


# ============================================================
# VALIDATE HOSPITAL AND DEPARTMENT
# ============================================================

def validate_hospital_and_department(
    hospital_id: int,
    department_id: int,
    db: Session,
):
    # --------------------------------------------------------
    # Check hospital
    # --------------------------------------------------------

    hospital = db.scalar(
        select(HospitalDB).where(
            HospitalDB.id == hospital_id
        )
    )

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found.",
        )

    # --------------------------------------------------------
    # Check department
    # --------------------------------------------------------

    department = db.scalar(
        select(DepartmentDB).where(
            DepartmentDB.id == department_id
        )
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    # --------------------------------------------------------
    # Department must belong to selected hospital
    # --------------------------------------------------------

    if department.hospital_id != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The selected department does not "
                "belong to the selected hospital."
            ),
        )

    return hospital, department


# ============================================================
# CREATE ROOM
# ============================================================

@router.post(
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    # --------------------------------------------------------
    # Validate hospital + department
    # --------------------------------------------------------

    validate_hospital_and_department(
        room_data.hospital_id,
        room_data.department_id,
        db,
    )

    # --------------------------------------------------------
    # Check duplicate room number within hospital
    # --------------------------------------------------------

    existing_room = db.scalar(
        select(RoomDB).where(
            RoomDB.hospital_id == room_data.hospital_id,
            RoomDB.room_number == room_data.room_number,
        )
    )

    if existing_room is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room number already exists in this hospital.",
        )

    # --------------------------------------------------------
    # Create room
    # --------------------------------------------------------

    room = RoomDB(
        room_number=room_data.room_number,
        room_type=room_data.room_type,
        status=room_data.status,
        hospital_id=room_data.hospital_id,
        department_id=room_data.department_id,
    )

    db.add(room)

    try:
        db.commit()
        db.refresh(room)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Room could not be created because "
                "of a database constraint."
            ),
        )

    return room


# ============================================================
# GET ALL ROOMS
# ============================================================

@router.get(
    "/",
    response_model=list[RoomResponse],
    status_code=status.HTTP_200_OK,
)
def get_rooms(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "pharmacist",
        )
    ),
):
    rooms = db.scalars(
        select(RoomDB).order_by(
            RoomDB.hospital_id,
            RoomDB.room_number,
            RoomDB.id,
        )
    ).all()

    return rooms


# ============================================================
# GET ROOMS BY HOSPITAL
# ============================================================

@router.get(
    "/hospital/{hospital_id}",
    response_model=list[RoomResponse],
    status_code=status.HTTP_200_OK,
)
def get_hospital_rooms(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "pharmacist",
        )
    ),
):
    # --------------------------------------------------------
    # Check hospital
    # --------------------------------------------------------

    hospital = db.scalar(
        select(HospitalDB).where(
            HospitalDB.id == hospital_id
        )
    )

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found.",
        )

    rooms = db.scalars(
        select(RoomDB)
        .where(
            RoomDB.hospital_id == hospital_id
        )
        .order_by(
            RoomDB.room_number,
            RoomDB.id,
        )
    ).all()

    return rooms


# ============================================================
# GET ROOMS BY DEPARTMENT
# ============================================================

@router.get(
    "/department/{department_id}",
    response_model=list[RoomResponse],
    status_code=status.HTTP_200_OK,
)
def get_department_rooms(
    department_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "pharmacist",
        )
    ),
):
    # --------------------------------------------------------
    # Check department
    # --------------------------------------------------------

    department = db.scalar(
        select(DepartmentDB).where(
            DepartmentDB.id == department_id
        )
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    rooms = db.scalars(
        select(RoomDB)
        .where(
            RoomDB.department_id == department_id
        )
        .order_by(
            RoomDB.room_number,
            RoomDB.id,
        )
    ).all()

    return rooms


# ============================================================
# GET ROOM BY ID
# ============================================================

@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    status_code=status.HTTP_200_OK,
)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "pharmacist",
        )
    ),
):
    room = db.scalar(
        select(RoomDB).where(
            RoomDB.id == room_id
        )
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    return room


# ============================================================
# UPDATE ROOM
# ============================================================

@router.patch(
    "/{room_id}",
    response_model=RoomResponse,
    status_code=status.HTTP_200_OK,
)
def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    # --------------------------------------------------------
    # Lock room during update
    # --------------------------------------------------------

    room = db.scalar(
        select(RoomDB)
        .where(
            RoomDB.id == room_id
        )
        .with_for_update()
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    update_data = room_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # --------------------------------------------------------
    # Determine final values
    # --------------------------------------------------------

    final_room_number = update_data.get(
        "room_number",
        room.room_number,
    )

    final_room_type = update_data.get(
        "room_type",
        room.room_type,
    )

    final_status = update_data.get(
        "status",
        room.status,
    )

    final_hospital_id = update_data.get(
        "hospital_id",
        room.hospital_id,
    )

    final_department_id = update_data.get(
        "department_id",
        room.department_id,
    )

    # --------------------------------------------------------
    # Validate hospital + department
    # --------------------------------------------------------

    validate_hospital_and_department(
        final_hospital_id,
        final_department_id,
        db,
    )

    # --------------------------------------------------------
    # Check duplicate room number
    # --------------------------------------------------------

    existing_room = db.scalar(
        select(RoomDB).where(
            RoomDB.hospital_id == final_hospital_id,
            RoomDB.room_number == final_room_number,
            RoomDB.id != room_id,
        )
    )

    if existing_room is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room number already exists in this hospital.",
        )

    # --------------------------------------------------------
    # Check beds before moving room between hospitals/
    # departments.
    #
    # Existing beds belong to this room, so moving a room is
    # allowed only when the room itself remains logically valid.
    # --------------------------------------------------------

    if (
        final_hospital_id != room.hospital_id
        or final_department_id != room.department_id
    ):
        beds_exist = db.scalar(
            select(BedDB.id)
            .where(
                BedDB.room_id == room_id
            )
            .limit(1)
        )

        if beds_exist is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A room containing beds cannot be "
                    "moved to another hospital or department."
                ),
            )

    # --------------------------------------------------------
    # Do not change an occupied room to maintenance/inactive
    # --------------------------------------------------------

    if (
        room.status == "occupied"
        and final_status in {"maintenance", "inactive", "available"}
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An occupied room cannot be changed to "
                "available, maintenance, or inactive."
            ),
        )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    room.room_number = final_room_number
    room.room_type = final_room_type
    room.status = final_status
    room.hospital_id = final_hospital_id
    room.department_id = final_department_id

    try:
        db.commit()
        db.refresh(room)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Room could not be updated because "
                "of a database constraint."
            ),
        )

    return room


# ============================================================
# DELETE ROOM
# ============================================================

@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    # --------------------------------------------------------
    # Lock room
    # --------------------------------------------------------

    room = db.scalar(
        select(RoomDB)
        .where(
            RoomDB.id == room_id
        )
        .with_for_update()
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    # --------------------------------------------------------
    # Do not delete a room containing beds
    # --------------------------------------------------------

    bed_exists = db.scalar(
        select(BedDB.id)
        .where(
            BedDB.room_id == room_id
        )
        .limit(1)
    )

    if bed_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Room cannot be deleted because "
                "it contains beds."
            ),
        )

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    try:
        db.delete(room)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Room cannot be deleted because "
                "it is referenced by another record."
            ),
        )

    return None