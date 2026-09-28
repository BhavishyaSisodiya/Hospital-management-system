from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.medical_record import MedicalRecordDB
from models.patient import PatientDB
from models.doctor import DoctorDB
from models.users import UserDB
from models.employee import EmployeeDB

from schema.medical_record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
)

from utils.dependencies import (
    get_current_user,
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"],
)


# ============================================================
# CREATE MEDICAL RECORD
# ============================================================

@router.post(
    "/",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_medical_record(
    record_data: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role("admin", "doctor")
    ),
):
    # --------------------------------------------------------
    # Verify that the patient exists
    # --------------------------------------------------------
    patient = db.scalar(
        select(PatientDB).where(
            PatientDB.id == record_data.patient_id
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Determine doctor
    # --------------------------------------------------------
    doctor_id = record_data.doctor_id

    if current_user.role.name.lower() == "doctor":
        # Find employee linked to logged-in doctor
        employee = db.scalar(
            select(EmployeeDB).where(
                EmployeeDB.email == current_user.email
            )
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found for this doctor.",
            )

        # Find doctor profile
        doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.employee_id == employee.id
            )
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found.",
            )

        # Never trust doctor_id supplied by frontend
        doctor_id = doctor.id

    else:
        # Admin can create a record for any valid doctor
        doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.id == doctor_id
            )
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

    # --------------------------------------------------------
    # Verify diagnosis
    # --------------------------------------------------------
    diagnosis = record_data.diagnosis.strip()

    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Diagnosis cannot be empty.",
        )

    # --------------------------------------------------------
    # Create medical record
    # --------------------------------------------------------
    medical_record = MedicalRecordDB(
        patient_id=record_data.patient_id,
        doctor_id=doctor_id,
        diagnosis=diagnosis,
        notes=record_data.notes,
        record_date=record_data.record_date,
    )

    db.add(medical_record)

    try:
        db.commit()
        db.refresh(medical_record)

    except IntegrityError as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to create medical record because "
                "of a database constraint."
            ),
        )

    return medical_record


@router.get(
    "/doctor/me",
    response_model=list[MedicalRecordResponse],
)
def get_my_doctor_medical_records(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("doctor")),
):
    employee = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.email == current_user.email
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this doctor.",
        )

    doctor = db.scalar(
        select(DoctorDB).where(
            DoctorDB.employee_id == employee.id
        )
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found.",
        )

    records = db.scalars(
        select(MedicalRecordDB)
        .where(
            MedicalRecordDB.doctor_id == doctor.id
        )
        .order_by(
            MedicalRecordDB.record_date.desc(),
            MedicalRecordDB.id.desc(),
        )
    ).all()

    return records

# ============================================================
# GET MEDICAL RECORDS BY PATIENT
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[MedicalRecordResponse],
    status_code=status.HTTP_200_OK,
)
def get_patient_medical_records(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # Verify that the patient exists

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

    # Patients can only access their own records

    if current_user.account_type == "patient":

        if (
            current_user.patient is None
            or current_user.patient.id != patient_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own medical records.",
            )

    # Staff members must have an allowed role

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
            detail="You do not have permission to view patient medical records.",
        )

    # Fetch patient medical records

    medical_records = db.scalars(
        select(MedicalRecordDB)
        .where(
            MedicalRecordDB.patient_id == patient_id
        )
        .order_by(
            MedicalRecordDB.record_date.desc(),
            MedicalRecordDB.id.desc(),
        )
    ).all()

    return medical_records


# ============================================================
# GET MEDICAL RECORDS BY DOCTOR
# ============================================================

@router.get(
    "/doctor/{doctor_id}",
    response_model=list[MedicalRecordResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctor_medical_records(
    doctor_id: int,
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
    # Verify that the doctor exists

    doctor = db.scalar(
        select(DoctorDB).where(
            DoctorDB.id == doctor_id
        )
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found.",
        )

    # Fetch records created by the specified doctor

    medical_records = db.scalars(
        select(MedicalRecordDB)
        .where(
            MedicalRecordDB.doctor_id == doctor_id
        )
        .order_by(
            MedicalRecordDB.record_date.desc(),
            MedicalRecordDB.id.desc(),
        )
    ).all()

    return medical_records


# ============================================================
# GET MEDICAL RECORD BY ID
# ============================================================

@router.get(
    "/{record_id}",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_200_OK,
)
def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # Find the medical record

    medical_record = db.scalar(
        select(MedicalRecordDB).where(
            MedicalRecordDB.id == record_id
        )
    )

    if medical_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found.",
        )

    # Patients can only view their own medical records

    if current_user.account_type == "patient":

        if (
            current_user.patient is None
            or current_user.patient.id
            != medical_record.patient_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own medical record.",
            )

    # Staff members must have an allowed role

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
            detail="You do not have permission to view this medical record.",
        )

    return medical_record


# ============================================================
# UPDATE MEDICAL RECORD
# ============================================================

@router.patch(
    "/{record_id}",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_200_OK,
)
def update_medical_record(
    record_id: int,
    record_data: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role("admin", "doctor")
    ),
):
    # Find the medical record

    medical_record = db.scalar(
        select(MedicalRecordDB).where(
            MedicalRecordDB.id == record_id
        )
    )

    if medical_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found.",
        )

    # Get only the fields supplied by the client

    update_data = record_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # Validate patient if patient_id is changed

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

    # Validate doctor if doctor_id is changed

    if "doctor_id" in update_data:

        doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.id == update_data["doctor_id"]
            )
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

    # Validate diagnosis if it is being changed

    if "diagnosis" in update_data:

        diagnosis = update_data["diagnosis"].strip()

        if not diagnosis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Diagnosis cannot be empty.",
            )

        update_data["diagnosis"] = diagnosis

    # Apply updates

    for field, value in update_data.items():
        setattr(
            medical_record,
            field,
            value,
        )

    # Save changes

    try:
        db.commit()
        db.refresh(medical_record)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update medical record because of a database constraint.",
        )

    return medical_record


# ============================================================
# DELETE MEDICAL RECORD
# ============================================================

@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # Find the medical record

    medical_record = db.scalar(
        select(MedicalRecordDB).where(
            MedicalRecordDB.id == record_id
        )
    )

    if medical_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found.",
        )

    # Delete the medical record

    try:
        db.delete(medical_record)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to delete medical record.",
        )

    return None