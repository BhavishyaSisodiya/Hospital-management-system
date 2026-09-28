from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.hospital import HospitalDB
from models.users import UserDB

from schema.hospital import (
    HospitalCreate,
    HospitalUpdate,
    HospitalResponse,
)

from utils.dependencies import (
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"],
)


# ============================================================
# CREATE HOSPITAL
# ADMIN ONLY
# ============================================================

@router.post(
    "/",
    response_model=HospitalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Create a new hospital.

    Only administrators can create hospitals.
    """

    # --------------------------------------------------------
    # CHECK DUPLICATE EMAIL
    # --------------------------------------------------------

    existing_hospital = db.scalar(
        select(HospitalDB).where(
            HospitalDB.email == hospital_data.email
        )
    )

    if existing_hospital is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A hospital with this email already exists.",
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE PHONE
    # --------------------------------------------------------

    existing_hospital = db.scalar(
        select(HospitalDB).where(
            HospitalDB.phone == hospital_data.phone
        )
    )

    if existing_hospital is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A hospital with this phone number already exists.",
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE NAME
    # --------------------------------------------------------

    existing_hospital = db.scalar(
        select(HospitalDB).where(
            HospitalDB.name == hospital_data.name
        )
    )

    if existing_hospital is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A hospital with this name already exists.",
        )

    # --------------------------------------------------------
    # CREATE HOSPITAL
    # --------------------------------------------------------

    hospital = HospitalDB(
        name=hospital_data.name,
        address=hospital_data.address,
        phone=hospital_data.phone,
        email=hospital_data.email,
    )

    db.add(hospital)

    try:
        db.commit()
        db.refresh(hospital)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Hospital could not be created because "
                "of a database constraint."
            ),
        )

    return hospital


# ============================================================
# GET ALL HOSPITALS
# ADMIN / DOCTOR / NURSE / RECEPTIONIST
# ============================================================

@router.get(
    "/",
    response_model=list[HospitalResponse],
    status_code=status.HTTP_200_OK,
)
def get_hospitals(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):
    """
    Get all hospitals.

    Allowed roles:
        admin
        doctor
        nurse
        receptionist
    """

    hospitals = db.scalars(
        select(HospitalDB)
        .order_by(HospitalDB.id)
    ).all()

    return hospitals


# ============================================================
# GET HOSPITAL BY ID
# ADMIN / DOCTOR / NURSE / RECEPTIONIST
# ============================================================

@router.get(
    "/{hospital_id}",
    response_model=HospitalResponse,
    status_code=status.HTTP_200_OK,
)
def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):
    """
    Get a hospital by ID.
    """

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

    return hospital


# ============================================================
# UPDATE HOSPITAL
# ADMIN ONLY
# ============================================================

@router.patch(
    "/{hospital_id}",
    response_model=HospitalResponse,
    status_code=status.HTTP_200_OK,
)
def update_hospital(
    hospital_id: int,
    hospital_data: HospitalUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Partially update a hospital.

    Only administrators can update hospitals.
    """

    # --------------------------------------------------------
    # FIND HOSPITAL
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
    # GET SUPPLIED FIELDS
    # --------------------------------------------------------

    update_data = hospital_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # CHECK DUPLICATE NAME
    # --------------------------------------------------------

    if "name" in update_data:

        existing_hospital = db.scalar(
            select(HospitalDB).where(
                HospitalDB.name == update_data["name"],
                HospitalDB.id != hospital_id,
            )
        )

        if existing_hospital is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another hospital already uses this name.",
            )

    # --------------------------------------------------------
    # CHECK DUPLICATE EMAIL
    # --------------------------------------------------------

    if "email" in update_data:

        existing_hospital = db.scalar(
            select(HospitalDB).where(
                HospitalDB.email == update_data["email"],
                HospitalDB.id != hospital_id,
            )
        )

        if existing_hospital is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another hospital already uses this email.",
            )

    # --------------------------------------------------------
    # CHECK DUPLICATE PHONE
    # --------------------------------------------------------

    if "phone" in update_data:

        existing_hospital = db.scalar(
            select(HospitalDB).where(
                HospitalDB.phone == update_data["phone"],
                HospitalDB.id != hospital_id,
            )
        )

        if existing_hospital is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Another hospital already uses "
                    "this phone number."
                ),
            )

    # --------------------------------------------------------
    # APPLY CHANGES
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(hospital, field, value)

    # --------------------------------------------------------
    # SAVE CHANGES
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(hospital)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Hospital could not be updated because "
                "of a database constraint."
            ),
        )

    return hospital


# ============================================================
# DELETE HOSPITAL
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{hospital_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Permanently delete a hospital.

    Only administrators can delete hospitals.
    """

    # --------------------------------------------------------
    # FIND HOSPITAL
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
    # DELETE HOSPITAL
    # --------------------------------------------------------

    try:
        db.delete(hospital)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Hospital cannot be deleted because "
                "other records depend on this hospital."
            ),
        )

    return None
