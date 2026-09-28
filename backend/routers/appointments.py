from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, time

from database import get_db
from utils.dependencies import get_current_user,require_role

from models.appointments import AppointmentDB
from models.users import UserDB
from models.patient import PatientDB
from models.doctor import DoctorDB
from models.employee import EmployeeDB
from models.doctorScedule import DoctorScheduleDB

from schema.appointments import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


# ============================================================
# AUTHORIZATION HELPERS
# ============================================================

def is_admin(user: UserDB) -> bool:
    return (
        user.account_type == "member"
        and user.role is not None
        and user.role.name.lower() == "admin"
    )


def has_role(user: UserDB, *roles: str) -> bool:
    if user.account_type != "member":
        return False

    if user.role is None:
        return False

    return user.role.name.lower() in {
        role.lower() for role in roles
    }

# ============================================================
# DOCTOR SCHEDULE VALIDATION
# ============================================================

def validate_doctor_schedule(
    db: Session,
    doctor_id: int,
    appointment_date,
    appointment_time,
):
    """
    Validate that the appointment falls within the
    doctor's recurring weekly working schedule.
    """

    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    selected_day = days[appointment_date.weekday()]

    schedules = db.scalars(
        select(DoctorScheduleDB)
        .where(
            DoctorScheduleDB.doctor_id == doctor_id,
            DoctorScheduleDB.day_of_week == selected_day,
        )
    ).all()

    if not schedules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"The doctor is not available on "
                f"{selected_day.capitalize()}."
            ),
        )

    is_available = any(
        schedule.start_time
        <= appointment_time
        < schedule.end_time
        for schedule in schedules
    )

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The selected appointment time is "
                "outside the doctor's working hours."
            ),
        )


def is_patient_owner(
    user: UserDB,
    patient_id: int,
) -> bool:
    """
    Check whether the authenticated user owns the
    requested patient record.
    """

    return (
        user.account_type == "patient"
        and user.patient is not None
        and user.patient.id == patient_id
    )


# ============================================================
# CREATE APPOINTMENT
# ============================================================
#
# Allowed:
#   Patient → can create appointment for themselves
#   Doctor  → can create appointment
#   Admin   → can create appointment
#
# Nurse/pharmacist/etc. cannot create appointments.
# ============================================================

@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    allowed = (
        is_admin(current_user)
        or has_role(current_user, "doctor")
        or has_role(current_user, "receptionist")
        or is_patient_owner(
            current_user,
            appointment_data.patient_id,
        )
    )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create this appointment.",
        )

    # --------------------------------------------------------
    # Patient ownership
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if not is_patient_owner(
            current_user,
            appointment_data.patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create appointments for yourself.",
            )

    # --------------------------------------------------------
    # Check patient
    # --------------------------------------------------------

    patient = db.get(
        PatientDB,
        appointment_data.patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Check doctor
    # --------------------------------------------------------

    doctor = db.get(
        DoctorDB,
        appointment_data.doctor_id,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found.",
        )
        # --------------------------------------------------------
    # Validate doctor working schedule
    # --------------------------------------------------------

    validate_doctor_schedule(
        db=db,
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
    )

    # --------------------------------------------------------
    # Check doctor scheduling conflict
    # --------------------------------------------------------

    existing_appointment = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id
            == appointment_data.doctor_id,
            AppointmentDB.appointment_date
            == appointment_data.appointment_date,
            AppointmentDB.appointment_time
            == appointment_data.appointment_time,
            AppointmentDB.status != "cancelled",
        )
        .first()
    )

    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The doctor already has an appointment "
                "at this date and time."
            ),
        )

    # --------------------------------------------------------
    # Create appointment
    # --------------------------------------------------------

    appointment = AppointmentDB(
        patient_id=appointment_data.patient_id,
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        reason=appointment_data.reason,
        status=appointment_data.status,
    )

    db.add(appointment)

    try:
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Appointment could not be created. "
                "Check patient, doctor, or appointment time."
            ),
        )

    return appointment


# ============================================================
# GET ALL APPOINTMENTS
# ============================================================
#
# Allowed:
#   Admin
#   Doctor
#
# Patients must use their own appointments endpoint through
# /patient/{patient_id}, where ownership is checked.
# ============================================================

@router.get(
    "/",
    response_model=list[AppointmentResponse],
)
def get_appointments(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not (
        is_admin(current_user)
        or has_role(current_user, "doctor")
        or has_role(current_user, "receptionist")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view all appointments.",
        )

    appointments = (
        db.query(AppointmentDB)
        .order_by(
            AppointmentDB.appointment_date,
            AppointmentDB.appointment_time,
        )
        .all()
    )

    return appointments



@router.get(
    "/doctor/me",
    response_model=list[AppointmentResponse],
    status_code=status.HTTP_200_OK,
)
def get_my_doctor_appointments(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("doctor")),
):
    # Find the employee belonging to the logged-in doctor account.
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

    # Find the doctor profile belonging to that employee.
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

    # Return only this doctor's appointments.
    appointments = db.scalars(
        select(AppointmentDB)
        .where(
            AppointmentDB.doctor_id == doctor.id
        )
        .order_by(
            AppointmentDB.appointment_date,
            AppointmentDB.appointment_time,
        )
    ).all()

    return appointments

# ============================================================
# GET BOOKED TIME SLOTS FOR DOCTOR
# ============================================================
#
# Patient can see which appointment times are already booked
# for a selected doctor and date.
#
# Only the appointment times are returned.
# Patient information is NOT exposed.
# ============================================================

