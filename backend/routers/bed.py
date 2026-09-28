from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.bed import BedDB
from models.room import RoomDB
from models.admission import AdmissionDB

from schema.bed import (
    BedCreate,
    BedUpdate,
    BedResponse,
)

from utils.dependencies import (
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/beds",
    tags=["Beds"],
)


# ============================================================
# CREATE BED
# ============================================================

@router.post(
    "/",
    response_model=BedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bed(
    bed_data: BedCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    # --------------------------------------------------------
    # Validate room
    # --------------------------------------------------------

    room = db.scalar(
        select(RoomDB).where(
            RoomDB.id == bed_data.room_id
        )
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    # --------------------------------------------------------
    # Check duplicate bed number inside room
    # --------------------------------------------------------

    existing_bed = db.scalar(
        select(BedDB).where(
            BedDB.room_id == bed_data.room_id,
            BedDB.bed_number == bed_data.bed_number,
        )
    )

    if existing_bed is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bed number already exists in this room.",
        )

    # --------------------------------------------------------
    # Create bed
    # --------------------------------------------------------

    bed = BedDB(
        bed_number=bed_data.bed_number,
        room_id=bed_data.room_id,
        status=bed_data.status,
    )

    db.add(bed)

    try:
        db.commit()
        db.refresh(bed)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bed could not be created because of a database constraint.",
        )

    return bed


# ============================================================
# GET ALL BEDS
# ============================================================

@router.get(
    "/",
    response_model=list[BedResponse],
    status_code=status.HTTP_200_OK,
)
def get_beds(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):
    beds = db.scalars(
        select(BedDB).order_by(
            BedDB.room_id,
            BedDB.bed_number,
            BedDB.id,
        )
    ).all()

    return beds


# ============================================================
# GET BEDS BY ROOM
# ============================================================

@router.get(
    "/room/{room_id}",
    response_model=list[BedResponse],
    status_code=status.HTTP_200_OK,
)
def get_room_beds(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):
    # --------------------------------------------------------
    # Validate room
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Fetch beds
    # --------------------------------------------------------

    beds = db.scalars(
        select(BedDB)
        .where(
            BedDB.room_id == room_id
        )
        .order_by(
            BedDB.bed_number,
            BedDB.id,
        )
    ).all()

    return beds


# ============================================================
# GET AVAILABLE BEDS BY ROOM
# ============================================================

@router.get(
    "/room/{room_id}/available",
    response_model=list[BedResponse],
    status_code=status.HTTP_200_OK,
)
def get_available_beds(
    room_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):
    # --------------------------------------------------------
    # Validate room
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Fetch available beds
    # --------------------------------------------------------

    beds = db.scalars(
        select(BedDB)
        .where(
            BedDB.room_id == room_id,
            BedDB.status == "available",
        )
        .order_by(
            BedDB.bed_number,
            BedDB.id,
        )
    ).all()

    return beds


# ============================================================
# GET BED BY ID
# ============================================================

@router.get(
    "/{bed_id}",
    response_model=BedResponse,
    status_code=status.HTTP_200_OK,
)
def get_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):
    bed = db.scalar(
        select(BedDB).where(
            BedDB.id == bed_id
        )
    )

    if bed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bed not found.",
        )

    return bed


# ============================================================
# UPDATE BED
# ============================================================

@router.patch(
    "/{bed_id}",
    response_model=BedResponse,
    status_code=status.HTTP_200_OK,
)
def update_bed(
    bed_id: int,
    bed_data: BedUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    # --------------------------------------------------------
    # Lock the bed during update
    # --------------------------------------------------------

    bed = db.scalar(
        select(BedDB)
        .where(
            BedDB.id == bed_id
        )
        .with_for_update()
    )

    if bed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bed not found.",
        )

    update_data = bed_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # --------------------------------------------------------
    # Calculate final values
    # --------------------------------------------------------

    final_room_id = update_data.get(
        "room_id",
        bed.room_id,
    )

    final_bed_number = update_data.get(
        "bed_number",
        bed.bed_number,
    )

    final_status = update_data.get(
        "status",
        bed.status,
    )

    # --------------------------------------------------------
    # Validate room
    # --------------------------------------------------------

    room = db.scalar(
        select(RoomDB).where(
            RoomDB.id == final_room_id
        )
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    # --------------------------------------------------------
    # Check duplicate room + bed number
    # --------------------------------------------------------

    existing_bed = db.scalar(
        select(BedDB).where(
            BedDB.room_id == final_room_id,
            BedDB.bed_number == final_bed_number,
            BedDB.id != bed_id,
        )
    )

    if existing_bed is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bed number already exists in this room.",
        )

    # --------------------------------------------------------
    # Check active admission
    # --------------------------------------------------------

    active_admission = db.scalar(
        select(AdmissionDB).where(
            AdmissionDB.bed_id == bed_id,
            AdmissionDB.status == "admitted",
        )
    )

    # --------------------------------------------------------
    # Do not manually make an actively occupied bed available
    # or move it to another room while it has an admission.
    # --------------------------------------------------------

    if active_admission is not None:

        if final_status != "occupied":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This bed has an active admission and "
                    "cannot be changed from occupied status."
                ),
            )

        if final_room_id != bed.room_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A bed with an active admission cannot "
                    "be moved to another room."
                ),
            )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    bed.room_id = final_room_id
    bed.bed_number = final_bed_number
    bed.status = final_status

    try:
        db.commit()
        db.refresh(bed)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bed could not be updated because of a database constraint.",
        )

    return bed


# ============================================================
# DELETE BED
# ============================================================

@router.delete(
    "/{bed_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    # --------------------------------------------------------
    # Lock bed
    # --------------------------------------------------------

    bed = db.scalar(
        select(BedDB)
        .where(
            BedDB.id == bed_id
        )
        .with_for_update()
    )

    if bed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bed not found.",
        )

    # --------------------------------------------------------
    # Do not delete a bed currently used by an admission
    # --------------------------------------------------------

    existing_admission = db.scalar(
        select(AdmissionDB).where(
            AdmissionDB.bed_id == bed_id
        )
    )

    if existing_admission is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Bed cannot be deleted because it is "
                "referenced by an admission."
            ),
        )

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    try:
        db.delete(bed)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Bed cannot be deleted because it is "
                "referenced by another record."
            ),
        )

    return None