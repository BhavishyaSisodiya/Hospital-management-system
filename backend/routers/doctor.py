from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.doctor import DoctorDB
from models.employee import EmployeeDB
from models.role import RoleDB
from models.users import UserDB
from models.appointments import AppointmentDB

from schema.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorPublicResponse,
)
from schema.appointments import (
    AppointmentBase,
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)

from utils.dependencies import (
    require_admin,
    require_role,
    require_patient,
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def serialize_doctor(doctor: DoctorDB) -> dict:
    """
    Build a flat response dict that includes the linked
    employee + department information.
    """
    employee = getattr(doctor, "employee", None)
    department = (
        getattr(employee, "department", None)
        if employee is not None
        else None
    )

    return {
        "id": doctor.id,
        "employee_id": doctor.employee_id,
        "name": employee.name if employee is not None else "",
        "email": employee.email if employee is not None else None,
        "phone": employee.phone if employee is not None else None,
        "department_id": (
            employee.department_id
            if employee is not None
            else None
        ),
        "department_name": (
            department.name
            if department is not None
            else None
        ),
        "specialization": doctor.specialization,
        "experience_years": doctor.experience_years,
    }


def get_doctor_role(db: Session) -> RoleDB:
    """
    Fetch the canonical "doctor" role.
    """
    role = db.scalar(
        select(RoleDB).where(
            func.lower(RoleDB.name) == "doctor"
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Doctor role is not configured.",
        )

    return role


# ============================================================
# CREATE DOCTOR
# ============================================================

@router.post(
    "/",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # --------------------------------------------------------
    # Case 1: link to an existing employee
    # --------------------------------------------------------

    if doctor_data.employee_id is not None:

        employee = db.scalar(
            select(EmployeeDB).where(
                EmployeeDB.id == doctor_data.employee_id
            )
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found.",
            )

        # Make sure the employee has the doctor role
        if (
            employee.role is None
            or employee.role.name.lower() != "doctor"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected employee does not have the doctor role.",
            )

        # Check whether this employee is already registered
        existing_doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.employee_id == doctor_data.employee_id
            )
        )

        if existing_doctor is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This employee is already registered as a doctor.",
            )

    # --------------------------------------------------------
    # Case 2: create a brand-new employee + doctor
    # --------------------------------------------------------

    else:

        if not doctor_data.name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Doctor name is required.",
            )

        if doctor_data.department_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Department is required for a new doctor.",
            )

        if doctor_data.email:
            existing_email = db.scalar(
                select(EmployeeDB).where(
                    func.lower(EmployeeDB.email)
                    == doctor_data.email.lower()
                )
            )

            if existing_email is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An employee with this email already exists.",
                )

        doctor_role = get_doctor_role(db)

        employee = EmployeeDB(
            name=doctor_data.name.strip(),
            role_id=doctor_role.id,
            department_id=doctor_data.department_id,
            email=doctor_data.email,
            phone=doctor_data.phone,
            hire_date=date.today(),
            employment_status="active",
        )

        db.add(employee)
        db.flush()

    # --------------------------------------------------------
    # Create doctor record
    # --------------------------------------------------------

    new_doctor = DoctorDB(
        employee_id=employee.id,
        specialization=doctor_data.specialization,
        experience_years=doctor_data.experience_years,
    )

    db.add(new_doctor)

    # --------------------------------------------------------
    # Save doctor to database
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(new_doctor)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Doctor could not be created because "
                "of a database constraint."
            ),
        )

    return serialize_doctor(new_doctor)


# ============================================================
# GET ALL DOCTORS
# ============================================================

@router.get(
    "/",
    response_model=list[DoctorResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctors(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "pharmacist",
            "lab_technician",
        )
    ),
):
    # --------------------------------------------------------
    # Fetch all doctors ordered by name
    # --------------------------------------------------------

    doctors = db.scalars(
        select(DoctorDB)
        .join(
            EmployeeDB,
            DoctorDB.employee_id == EmployeeDB.id,
        )
        .order_by(EmployeeDB.name)
    ).all()

    return [
        serialize_doctor(doctor)
        for doctor in doctors
    ]


# ============================================================
# GET DOCTOR BY EMPLOYEE ID
# ============================================================

