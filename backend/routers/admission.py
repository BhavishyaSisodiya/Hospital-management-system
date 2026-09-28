from fastapi import APIRouter, Depends, HTTPException, status

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.admission import AdmissionDB
from models.patient import PatientDB
from models.doctor import DoctorDB
from models.bed import BedDB
from models.users import UserDB

from schema.admission import (
    AdmissionCreate,
    AdmissionUpdate,
    AdmissionResponse,
)

from utils.dependencies import (
    get_current_user,
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/admissions",
    tags=["Admissions"],
)


# ============================================================
# CREATE ADMISSION
# ============================================================

@router.post(
    "/",
    response_model=AdmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_admission(
    admission_data: AdmissionCreate,
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
    # Verify patient
    # --------------------------------------------------------

    patient = db.scalar(
        select(PatientDB).where(
            PatientDB.id == admission_data.patient_id
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Verify doctor
    # --------------------------------------------------------

    doctor = db.scalar(
        select(DoctorDB).where(
            DoctorDB.id == admission_data.doctor_id
        )
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found.",
        )

    # --------------------------------------------------------
    # Lock the bed during this transaction.
    #
    # This prevents two concurrent requests from both seeing
    # the same bed as available.
    # --------------------------------------------------------

    bed = db.scalar(
        select(BedDB)
        .where(
            BedDB.id == admission_data.bed_id
        )
        .with_for_update()
    )

    if bed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bed not found.",
        )

    # --------------------------------------------------------
    # Only an available bed can be used for a new admission.
    # --------------------------------------------------------

    if bed.status != "available":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Selected bed is not available.",
        )

    # --------------------------------------------------------
    # Prevent another active admission from using this bed.
    # --------------------------------------------------------

    active_admission = db.scalar(
        select(AdmissionDB)
        .where(
            AdmissionDB.bed_id == admission_data.bed_id,
            AdmissionDB.status == "admitted",
        )
    )

    if active_admission is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Selected bed is already assigned to an active admission.",
        )

    # --------------------------------------------------------
    # Create admission
    # --------------------------------------------------------

    admission = AdmissionDB(
        patient_id=admission_data.patient_id,
        doctor_id=admission_data.doctor_id,
        bed_id=admission_data.bed_id,
        admission_date=admission_data.admission_date,
        discharge_date=admission_data.discharge_date,
        status=admission_data.status,
    )

    db.add(admission)

    # --------------------------------------------------------
    # Update bed status
    # --------------------------------------------------------

    if admission_data.status == "admitted":
        bed.status = "occupied"

    elif admission_data.status in {
        "discharged",
        "cancelled",
    }:
        bed.status = "available"

    # --------------------------------------------------------
    # Commit admission + bed change together.
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(admission)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to create admission because "
                "of a database constraint."
            ),
        )

    return admission


# ============================================================
# GET ALL ADMISSIONS
# ============================================================

@router.get(
    "/",
    response_model=list[AdmissionResponse],
    status_code=status.HTTP_200_OK,
)
def get_admissions(
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
    admissions = db.scalars(
        select(AdmissionDB)
        .order_by(
            AdmissionDB.admission_date.desc(),
            AdmissionDB.id.desc(),
        )
    ).all()

    return admissions


# ============================================================
# GET ADMISSION BY ID
# ============================================================

@router.get(
    "/{admission_id}",
    response_model=AdmissionResponse,
    status_code=status.HTTP_200_OK,
)
def get_admission(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    admission = db.scalar(
        select(AdmissionDB).where(
            AdmissionDB.id == admission_id
        )
    )

    if admission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission not found.",
        )

    # --------------------------------------------------------
    # Staff access
    # --------------------------------------------------------

    if current_user.account_type == "member":

        if (
            current_user.role is None
            or current_user.role.name.lower()
            not in {
                "admin",
                "doctor",
                "nurse",
            }
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission to "
                    "view this admission."
                ),
            )

        return admission

    # --------------------------------------------------------
    # Patient can only view own admission
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if (
            current_user.patient is None
            or current_user.patient.id != admission.patient_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own admission.",
            )

        return admission

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view this admission.",
    )


