from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from utils.dependencies import require_patient
from database import get_db
from models.doctor import DoctorDB
from models.doctorScedule import DoctorScheduleDB
from models.users import UserDB
from models.employee import EmployeeDB

from schema.doctor_schedule import (
    DoctorScheduleCreate,
    DoctorScheduleResponse,
    DoctorScheduleUpdate,
)
from utils.dependencies import require_admin, require_role


router = APIRouter(
    prefix="/doctor-schedules",
    tags=["Doctor Schedules"],
)


# ============================================================
# CREATE DOCTOR SCHEDULE
# ============================================================

@router.post(
    "/",
    response_model=DoctorScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor_schedule(
    schedule_data: DoctorScheduleCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # Verify that the doctor exists

    doctor = db.scalar(
        select(DoctorDB).where(
            DoctorDB.id == schedule_data.doctor_id
        )
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found.",
        )

    # Check for an existing schedule with the same
    # doctor, day and starting time

    existing_schedule = db.scalar(
        select(DoctorScheduleDB).where(
            DoctorScheduleDB.doctor_id == schedule_data.doctor_id,
            DoctorScheduleDB.day_of_week == schedule_data.day_of_week,
            DoctorScheduleDB.start_time == schedule_data.start_time,
        )
    )

    if existing_schedule is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A schedule already exists for this doctor "
                "on this day at this starting time."
            ),
        )

    # Create the schedule

    schedule = DoctorScheduleDB(
        doctor_id=schedule_data.doctor_id,
        day_of_week=schedule_data.day_of_week,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
    )

    db.add(schedule)

    # Save the schedule

    try:
        db.commit()
        db.refresh(schedule)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Doctor schedule could not be created "
                "because of a database constraint."
            ),
        )

    return schedule


# ============================================================
# GET SCHEDULES FOR A SPECIFIC DOCTOR
# ============================================================

@router.get(
    "/doctor/{doctor_id}",
    response_model=list[DoctorScheduleResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctor_schedule_by_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_patient),
):
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

    schedules = db.scalars(
        select(DoctorScheduleDB)
        .where(
            DoctorScheduleDB.doctor_id == doctor_id
        )
        .order_by(
            DoctorScheduleDB.day_of_week,
            DoctorScheduleDB.start_time,
            DoctorScheduleDB.id,
        )
    ).all()

    return schedules


# ============================================================
# GET ALL DOCTOR SCHEDULES
# ============================================================

@router.get(
    "/",
    response_model=list[DoctorScheduleResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctor_schedules(
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
    # Fetch all schedules in a predictable order

    schedules = db.scalars(
        select(DoctorScheduleDB).order_by(
            DoctorScheduleDB.doctor_id,
            DoctorScheduleDB.day_of_week,
            DoctorScheduleDB.start_time,
            DoctorScheduleDB.id,
        )
    ).all()

    return schedules

@router.get(
    "/me",
    response_model=list[DoctorScheduleResponse],
    status_code=status.HTTP_200_OK,
)
def get_my_schedule(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role("doctor")
    ),
):
    # --------------------------------------------------------
    # Find employee belonging to the logged-in user
    # --------------------------------------------------------
    employee = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.email == current_user.email
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found.",
        )

    # --------------------------------------------------------
    # Find doctor belonging to that employee
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
    # Get this doctor's schedules
    # --------------------------------------------------------
    schedules = db.scalars(
        select(DoctorScheduleDB)
        .where(
            DoctorScheduleDB.doctor_id == doctor.id
        )
        .order_by(
            DoctorScheduleDB.start_time,
            DoctorScheduleDB.id,
        )
    ).all()

    return schedules
# ============================================================
# GET DOCTOR SCHEDULE BY ID
# ============================================================

@router.get(
    "/{schedule_id}",
    response_model=DoctorScheduleResponse,
    status_code=status.HTTP_200_OK,
)
def get_doctor_schedule(
    schedule_id: int,
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
    # Find the schedule

    schedule = db.scalar(
        select(DoctorScheduleDB).where(
            DoctorScheduleDB.id == schedule_id
        )
    )

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor schedule not found.",
        )

    return schedule


# ============================================================
# UPDATE DOCTOR SCHEDULE
# ============================================================

@router.patch(
    "/{schedule_id}",
    response_model=DoctorScheduleResponse,
    status_code=status.HTTP_200_OK,
)
def update_doctor_schedule(
    schedule_id: int,
    schedule_data: DoctorScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # Find the existing schedule

    schedule = db.scalar(
        select(DoctorScheduleDB).where(
            DoctorScheduleDB.id == schedule_id
        )
    )

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor schedule not found.",
        )

    # Get only the fields supplied by the client

    update_data = schedule_data.model_dump(
        exclude_unset=True
    )

    # Nothing was supplied for update

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # Determine the final doctor ID

    final_doctor_id = update_data.get(
        "doctor_id",
        schedule.doctor_id,
    )

    # Determine the final day

    final_day = update_data.get(
        "day_of_week",
        schedule.day_of_week,
    )

    # Determine the final start time

    final_start_time = update_data.get(
        "start_time",
        schedule.start_time,
    )

    # Determine the final end time

    final_end_time = update_data.get(
        "end_time",
        schedule.end_time,
    )

    # Validate the final time range

    if final_end_time <= final_start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be later than start_time.",
        )

    # If doctor_id is changed, verify that the new doctor exists

    if "doctor_id" in update_data:
        doctor = db.scalar(
            select(DoctorDB).where(
                DoctorDB.id == final_doctor_id
            )
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

    # Prevent duplicate schedules

    existing_schedule = db.scalar(
        select(DoctorScheduleDB).where(
            DoctorScheduleDB.doctor_id == final_doctor_id,
            DoctorScheduleDB.day_of_week == final_day,
            DoctorScheduleDB.start_time == final_start_time,
            DoctorScheduleDB.id != schedule_id,
        )
    )

    if existing_schedule is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A schedule already exists for this doctor "
                "on this day at this starting time."
            ),
        )

    # Apply the requested changes

    for field, value in update_data.items():
        setattr(schedule, field, value)

    # Save changes

    try:
        db.commit()
        db.refresh(schedule)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Doctor schedule could not be updated "
                "because of a database constraint."
            ),
        )

    return schedule


# ============================================================
# DELETE DOCTOR SCHEDULE
# ============================================================

@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_doctor_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # Find the schedule

    schedule = db.scalar(
        select(DoctorScheduleDB).where(
            DoctorScheduleDB.id == schedule_id
        )
    )

    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor schedule not found.",
        )

    # Delete the schedule

    try:
        db.delete(schedule)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Doctor schedule could not be deleted.",
        )

    return None