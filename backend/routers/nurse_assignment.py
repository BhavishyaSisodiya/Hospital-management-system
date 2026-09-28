from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.nurse_assignment import NurseAssignmentDB
from models.admission import AdmissionDB
from models.employee import EmployeeDB

from schema.nurse_Assignment import (
    NurseAssignmentCreate,
    NurseAssignmentUpdate,
    NurseAssignmentResponse,
)

from utils.dependencies import (
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/nurse-assignments",
    tags=["Nurse Assignments"],
)


# ============================================================
# VALIDATE NURSE
# ============================================================

def has_role(user, *roles: str) -> bool:
    return (
        user.role is not None
        and user.role.name.lower() in {r.lower() for r in roles}
    )


def validate_nurse(
    nurse_id: int,
    db: Session,
) -> EmployeeDB:

    nurse = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.id == nurse_id
        )
    )

    if nurse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nurse not found.",
        )

    if nurse.role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected employee does not have a role.",
        )

    if nurse.role.name.lower() != "nurse":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected employee is not a nurse.",
        )

    return nurse


# ============================================================
# CREATE NURSE ASSIGNMENT
# ============================================================

@router.post(
    "/",
    response_model=NurseAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_nurse_assignment(
    assignment_data: NurseAssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "nurse")
    ),
):

    # --------------------------------------------------------
    # Validate admission
    # --------------------------------------------------------

    admission = db.scalar(
        select(AdmissionDB).where(
            AdmissionDB.id == assignment_data.admission_id
        )
    )

    if admission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission not found.",
        )

    # A nurse should only be assigned to an active admission.
    if admission.status != "admitted":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nurse can only be assigned to an active admission.",
        )

    # --------------------------------------------------------
    # Validate nurse
    # --------------------------------------------------------

    validate_nurse(
        assignment_data.nurse_id,
        db,
    )

    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------

    if (
        assignment_data.assigned_at is not None
        and assignment_data.unassigned_at is not None
        and assignment_data.unassigned_at
        < assignment_data.assigned_at
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="unassigned_at must be greater than or equal to assigned_at.",
        )

    # --------------------------------------------------------
    # Prevent duplicate active assignment
    # --------------------------------------------------------

    if assignment_data.unassigned_at is None:

        existing_assignment = db.scalar(
            select(NurseAssignmentDB).where(
                NurseAssignmentDB.admission_id
                == assignment_data.admission_id,

                NurseAssignmentDB.nurse_id
                == assignment_data.nurse_id,

                NurseAssignmentDB.unassigned_at.is_(None),
            )
        )

        if existing_assignment is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This nurse is already actively assigned to this admission.",
            )

    # --------------------------------------------------------
    # Create assignment
    # --------------------------------------------------------

    assignment = NurseAssignmentDB(
        admission_id=assignment_data.admission_id,
        nurse_id=assignment_data.nurse_id,
        unassigned_at=assignment_data.unassigned_at,
    )

    # Only override model default when client supplied value.
    if assignment_data.assigned_at is not None:
        assignment.assigned_at = assignment_data.assigned_at

    db.add(assignment)

    try:
        db.commit()
        db.refresh(assignment)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nurse assignment could not be created because of a database constraint.",
        )

    return assignment


# ============================================================
# GET ALL NURSE ASSIGNMENTS
# ============================================================

@router.get(
    "/",
    response_model=list[NurseAssignmentResponse],
    status_code=status.HTTP_200_OK,
)
def get_nurse_assignments(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):

    assignments = db.scalars(
        select(NurseAssignmentDB).order_by(
            NurseAssignmentDB.assigned_at.desc(),
            NurseAssignmentDB.id.desc(),
        )
    ).all()

    return assignments


# ============================================================
# GET ASSIGNMENTS BY ADMISSION
# ============================================================

