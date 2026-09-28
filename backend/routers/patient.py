from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select, distinct

from database import get_db
from models.patient import PatientDB
from models.users import UserDB
from models.employee import EmployeeDB
from models.doctor import DoctorDB
from models.appointments import AppointmentDB
from schema.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
)
from utils.dependencies import get_current_user,require_role
from utils.security import hash_password

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


def get_role_name(current_user):
    return (
        current_user.role.name.lower()
        if current_user.role
        else ""
    )


def is_staff(current_user):
    return (
        current_user.account_type.lower() == "member"
        and get_role_name(current_user) in {
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "pharmacist",
            "lab_technician",
        }
    )


def is_admin_or_receptionist(current_user):
    return (
        current_user.account_type.lower() == "member"
        and get_role_name(current_user) in {
            "admin",
            "receptionist",
        }
    )


def is_patient_owner(current_user, patient_id):
    return (
        current_user.account_type.lower() == "patient"
        and current_user.patient is not None
        and current_user.patient.id == patient_id
    )


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not is_admin_or_receptionist(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or receptionist can create patients.",
        )

    if not patient_data.email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An email is required to create a patient login account.",
        )

    existing_user = (
        db.query(UserDB)
        .filter(UserDB.email == patient_data.email)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # --------------------------------------------------------
    # Create a matching patient login account so the patient
    # can use the patient portal. Default demo password.
    # --------------------------------------------------------

    user = UserDB(
        name=patient_data.name,
        email=patient_data.email,
        password_hash=hash_password("Patient@123"),
        account_type="patient",
        role_id=None,
        is_active=True,
    )

    db.add(user)

    try:
        db.flush()

        patient = PatientDB(
            **patient_data.model_dump(),
            user_id=user.id,
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient could not be created.",
        )

    return patient


@router.get(
    "/",
    response_model=list[PatientResponse],
)
def get_patients(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not is_staff(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view all patients.",
        )

    return (
        db.query(PatientDB)
        .order_by(PatientDB.id)
        .all()
    )


@router.get(
    "/me",
    response_model=PatientResponse,
)
def get_my_patient_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Only patient accounts can use this endpoint
    if current_user.account_type.lower() != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access their own profile.",
        )

    # Check whether the logged-in user has a patient profile
    if current_user.patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    patient = (
        db.query(PatientDB)
        .filter(PatientDB.id == current_user.patient.id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found.",
        )

    return patient


@router.get(
    "/doctor/me",
    response_model=list[PatientResponse],
)
def get_my_patients(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("doctor")),
):
    # Find employee connected to logged-in doctor's account.
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

    # Find doctor profile.
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

    # Get patients who have appointments with this doctor.
    patients = db.scalars(
        select(PatientDB)
        .join(
            AppointmentDB,
            AppointmentDB.patient_id == PatientDB.id,
        )
        .where(
            AppointmentDB.doctor_id == doctor.id
        )
        .distinct()
        .order_by(PatientDB.id)
    ).all()

    return patients

@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not (
        is_staff(current_user)
        or is_patient_owner(current_user, patient_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this patient.",
        )

    patient = (
        db.query(PatientDB)
        .filter(PatientDB.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    return patient


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not (
        is_admin_or_receptionist(current_user)
        or is_patient_owner(current_user, patient_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this patient.",
        )

    patient = (
        db.query(PatientDB)
        .filter(PatientDB.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    update_data = patient_data.model_dump(
        exclude_unset=True
    )

    if is_patient_owner(current_user, patient_id):
        update_data.pop("user_id", None)

    for field, value in update_data.items():
        setattr(patient, field, value)

    try:
        db.commit()
        db.refresh(patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient could not be updated.",
        )

    return patient


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.account_type.lower() != "member" or get_role_name(current_user) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete patients.",
        )

    patient = (
        db.query(PatientDB)
        .filter(PatientDB.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    linked_user = db.query(UserDB).filter(UserDB.id == patient.user_id).first()

    db.delete(patient)
    # a patient always owns exactly one login user; delete it too so we
    # never leave behind an orphan "patient" account that cannot log in
    if linked_user is not None:
        db.delete(linked_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient cannot be deleted because the patient is referenced by existing records.",
        )

    return None