# ============================================================
# GET ADMISSIONS FOR PATIENT
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[AdmissionResponse],
    status_code=status.HTTP_200_OK,
)
def get_patient_admissions(
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
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if (
            current_user.patient is None
            or current_user.patient.id != patient_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own admissions.",
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
        }
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to "
                "view patient admissions."
            ),
        )

    admissions = db.scalars(
        select(AdmissionDB)
        .where(
            AdmissionDB.patient_id == patient_id
        )
        .order_by(
            AdmissionDB.admission_date.desc(),
            AdmissionDB.id.desc(),
        )
    ).all()

    return admissions


# ============================================================
# GET ADMISSIONS FOR DOCTOR
# ============================================================

@router.get(
    "/doctor/{doctor_id}",
    response_model=list[AdmissionResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctor_admissions(
    doctor_id: int,
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
    # Verify doctor
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

    admissions = db.scalars(
        select(AdmissionDB)
        .where(
            AdmissionDB.doctor_id == doctor_id
        )
        .order_by(
            AdmissionDB.admission_date.desc(),
            AdmissionDB.id.desc(),
        )
    ).all()

    return admissions


# ============================================================
# UPDATE ADMISSION
# ============================================================

@router.patch(
    "/{admission_id}",
    response_model=AdmissionResponse,
    status_code=status.HTTP_200_OK,
)
def update_admission(
    admission_id: int,
    admission_data: AdmissionUpdate,
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
    # Find admission
    # --------------------------------------------------------

    admission = db.scalar(
        select(AdmissionDB)
        .where(
            AdmissionDB.id == admission_id
        )
        .with_for_update()
    )

    if admission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission not found.",
        )

    # --------------------------------------------------------
    # Get supplied fields only
    # --------------------------------------------------------

    update_data = admission_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # --------------------------------------------------------
    # Calculate final values before changing the database
    # object.
    # --------------------------------------------------------

    final_patient_id = update_data.get(
        "patient_id",
        admission.patient_id,
    )

    final_doctor_id = update_data.get(
        "doctor_id",
        admission.doctor_id,
    )

    final_bed_id = update_data.get(
        "bed_id",
        admission.bed_id,
    )

    final_admission_date = update_data.get(
        "admission_date",
        admission.admission_date,
    )

    final_discharge_date = update_data.get(
        "discharge_date",
        admission.discharge_date,
    )

    final_status = update_data.get(
        "status",
        admission.status,
    )

    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------

    if (
        final_discharge_date is not None
        and final_discharge_date < final_admission_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "discharge_date must be greater than "
                "or equal to admission_date."
            ),
        )

    # --------------------------------------------------------
    # Validate status + discharge date
    # --------------------------------------------------------

    if (
        final_status == "admitted"
        and final_discharge_date is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "An admitted admission cannot have "
                "a discharge_date."
            ),
        )

    if (
        final_status == "discharged"
        and final_discharge_date is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "A discharged admission must have "
                "a discharge_date."
            ),
        )

    # --------------------------------------------------------
    # Verify patient
    # --------------------------------------------------------

    if "patient_id" in update_data:

        patient = db.scalar(
            select(PatientDB).where(
                PatientDB.id == final_patient_id
            )
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

    # --------------------------------------------------------
    # Verify doctor
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Handle bed changes
    # --------------------------------------------------------

    if (
        final_bed_id != admission.bed_id
        or final_status == "admitted"
    ):

        # ----------------------------------------------------
        # Lock selected bed.
        # ----------------------------------------------------

        new_bed = db.scalar(
            select(BedDB)
            .where(
                BedDB.id == final_bed_id
            )
            .with_for_update()
        )

        if new_bed is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bed not found.",
            )

        # ----------------------------------------------------
        # If admission will be active, the new bed must
        # be available unless it is already this admission's
        # current bed.
        # ----------------------------------------------------

        if final_status == "admitted":

            if (
                final_bed_id != admission.bed_id
                and new_bed.status != "available"
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Selected bed is not available.",
                )

            # ------------------------------------------------
            # Prevent another active admission from using
            # the same bed.
            # ------------------------------------------------

            existing_admission = db.scalar(
                select(AdmissionDB)
                .where(
                    AdmissionDB.bed_id == final_bed_id,
                    AdmissionDB.status == "admitted",
                    AdmissionDB.id != admission.id,
                )
            )

            if existing_admission is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Selected bed is already assigned "
                        "to another active admission."
                    ),
                )

        # ----------------------------------------------------
        # Release old bed if changing beds.
        # ----------------------------------------------------

        if final_bed_id != admission.bed_id:

            old_bed = db.scalar(
                select(BedDB)
                .where(
                    BedDB.id == admission.bed_id
                )
                .with_for_update()
            )

            if old_bed is not None:
                old_bed.status = "available"

        # ----------------------------------------------------
        # Set new bed status.
        # ----------------------------------------------------

        if final_status == "admitted":
            new_bed.status = "occupied"
        else:
            new_bed.status = "available"

    else:
        # ----------------------------------------------------
        # Same bed, status may have changed.
        # ----------------------------------------------------

        bed = db.scalar(
            select(BedDB)
            .where(
                BedDB.id == admission.bed_id
            )
            .with_for_update()
        )

        if bed is not None:

            if final_status == "admitted":

                existing_admission = db.scalar(
                    select(AdmissionDB)
                    .where(
                        AdmissionDB.bed_id == bed.id,
                        AdmissionDB.status == "admitted",
                        AdmissionDB.id != admission.id,
                    )
                )

                if existing_admission is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "This bed is already assigned "
                            "to another active admission."
                        ),
                    )

                if bed.status not in {
                    "available",
                    "occupied",
                }:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Selected bed is not available.",
                    )

                bed.status = "occupied"

            elif final_status in {
                "discharged",
                "cancelled",
            }:
                bed.status = "available"

    # --------------------------------------------------------
    # Apply admission changes
    # --------------------------------------------------------

    admission.patient_id = final_patient_id
    admission.doctor_id = final_doctor_id
    admission.bed_id = final_bed_id
    admission.admission_date = final_admission_date
    admission.discharge_date = final_discharge_date
    admission.status = final_status

    # --------------------------------------------------------
    # Commit all changes together.
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(admission)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to update admission because "
                "of a database constraint."
            ),
        )

    return admission