@router.get(
    "/doctor/{doctor_id}/booked-slots",
    response_model=list[time],
    status_code=status.HTTP_200_OK,
)
def get_doctor_booked_slots(
    doctor_id: int,
    appointment_date: date,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Patient access
    # --------------------------------------------------------

    if current_user.account_type == "patient":
        pass

    elif not (
        is_admin(current_user)
        or has_role(current_user, "doctor")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view booked slots.",
        )

    # --------------------------------------------------------
    # Check doctor
    # --------------------------------------------------------

    doctor = db.get(
        DoctorDB,
        doctor_id,
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found.",
        )

    # --------------------------------------------------------
    # Get booked times
    #
    # Cancelled appointments do NOT block a slot.
    # --------------------------------------------------------

    booked_slots = db.scalars(
        select(AppointmentDB.appointment_time)
        .where(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.appointment_date == appointment_date,
            AppointmentDB.status != "cancelled",
        )
        .order_by(
            AppointmentDB.appointment_time
        )
    ).all()

    return booked_slots
# ============================================================
# GET APPOINTMENT BY ID
# ============================================================
#
# Allowed:
#   Admin
#   Doctor
#   Patient → own appointment
# ============================================================

@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    appointment = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.id == appointment_id
        )
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found.",
        )

    # --------------------------------------------------------
    # Patient ownership
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if not is_patient_owner(
            current_user,
            appointment.patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own appointment.",
            )

    # --------------------------------------------------------
    # Staff authorization
    # --------------------------------------------------------

    elif not (
        is_admin(current_user)
        or has_role(current_user, "doctor")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this appointment.",
        )

    return appointment


# ============================================================
# GET APPOINTMENTS FOR PATIENT
# ============================================================
#
# Patient:
#   Own appointments only
#
# Admin / Doctor:
#   Can view requested patient's appointments
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[AppointmentResponse],
)
def get_patient_appointments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Check patient
    # --------------------------------------------------------

    patient = db.get(
        PatientDB,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if not is_patient_owner(
            current_user,
            patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own appointments.",
            )

    elif not (
        is_admin(current_user)
        or has_role(current_user, "doctor")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view patient appointments.",
        )

    # --------------------------------------------------------
    # Fetch appointments
    # --------------------------------------------------------

    appointments = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.patient_id == patient_id
        )
        .order_by(
            AppointmentDB.appointment_date,
            AppointmentDB.appointment_time,
        )
        .all()
    )

    return appointments


# ============================================================
# UPDATE APPOINTMENT
# ============================================================
#
# Allowed:
#   Admin
#   Doctor
#   Patient → own appointment
#
# Patient is restricted from changing patient_id.
# ============================================================

@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    appointment = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.id == appointment_id
        )
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found.",
        )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    patient_owner = is_patient_owner(
        current_user,
        appointment.patient_id,
    )

    staff_user = (
        is_admin(current_user)
        or has_role(current_user, "doctor")
        or has_role(current_user, "receptionist")
    )

    if not (patient_owner or staff_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this appointment.",
        )

    update_data = appointment_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # Patient restrictions
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if "patient_id" in update_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change the patient of an appointment.",
            )

        if "doctor_id" in update_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change the doctor of an appointment.",
            )

        if "status" in update_data:
            # Patient may cancel but should not mark
            # appointment completed.
            if update_data["status"] != "cancelled":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Patients can only cancel appointments.",
                )

    # --------------------------------------------------------
    # Validate new patient
    # --------------------------------------------------------

    if "patient_id" in update_data:

        patient = db.get(
            PatientDB,
            update_data["patient_id"],
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

    # --------------------------------------------------------
    # Validate new doctor
    # --------------------------------------------------------

    if "doctor_id" in update_data:

        doctor = db.get(
            DoctorDB,
            update_data["doctor_id"],
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

    # --------------------------------------------------------
    # Determine final scheduling values
    # --------------------------------------------------------

    final_doctor_id = update_data.get(
        "doctor_id",
        appointment.doctor_id,
    )

    final_date = update_data.get(
        "appointment_date",
        appointment.appointment_date,
    )

    final_time = update_data.get(
        "appointment_time",
        appointment.appointment_time,
    )

        # --------------------------------------------------------
    # Validate doctor working schedule
    # --------------------------------------------------------

    validate_doctor_schedule(
        db=db,
        doctor_id=final_doctor_id,
        appointment_date=final_date,
        appointment_time=final_time,
    )

    # --------------------------------------------------------
    # Check scheduling conflict
    # --------------------------------------------------------

    conflicting_appointment = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == final_doctor_id,
            AppointmentDB.appointment_date == final_date,
            AppointmentDB.appointment_time == final_time,
            AppointmentDB.id != appointment_id,
            AppointmentDB.status != "cancelled",
        )
        .first()
    )

    if conflicting_appointment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The doctor already has another appointment "
                "at this date and time."
            ),
        )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            appointment,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appointment could not be updated.",
        )

    return appointment


# ============================================================
# DELETE APPOINTMENT
# ============================================================
#
# Admin only.
#
# Patients should cancel instead of deleting medical records.
# ============================================================

@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Admin only
    # --------------------------------------------------------

    if not (
        is_admin(current_user)
        or has_role(current_user, "receptionist")
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an administrator can delete an appointment.",
        )

    appointment = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.id == appointment_id
        )
        .first()
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found.",
        )

    try:
        db.delete(appointment)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appointment could not be deleted.",
        )

    return None