@router.get(
    "/employee/{employee_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def get_doctor_by_employee(
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
    # Find doctor using employee ID
    # --------------------------------------------------------

    doctor = db.scalar(
        select(DoctorDB).where(
            DoctorDB.employee_id == employee_id
        )
    )

    # --------------------------------------------------------
    # Return 404 if doctor does not exist
    # --------------------------------------------------------

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor record not found for this employee.",
        )

    return serialize_doctor(doctor)

@router.get(
    "/me",
    response_model=list[AppointmentResponse],
    status_code=status.HTTP_200_OK,
)
def get_my_doctor_appointments(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role("doctor")
    ),
):
    # --------------------------------------------------------
    # Find the employee belonging to the logged-in doctor
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # Make sure this employee is actually registered
    # as a doctor
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # Get ONLY this doctor's appointments
    # --------------------------------------------------------
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
# GET AVAILABLE DOCTORS FOR PATIENTS
# ============================================================


@router.get(
    "/available",
    response_model=list[DoctorPublicResponse],
    status_code=status.HTTP_200_OK,
)
def get_available_doctors(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_patient),
):
    doctors = db.scalars(
        select(DoctorDB)
        .join(
            EmployeeDB,
            DoctorDB.employee_id == EmployeeDB.id,
        )
        .where(
            EmployeeDB.employment_status == "active"
        )
        .order_by(EmployeeDB.name)
    ).all()

    return [
        DoctorPublicResponse(
            id=doctor.id,
            name=doctor.employee.name,
            specialization=doctor.specialization,
            experience_years=doctor.experience_years,
        )
        for doctor in doctors
    ]
# ============================================================
# GET DOCTOR BY ID
# ============================================================


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def get_doctor(
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
    # --------------------------------------------------------
    # Find doctor by doctor ID
    # --------------------------------------------------------

    doctor = db.scalar(
        select(DoctorDB).where(
            DoctorDB.id == doctor_id
        )
    )

    # --------------------------------------------------------
    # Return 404 if doctor does not exist
    # --------------------------------------------------------

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found.",
        )

    return serialize_doctor(doctor)


# ============================================================
# UPDATE DOCTOR
# ============================================================

@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # --------------------------------------------------------
    # Find existing doctor
    # --------------------------------------------------------

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

    employee = doctor.employee

    # --------------------------------------------------------
    # Get only fields supplied by the client
    # --------------------------------------------------------

    update_data = doctor_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    # --------------------------------------------------------
    # Employee re-link
    # --------------------------------------------------------

    if "employee_id" in update_data:

        new_employee_id = update_data["employee_id"]

        new_employee = db.scalar(
            select(EmployeeDB).where(
                EmployeeDB.id == new_employee_id
            )
        )

        if new_employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found.",
            )

        # New employee must have doctor role
        if (
            new_employee.role is None
            or new_employee.role.name.lower() != "doctor"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected employee does not have the doctor role.",
            )

        # Check whether another doctor already uses this employee
        existing_doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.employee_id == new_employee_id,
                DoctorDB.id != doctor_id,
            )
        )

        if existing_doctor is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This employee is already registered "
                    "as a doctor."
                ),
            )

        doctor.employee_id = new_employee_id
        employee = new_employee

    # --------------------------------------------------------
    # Employee-level fields
    # --------------------------------------------------------

    if "name" in update_data:
        employee.name = update_data["name"].strip()

    if "email" in update_data:
        new_email = update_data["email"]

        if new_email:
            duplicate = db.scalar(
                select(EmployeeDB).where(
                    EmployeeDB.email == new_email,
                    EmployeeDB.id != employee.id,
                )
            )

            if duplicate is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another employee already uses this email.",
                )

        employee.email = new_email

    if "phone" in update_data:
        employee.phone = update_data["phone"]

    if "department_id" in update_data:
        employee.department_id = update_data["department_id"]

    # --------------------------------------------------------
    # Doctor-level fields
    # --------------------------------------------------------

    doctor_fields = ("specialization", "experience_years")

    for field in doctor_fields:
        if field in update_data:
            setattr(doctor, field, update_data[field])

    # --------------------------------------------------------
    # Save changes
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(doctor)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Doctor could not be updated because "
                "of a database constraint."
            ),
        )

    return serialize_doctor(doctor)


# ============================================================
# DELETE DOCTOR
# ============================================================

@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # --------------------------------------------------------
    # Find doctor
    # --------------------------------------------------------

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
    # Delete doctor
    # --------------------------------------------------------

    try:
        db.delete(doctor)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Doctor cannot be deleted because "
                "the doctor is referenced by other records."
            ),
        )

    return None
