from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.vitals import VitalDB
from models.patient import PatientDB
from models.employee import EmployeeDB
from models.users import UserDB

from schema.vitals import (
    VitalCreate,
    VitalUpdate,
    VitalResponse,
)

from utils.dependencies import (
    get_current_user,
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/vitals",
    tags=["Vitals"],
)


# ============================================================
# CREATE VITAL
# ============================================================

@router.post(
    "/",
    response_model=VitalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vital(
    vital_data: VitalCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
        )
    ),
):
    # --------------------------------------------------------
    # Verify patient
    # --------------------------------------------------------

    patient = db.scalar(
        select(PatientDB).where(
            PatientDB.id == vital_data.patient_id
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Verify employee
    # --------------------------------------------------------

    employee = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.id == vital_data.recorded_by
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    # --------------------------------------------------------
    # Verify employee role
    # --------------------------------------------------------
    # Vital records should be recorded by appropriate clinical
    # staff, not arbitrary employees.
    #
    # We intentionally use EmployeeDB.role here.
    # We do NOT connect UserDB directly to EmployeeDB.
    # --------------------------------------------------------

    if employee.role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected employee does not have an assigned role.",
        )

    employee_role = employee.role.name.lower()

    if employee_role not in {
        "admin",
        "doctor",
        "nurse",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Vital records can only be recorded by "
                "admin, doctor, or nurse employees."
            ),
        )

    # --------------------------------------------------------
    # Create vital
    # --------------------------------------------------------

    vital = VitalDB(
        patient_id=vital_data.patient_id,
        recorded_by=vital_data.recorded_by,
        temperature=vital_data.temperature,
        heart_rate=vital_data.heart_rate,
        blood_pressure_systolic=(
            vital_data.blood_pressure_systolic
        ),
        blood_pressure_diastolic=(
            vital_data.blood_pressure_diastolic
        ),
        respiratory_rate=vital_data.respiratory_rate,
        oxygen_saturation=vital_data.oxygen_saturation,
        weight=vital_data.weight,
    )

    # --------------------------------------------------------
    # Only override the model default when the client
    # explicitly provides recorded_at.
    # --------------------------------------------------------

    if vital_data.recorded_at is not None:
        vital.recorded_at = vital_data.recorded_at

    db.add(vital)

    try:
        db.commit()
        db.refresh(vital)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to create vital record because "
                "of a database constraint."
            ),
        )

    return vital


# ============================================================
# GET ALL VITALS
# ============================================================

@router.get(
    "/",
    response_model=list[VitalResponse],
    status_code=status.HTTP_200_OK,
)
def get_vitals(
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
    vitals = db.scalars(
        select(VitalDB).order_by(
            VitalDB.recorded_at.desc(),
            VitalDB.id.desc(),
        )
    ).all()

    return vitals


# ============================================================
# GET PATIENT VITALS
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[VitalResponse],
    status_code=status.HTTP_200_OK,
)
def get_patient_vitals(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Verify patient
    # --------------------------------------------------------

    patient = db.scalar(
        select(PatientDB).where(
            PatientDB.id == patient_id
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Patient can only access their own records.
    #
    # Staff members with appropriate roles can access
    # any patient's records.
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if (
            current_user.patient is None
            or current_user.patient.id != patient_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own vital records.",
            )

    elif (
        current_user.account_type != "member"
        or current_user.role is None
        or current_user.role.name.lower()
        not in {
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        }
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "patient vital records."
            ),
        )

    # --------------------------------------------------------
    # Fetch vitals
    # --------------------------------------------------------

    vitals = db.scalars(
        select(VitalDB)
        .where(
            VitalDB.patient_id == patient_id
        )
        .order_by(
            VitalDB.recorded_at.desc(),
            VitalDB.id.desc(),
        )
    ).all()

    return vitals


# ============================================================
# GET VITALS RECORDED BY EMPLOYEE
# ============================================================

@router.get(
    "/employee/{employee_id}",
    response_model=list[VitalResponse],
    status_code=status.HTTP_200_OK,
)
def get_employee_vitals(
    employee_id: int,
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
    # --------------------------------------------------------
    # Verify employee
    # --------------------------------------------------------

    employee = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.id == employee_id
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    # --------------------------------------------------------
    # Fetch records
    # --------------------------------------------------------

    vitals = db.scalars(
        select(VitalDB)
        .where(
            VitalDB.recorded_by == employee_id
        )
        .order_by(
            VitalDB.recorded_at.desc(),
            VitalDB.id.desc(),
        )
    ).all()

    return vitals


# ============================================================
# GET SINGLE VITAL
# ============================================================

@router.get(
    "/{vital_id}",
    response_model=VitalResponse,
    status_code=status.HTTP_200_OK,
)
def get_vital(
    vital_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    vital = db.scalar(
        select(VitalDB).where(
            VitalDB.id == vital_id
        )
    )

    if vital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vital record not found.",
        )

    # --------------------------------------------------------
    # Patient can only view their own vital record.
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if (
            current_user.patient is None
            or current_user.patient.id != vital.patient_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own vital records.",
            )

    # --------------------------------------------------------
    # Staff authorization
    # --------------------------------------------------------

    elif (
        current_user.account_type != "member"
        or current_user.role is None
        or current_user.role.name.lower()
        not in {
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        }
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "this vital record."
            ),
        )

    return vital


# ============================================================
# UPDATE VITAL
# ============================================================

@router.patch(
    "/{vital_id}",
    response_model=VitalResponse,
    status_code=status.HTTP_200_OK,
)
def update_vital(
    vital_id: int,
    vital_data: VitalUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
        )
    ),
):
    # --------------------------------------------------------
    # Find vital
    # --------------------------------------------------------

    vital = db.scalar(
        select(VitalDB).where(
            VitalDB.id == vital_id
        )
    )

    if vital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vital record not found.",
        )

    # --------------------------------------------------------
    # Get only fields actually supplied by the client.
    # --------------------------------------------------------

    update_data = vital_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # --------------------------------------------------------
    # Validate patient if changed
    # --------------------------------------------------------

    if "patient_id" in update_data:

        patient = db.scalar(
            select(PatientDB).where(
                PatientDB.id == update_data["patient_id"]
            )
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

    # --------------------------------------------------------
    # Validate employee if changed
    # --------------------------------------------------------

    if "recorded_by" in update_data:

        employee = db.scalar(
            select(EmployeeDB).where(
                EmployeeDB.id == update_data["recorded_by"]
            )
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found.",
            )

        if employee.role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "The selected employee does not "
                    "have an assigned role."
                ),
            )

        employee_role = employee.role.name.lower()

        if employee_role not in {
            "admin",
            "doctor",
            "nurse",
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Vital records can only be recorded by "
                    "admin, doctor, or nurse employees."
                ),
            )

    # --------------------------------------------------------
    # Apply changes
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            vital,
            field,
            value,
        )

    # --------------------------------------------------------
    # Save changes
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(vital)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to update vital record because "
                "of a database constraint."
            ),
        )

    return vital


# ============================================================
# DELETE VITAL
# ============================================================

@router.delete(
    "/{vital_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vital(
    vital_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    vital = db.scalar(
        select(VitalDB).where(
            VitalDB.id == vital_id
        )
    )

    if vital is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vital record not found.",
        )

    try:
        db.delete(vital)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to delete vital record.",
        )

    return None