# ============================================================
# DISCHARGE ADMISSION
# ============================================================

@router.patch(
    "/{admission_id}/discharge",
    response_model=AdmissionResponse,
    status_code=status.HTTP_200_OK,
)
def discharge_admission(
    admission_id: int,
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
    # Find admission
    # --------------------------------------------------------

    admission = db.scalar(
        select(AdmissionDB)
        .where(
            AdmissionDB.id == admission_id
        )
        .with_for_update()
    )

    if admission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission not found.",
        )

    if admission.status == "discharged":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admission is already discharged.",
        )

    admission.status = "discharged"
    admission.discharge_date = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # Release the bed.
    # --------------------------------------------------------

    bed = db.scalar(
        select(BedDB)
        .where(
            BedDB.id == admission.bed_id
        )
        .with_for_update()
    )

    if bed is not None:
        bed.status = "available"

    try:
        db.commit()
        db.refresh(admission)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to discharge admission.",
        )

    return admission


# ============================================================
# DELETE ADMISSION
# ============================================================

@router.delete(
    "/{admission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_admission(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # --------------------------------------------------------
    # Find admission
    # --------------------------------------------------------

    admission = db.scalar(
        select(AdmissionDB)
        .where(
            AdmissionDB.id == admission_id
        )
        .with_for_update()
    )

    if admission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission not found.",
        )

    # --------------------------------------------------------
    # Release bed if this was an active admission.
    # --------------------------------------------------------

    if admission.status == "admitted":

        bed = db.scalar(
            select(BedDB)
            .where(
                BedDB.id == admission.bed_id
            )
            .with_for_update()
        )

        if bed is not None:
            bed.status = "available"

    # --------------------------------------------------------
    # Delete admission
    # --------------------------------------------------------

    db.delete(admission)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to delete admission because "
                "it is referenced by other records."
            ),
        )

    return None