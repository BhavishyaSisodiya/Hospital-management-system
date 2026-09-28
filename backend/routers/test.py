from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.test import TestTypeDB
from models.users import UserDB

from schema.test import (
    TestTypeCreate,
    TestTypeUpdate,
    TestTypeResponse,
)

from utils.dependencies import (
    get_current_user,
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/test-types",
    tags=["Test Types"],
)


# ============================================================
# CREATE TEST TYPE
# ============================================================

@router.post(
    "/",
    response_model=TestTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test_type(
    test_type_data: TestTypeCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "lab_technician",
        )
    ),
):
    # --------------------------------------------------------
    # Check duplicate name
    # --------------------------------------------------------

    existing_test_type = db.scalar(
        select(TestTypeDB).where(
            TestTypeDB.name == test_type_data.name
        )
    )

    if existing_test_type is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test type with this name already exists.",
        )

    # --------------------------------------------------------
    # Create test type
    # --------------------------------------------------------

    test_type = TestTypeDB(
        name=test_type_data.name,
        price=test_type_data.price,
    )

    db.add(test_type)

    try:
        db.commit()
        db.refresh(test_type)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test type could not be created because of a database constraint.",
        )

    return test_type


# ============================================================
# GET ALL TEST TYPES
# ============================================================

@router.get(
    "/",
    response_model=list[TestTypeResponse],
    status_code=status.HTTP_200_OK,
)
def get_test_types(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "lab_technician",
        )
    ),
):
    test_types = db.scalars(
        select(TestTypeDB)
        .order_by(TestTypeDB.name)
    ).all()

    return test_types


# ============================================================
# GET SINGLE TEST TYPE
# ============================================================

@router.get(
    "/{test_type_id}",
    response_model=TestTypeResponse,
    status_code=status.HTTP_200_OK,
)
def get_test_type(
    test_type_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "doctor",
            "nurse",
            "receptionist",
            "lab_technician",
        )
    ),
):
    test_type = db.get(
        TestTypeDB,
        test_type_id,
    )

    if test_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test type not found.",
        )

    return test_type


# ============================================================
# UPDATE TEST TYPE
# ============================================================

@router.patch(
    "/{test_type_id}",
    response_model=TestTypeResponse,
    status_code=status.HTTP_200_OK,
)
def update_test_type(
    test_type_id: int,
    test_type_data: TestTypeUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "lab_technician",
        )
    ),
):
    # --------------------------------------------------------
    # Find test type
    # --------------------------------------------------------

    test_type = db.get(
        TestTypeDB,
        test_type_id,
    )

    if test_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test type not found.",
        )

    # --------------------------------------------------------
    # Get only fields supplied in PATCH request
    # --------------------------------------------------------

    update_data = test_type_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------------
    # Check duplicate name
    # --------------------------------------------------------

    if "name" in update_data:

        existing_test_type = db.scalar(
            select(TestTypeDB).where(
                TestTypeDB.name == update_data["name"],
                TestTypeDB.id != test_type_id,
            )
        )

        if existing_test_type is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Test type with this name already exists.",
            )

    # --------------------------------------------------------
    # Apply updates
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            test_type,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(test_type)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test type could not be updated because of a database constraint.",
        )

    return test_type


# ============================================================
# DELETE TEST TYPE
# ============================================================

@router.delete(
    "/{test_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_test_type(
    test_type_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        require_role(
            "admin",
            "lab_technician",
        )
    ),
):
    # --------------------------------------------------------
    # Find test type
    # --------------------------------------------------------

    test_type = db.get(
        TestTypeDB,
        test_type_id,
    )

    if test_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test type not found.",
        )

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    try:
        db.delete(test_type)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test type cannot be deleted because it is being used by lab tests.",
        )

    return None