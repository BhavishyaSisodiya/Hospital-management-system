from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.lab import LabTestDB
from models.lab_result import LabResultDB
from models.users import UserDB
from models.patient import PatientDB

from schema.lab_result import (
    LabResultCreate,
    LabResultUpdate,
    LabResultResponse,
)

from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/lab-results",
    tags=["Lab Results"],
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
    if user.account_type != "member" or user.role is None:
        return False

    user_role = user.role.name.lower()

    return user_role in {
        role.lower()
        for role in roles
    }


def can_view_lab_results(user: UserDB) -> bool:
    return (
        is_admin(user)
        or has_role(
            user,
            "doctor",
            "nurse",
            "lab_technician",
            "receptionist",
        )
    )


def can_manage_lab_results(user: UserDB) -> bool:
    return (
        is_admin(user)
        or has_role(user, "lab_technician")
    )


# ============================================================
# CREATE LAB RESULT
# ============================================================

@router.post(
    "/",
    response_model=LabResultResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lab_result(
    result_data: LabResultCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_manage_lab_results(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create lab results.",
        )

    # --------------------------------------------------------
    # Find lab test
    # --------------------------------------------------------

    lab_test = db.scalar(
        select(LabTestDB).where(
            LabTestDB.id == result_data.lab_test_id
        )
    )

    if lab_test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab test not found.",
        )

    # --------------------------------------------------------
    # A cancelled test cannot receive a result
    # --------------------------------------------------------

    if lab_test.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot create a result for a cancelled lab test.",
        )

    # --------------------------------------------------------
    # Check one-to-one relationship
    # --------------------------------------------------------

    existing_result = db.scalar(
        select(LabResultDB).where(
            LabResultDB.lab_test_id == result_data.lab_test_id
        )
    )

    if existing_result is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A result already exists for this lab test.",
        )

    # --------------------------------------------------------
    # Create result
    # --------------------------------------------------------

    result_data_dict = result_data.model_dump(
        exclude_none=True
    )

    new_result = LabResultDB(
        **result_data_dict
    )

    db.add(new_result)

    # --------------------------------------------------------
    # Creating a result means the test is completed
    # --------------------------------------------------------

    lab_test.status = "completed"

    try:
        db.commit()
        db.refresh(new_result)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lab result could not be created because of a database constraint.",
        )

    return new_result


# ============================================================
# GET ALL LAB RESULTS
# ============================================================

@router.get(
    "/",
    response_model=list[LabResultResponse],
)
def get_lab_results(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_view_lab_results(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view lab results.",
        )

    results = db.scalars(
        select(LabResultDB)
        .order_by(LabResultDB.id)
    ).all()

    return results


# ============================================================
# GET SINGLE LAB RESULT
# ============================================================

@router.get(
    "/{result_id}",
    response_model=LabResultResponse,
)
def get_lab_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_view_lab_results(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view lab results.",
        )

    result = db.scalar(
        select(LabResultDB).where(
            LabResultDB.id == result_id
        )
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab result not found.",
        )

    return result

# ============================================================
# GET LAB RESULTS BY PATIENT
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[LabResultResponse],
    status_code=status.HTTP_200_OK,
)
def get_patient_lab_results(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Verify patient exists
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
    # Patient can only view their own lab results
    # --------------------------------------------------------

    if current_user.account_type == "patient":

        if (
            current_user.patient is None
            or current_user.patient.id != patient_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own lab results.",
            )

    # --------------------------------------------------------
    # Staff access
    # --------------------------------------------------------

    elif not can_view_lab_results(current_user):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "patient lab results."
            ),
        )

    # --------------------------------------------------------
    # Get patient's lab results
    #
    # LabResult -> LabTest -> patient_id
    # --------------------------------------------------------

    results = db.scalars(
        select(LabResultDB)
        .join(
            LabTestDB,
            LabResultDB.lab_test_id == LabTestDB.id,
        )
        .where(
            LabTestDB.patient_id == patient_id
        )
        .order_by(
            LabResultDB.reported_at.desc(),
            LabResultDB.id.desc(),
        )
    ).all()

    return results
# ============================================================
# UPDATE LAB RESULT
# ============================================================

@router.patch(
    "/{result_id}",
    response_model=LabResultResponse,
)
def update_lab_result(
    result_id: int,
    result_data: LabResultUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not can_manage_lab_results(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update lab results.",
        )

    # --------------------------------------------------------
    # Find existing result
    # --------------------------------------------------------

    result = db.scalar(
        select(LabResultDB).where(
            LabResultDB.id == result_id
        )
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab result not found.",
        )

    # --------------------------------------------------------
    # Get only fields actually sent by client
    # --------------------------------------------------------

    update_data = result_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # If lab_test_id is being changed
    # --------------------------------------------------------

    if "lab_test_id" in update_data:

        new_lab_test_id = update_data["lab_test_id"]

        new_lab_test = db.scalar(
            select(LabTestDB).where(
                LabTestDB.id == new_lab_test_id
            )
        )

        if new_lab_test is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lab test not found.",
            )

        if new_lab_test.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot attach a result to a cancelled lab test.",
            )

        # ----------------------------------------------------
        # Check one-to-one constraint
        # ----------------------------------------------------

        existing_result = db.scalar(
            select(LabResultDB).where(
                LabResultDB.lab_test_id == new_lab_test_id,
                LabResultDB.id != result_id,
            )
        )

        if existing_result is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A result already exists for this lab test.",
            )

        # ----------------------------------------------------
        # Previous lab test may no longer have a result
        # ----------------------------------------------------

        old_lab_test = db.scalar(
            select(LabTestDB).where(
                LabTestDB.id == result.lab_test_id
            )
        )

        if old_lab_test is not None:
            # We intentionally do not automatically change the
            # old test status because it may have other workflow
            # requirements.

            pass

        new_lab_test.status = "completed"

    # --------------------------------------------------------
    # Apply updates
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            result,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(result)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lab result could not be updated because of a database constraint.",
        )

    return result


# ============================================================
# DELETE LAB RESULT
# ============================================================

@router.delete(
    "/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_lab_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an administrator can delete lab results.",
        )

    result = db.scalar(
        select(LabResultDB).where(
            LabResultDB.id == result_id
        )
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab result not found.",
        )

    try:
        db.delete(result)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lab result could not be deleted.",
        )

    return None