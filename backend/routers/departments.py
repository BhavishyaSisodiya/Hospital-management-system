from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.department import DepartmentDB
from models.hospital import HospitalDB
from models.users import UserDB

from schema.departments import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)

from utils.dependencies import (
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


# ============================================================
# CREATE DEPARTMENT
# ADMIN ONLY
# ============================================================

@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Create a new department.

    Only administrators can create departments.
    """

    # --------------------------------------------------------
    # CHECK HOSPITAL EXISTS
    # --------------------------------------------------------

    hospital = db.scalar(
        select(HospitalDB).where(
            HospitalDB.id == department_data.hospital_id
        )
    )

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found.",
        )

    # --------------------------------------------------------
    # CHECK DUPLICATE DEPARTMENT
    # --------------------------------------------------------

    existing_department = db.scalar(
        select(DepartmentDB).where(
            DepartmentDB.hospital_id == department_data.hospital_id,
            DepartmentDB.name == department_data.name,
        )
    )

    if existing_department is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Department with this name already exists "
                "in this hospital."
            ),
        )

    # --------------------------------------------------------
    # CREATE DEPARTMENT
    # --------------------------------------------------------

    department = DepartmentDB(
        name=department_data.name,
        description=department_data.description,
        hospital_id=department_data.hospital_id,
    )

    db.add(department)

    try:
        db.commit()
        db.refresh(department)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Department could not be created because "
                "of a database constraint."
            ),
        )

    return department


# ============================================================
# GET ALL DEPARTMENTS
# ADMIN / DOCTOR / NURSE / RECEPTIONIST
# ============================================================

@router.get(
    "/",
    response_model=list[DepartmentResponse],
    status_code=status.HTTP_200_OK,
)
def get_departments(
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
    Get all departments.
    """

    departments = db.scalars(
        select(DepartmentDB)
        .order_by(DepartmentDB.id)
    ).all()

    return departments


# ============================================================
# GET DEPARTMENTS BY HOSPITAL
# ADMIN / DOCTOR / NURSE / RECEPTIONIST
# ============================================================

@router.get(
    "/hospital/{hospital_id}",
    response_model=list[DepartmentResponse],
    status_code=status.HTTP_200_OK,
)
def get_departments_by_hospital(
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
    Get all departments belonging to a hospital.
    """

    # --------------------------------------------------------
    # CHECK HOSPITAL EXISTS
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
    # GET DEPARTMENTS
    # --------------------------------------------------------

    departments = db.scalars(
        select(DepartmentDB)
        .where(
            DepartmentDB.hospital_id == hospital_id
        )
        .order_by(DepartmentDB.id)
    ).all()

    return departments


# ============================================================
# GET DEPARTMENT BY ID
# ADMIN / DOCTOR / NURSE / RECEPTIONIST
# ============================================================

@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_department(
    department_id: int,
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
    Get a department by ID.
    """

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

    return department


# ============================================================
# UPDATE DEPARTMENT
# ADMIN ONLY
# ============================================================

@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Partially update a department.

    Only administrators can update departments.
    """

    # --------------------------------------------------------
    # FIND DEPARTMENT
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
    # GET SUPPLIED FIELDS
    # --------------------------------------------------------

    update_data = department_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # DETERMINE FINAL VALUES
    # --------------------------------------------------------

    new_name = update_data.get(
        "name",
        department.name,
    )

    new_hospital_id = update_data.get(
        "hospital_id",
        department.hospital_id,
    )

    # --------------------------------------------------------
    # CHECK NEW HOSPITAL
    # --------------------------------------------------------

    if "hospital_id" in update_data:

        hospital = db.scalar(
            select(HospitalDB).where(
                HospitalDB.id == new_hospital_id
            )
        )

        if hospital is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found.",
            )

    # --------------------------------------------------------
    # CHECK DUPLICATE DEPARTMENT
    # --------------------------------------------------------

    duplicate_department = db.scalar(
        select(DepartmentDB).where(
            DepartmentDB.name == new_name,
            DepartmentDB.hospital_id == new_hospital_id,
            DepartmentDB.id != department_id,
        )
    )

    if duplicate_department is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Department with this name already exists "
                "in this hospital."
            ),
        )

    # --------------------------------------------------------
    # APPLY CHANGES
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(department, field, value)

    # --------------------------------------------------------
    # SAVE CHANGES
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(department)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Department could not be updated because "
                "of a database constraint."
            ),
        )

    return department


# ============================================================
# DELETE DEPARTMENT
# ADMIN ONLY
# ============================================================

@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    """
    Permanently delete a department.

    Only administrators can delete departments.
    """

    # --------------------------------------------------------
    # FIND DEPARTMENT
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
    # DELETE DEPARTMENT
    # --------------------------------------------------------

    try:
        db.delete(department)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Department cannot be deleted because "
                "it is being used by other records."
            ),
        )

    return None
