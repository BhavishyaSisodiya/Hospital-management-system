from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.lab import LabTestDB
from models.patient import PatientDB
from models.doctor import DoctorDB
from models.test import TestTypeDB
from models.employee import EmployeeDB
from models.users import UserDB

from schema.lab import (
    LabTestCreate,
    LabTestUpdate,
    LabTestResponse,
)

from utils.dependencies import (
    get_current_user,
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/lab-tests",
    tags=["Lab Tests"],
)


# ============================================================
# HELPER: VALIDATE LAB TECHNICIAN
# ============================================================

def validate_lab_technician(
    db: Session,
    technician_id: int,
) -> EmployeeDB:

    technician = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.id == technician_id
        )
    )

    if technician is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technician not found.",
        )

    if technician.employment_status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected employee is not an active employee.",
        )

    if technician.role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected employee does not have a role.",
        )

    if technician.role.name.lower() != "lab_technician":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected employee is not a Lab Technician.",
        )

    return technician


# ============================================================
# CREATE LAB TEST
# ============================================================

@router.post(
    "/",
    response_model=LabTestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lab_test(
    data: LabTestCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "lab_technician",
        )
    ),
):
    # --------------------------------------------------------
    # Validate patient
    # --------------------------------------------------------

    patient = db.scalar(
        select(PatientDB).where(
            PatientDB.id == data.patient_id
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Resolve doctor
    # --------------------------------------------------------

    role_name = (
        current_user.role.name.strip().lower()
        if current_user.role is not None
        else ""
    )

    if role_name == "doctor":

        employee = db.scalar(
            select(EmployeeDB).where(
                EmployeeDB.email
                == current_user.email
            )
        )

        if employee is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "Employee profile not found "
                    "for this doctor."
                ),
            )

        doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.employee_id
                == employee.id
            )
        )

        if doctor is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Doctor profile not found.",
            )

        doctor_id = doctor.id

    else:

        if data.doctor_id is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail="Doctor is required.",
            )

        doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.id == data.doctor_id
            )
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

        doctor_id = doctor.id

    # --------------------------------------------------------
    # Validate test type
    # --------------------------------------------------------

    test_type = db.scalar(
        select(TestTypeDB).where(
            TestTypeDB.id == data.test_type_id
        )
    )

    if test_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test type not found.",
        )

    # --------------------------------------------------------
    # Validate technician (optional)
    # --------------------------------------------------------

    if data.technician_id is not None:

        validate_lab_technician(
            db,
            data.technician_id,
        )

    # --------------------------------------------------------
    # Create lab test
    # --------------------------------------------------------

    lab_test = LabTestDB(
        test_type_id=data.test_type_id,
        patient_id=data.patient_id,
        doctor_id=doctor_id,
        technician_id=data.technician_id,
    )

    # Only assign optional test_date when supplied.
    # Otherwise the model's UTC default is used.
    if data.test_date is not None:
        lab_test.test_date = data.test_date

    lab_test.status = data.status

    db.add(lab_test)

    try:
        db.commit()
        db.refresh(lab_test)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Lab test could not be created because "
                "of a database constraint."
            ),
        )

    return lab_test


# ============================================================
# GET ALL LAB TESTS
# ============================================================

@router.get(
    "/",
    response_model=list[LabTestResponse],
    status_code=status.HTTP_200_OK,
)
def get_lab_tests(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Staff access
    # --------------------------------------------------------

    if (
        current_user.account_type == "member"
        and current_user.role is not None
        and current_user.role.name.lower()
        in {
            "admin",
            "doctor",
            "nurse",
            "lab_technician",
            "receptionist",
        }
    ):
        return db.scalars(
            select(LabTestDB).order_by(
                LabTestDB.test_date.desc()
            )
        ).all()

    # --------------------------------------------------------
    # Patient access
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if current_user.patient is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patient profile not found.",
            )

        return db.scalars(
            select(LabTestDB)
            .where(
                LabTestDB.patient_id
                == current_user.patient.id
            )
            .order_by(
                LabTestDB.test_date.desc()
            )
        ).all()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view lab tests.",
    )


# ============================================================
# GET LAB TEST BY ID
# ============================================================

@router.get(
    "/{lab_test_id}",
    response_model=LabTestResponse,
    status_code=status.HTTP_200_OK,
)
def get_lab_test(
    lab_test_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    lab_test = db.scalar(
        select(LabTestDB).where(
            LabTestDB.id == lab_test_id
        )
    )

    if lab_test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab test not found.",
        )

    # --------------------------------------------------------
    # Staff access
    # --------------------------------------------------------

    if (
        current_user.account_type == "member"
        and current_user.role is not None
        and current_user.role.name.lower()
        in {
            "admin",
            "doctor",
            "nurse",
            "lab_technician",
            "receptionist",
        }
    ):
        return lab_test

    # --------------------------------------------------------
    # Patient can view own test
    # --------------------------------------------------------

    if (
        current_user.account_type == "patient"
        and current_user.patient is not None
        and lab_test.patient_id
        == current_user.patient.id
    ):
        return lab_test

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view this lab test.",
    )


# ============================================================
# UPDATE LAB TEST
# ============================================================

@router.patch(
    "/{lab_test_id}",
    response_model=LabTestResponse,
    status_code=status.HTTP_200_OK,
)
def update_lab_test(
    lab_test_id: int,
    data: LabTestUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "lab_technician",
        )
    ),
):
    # --------------------------------------------------------
    # Find lab test
    # --------------------------------------------------------

    lab_test = db.scalar(
        select(LabTestDB).where(
            LabTestDB.id == lab_test_id
        )
    )

    if lab_test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab test not found.",
        )

    # --------------------------------------------------------
    # Get supplied fields
    # --------------------------------------------------------

    update_data = data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # --------------------------------------------------------
    # Validate patient
    # --------------------------------------------------------

    if "patient_id" in update_data:

        patient = db.scalar(
            select(PatientDB).where(
                PatientDB.id
                == update_data["patient_id"]
            )
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

    # --------------------------------------------------------
    # Validate doctor
    # --------------------------------------------------------

    if "doctor_id" in update_data:

        doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.id
                == update_data["doctor_id"]
            )
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

    # --------------------------------------------------------
    # Validate test type
    # --------------------------------------------------------

    if "test_type_id" in update_data:

        test_type = db.scalar(
            select(TestTypeDB).where(
                TestTypeDB.id
                == update_data["test_type_id"]
            )
        )

        if test_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test type not found.",
            )

    # --------------------------------------------------------
    # Validate technician
    # --------------------------------------------------------

    if "technician_id" in update_data:

        technician_id = update_data[
            "technician_id"
        ]

        if technician_id is not None:

            validate_lab_technician(
                db,
                technician_id,
            )

    # --------------------------------------------------------
    # Apply changes
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            lab_test,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(lab_test)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Lab test could not be updated because "
                "of a database constraint."
            ),
        )

    return lab_test


# ============================================================
# DELETE LAB TEST
# ============================================================

@router.delete(
    "/{lab_test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_lab_test(
    lab_test_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    lab_test = db.scalar(
        select(LabTestDB).where(
            LabTestDB.id == lab_test_id
        )
    )

    if lab_test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab test not found.",
        )

    db.delete(lab_test)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Lab test cannot be deleted because "
                "it is referenced by other records."
            ),
        )

    return None