@router.get(
    "/admission/{admission_id}",
    response_model=list[NurseAssignmentResponse],
    status_code=status.HTTP_200_OK,
)
def get_admission_assignments(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
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

    assignments = db.scalars(
        select(NurseAssignmentDB)
        .where(
            NurseAssignmentDB.admission_id == admission_id
        )
        .order_by(
            NurseAssignmentDB.assigned_at.desc(),
            NurseAssignmentDB.id.desc(),
        )
    ).all()

    return assignments


# ============================================================
# GET ASSIGNMENTS BY NURSE
# ============================================================

@router.get(
    "/nurse/{nurse_id}",
    response_model=list[NurseAssignmentResponse],
    status_code=status.HTTP_200_OK,
)
def get_nurse_assignments_by_nurse(
    nurse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):

    resolved_nurse_id = nurse_id

    if has_role(current_user, "nurse"):
        employee = db.scalar(
            select(EmployeeDB).where(
                EmployeeDB.email == current_user.email
            )
        )
        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found for this nurse.",
            )
        resolved_nurse_id = employee.id

    validate_nurse(
        resolved_nurse_id,
        db,
    )

    assignments = db.scalars(
        select(NurseAssignmentDB)
        .where(
            NurseAssignmentDB.nurse_id == resolved_nurse_id
        )
        .order_by(
            NurseAssignmentDB.assigned_at.desc(),
            NurseAssignmentDB.id.desc(),
        )
    ).all()

    return assignments


# ============================================================
# GET SINGLE NURSE ASSIGNMENT
# ============================================================

@router.get(
    "/{assignment_id}",
    response_model=NurseAssignmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_nurse_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
        )
    ),
):

    assignment = db.scalar(
        select(NurseAssignmentDB).where(
            NurseAssignmentDB.id == assignment_id
        )
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nurse assignment not found.",
        )

    return assignment


# ============================================================
# UPDATE NURSE ASSIGNMENT
# ============================================================

@router.patch(
    "/{assignment_id}",
    response_model=NurseAssignmentResponse,
    status_code=status.HTTP_200_OK,
)
def update_nurse_assignment(
    assignment_id: int,
    assignment_data: NurseAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("admin", "nurse")
    ),
):

    assignment = db.scalar(
        select(NurseAssignmentDB).where(
            NurseAssignmentDB.id == assignment_id
        )
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nurse assignment not found.",
        )

    update_data = assignment_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # --------------------------------------------------------
    # Calculate final values
    # --------------------------------------------------------

    final_admission_id = update_data.get(
        "admission_id",
        assignment.admission_id,
    )

    final_nurse_id = update_data.get(
        "nurse_id",
        assignment.nurse_id,
    )

    final_assigned_at = update_data.get(
        "assigned_at",
        assignment.assigned_at,
    )

    final_unassigned_at = update_data.get(
        "unassigned_at",
        assignment.unassigned_at,
    )

    # --------------------------------------------------------
    # Validate final dates
    # --------------------------------------------------------

    if (
        final_unassigned_at is not None
        and final_unassigned_at < final_assigned_at
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="unassigned_at must be greater than or equal to assigned_at.",
        )

    # --------------------------------------------------------
    # Validate admission
    # --------------------------------------------------------

    admission = db.scalar(
        select(AdmissionDB).where(
            AdmissionDB.id == final_admission_id
        )
    )

    if admission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admission not found.",
        )

    # An active assignment requires an active admission.
    if (
        final_unassigned_at is None
        and admission.status != "admitted"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An active nurse assignment requires an active admission.",
        )

    # --------------------------------------------------------
    # Validate nurse
    # --------------------------------------------------------

    validate_nurse(
        final_nurse_id,
        db,
    )

    # --------------------------------------------------------
    # Prevent duplicate active assignment
    # --------------------------------------------------------

    if final_unassigned_at is None:

        existing_assignment = db.scalar(
            select(NurseAssignmentDB).where(
                NurseAssignmentDB.admission_id
                == final_admission_id,

                NurseAssignmentDB.nurse_id
                == final_nurse_id,

                NurseAssignmentDB.unassigned_at.is_(None),

                NurseAssignmentDB.id != assignment_id,
            )
        )

        if existing_assignment is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This nurse is already actively assigned to this admission.",
            )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    assignment.admission_id = final_admission_id
    assignment.nurse_id = final_nurse_id
    assignment.assigned_at = final_assigned_at
    assignment.unassigned_at = final_unassigned_at

    try:
        db.commit()
        db.refresh(assignment)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nurse assignment could not be updated because of a database constraint.",
        )

    return assignment


# ============================================================
# DELETE NURSE ASSIGNMENT
# ============================================================

@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_nurse_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    assignment = db.scalar(
        select(NurseAssignmentDB).where(
            NurseAssignmentDB.id == assignment_id
        )
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nurse assignment not found.",
        )

    db.delete(assignment)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nurse assignment could not be deleted.",
        )

    return None