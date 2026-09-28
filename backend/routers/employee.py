from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.employee import EmployeeDB
from models.role import RoleDB
from models.department import DepartmentDB
from models.users import UserDB

from schema.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)

from utils.dependencies import (
    require_admin,
    require_role,
)


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


# ============================================================
# CREATE EMPLOYEE
# ============================================================

@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    # --------------------------------------------------------
    # Validate role
    # --------------------------------------------------------

    role = db.scalar(
        select(RoleDB).where(
            RoleDB.id == employee_data.role_id
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    # --------------------------------------------------------
    # Prevent assigning the admin role to new employees
    # --------------------------------------------------------

    if role.name.strip().lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The admin role cannot be assigned through the API.",
        )

    # --------------------------------------------------------
    # Validate department
    # --------------------------------------------------------

    department = db.scalar(
        select(DepartmentDB).where(
            DepartmentDB.id == employee_data.department_id
        )
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

    if employee_data.email is not None:
        existing_employee = db.scalar(
            select(EmployeeDB).where(
                EmployeeDB.email == str(employee_data.email)
            )
        )

        if existing_employee is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee with this email already exists.",
            )

    # --------------------------------------------------------
    # Create employee
    # --------------------------------------------------------

    employee = EmployeeDB(
        name=employee_data.name,
        role_id=employee_data.role_id,
        department_id=employee_data.department_id,
        dob=employee_data.dob,
        gender=employee_data.gender,
        phone=employee_data.phone,
        email=(
            str(employee_data.email)
            if employee_data.email is not None
            else None
        ),
        address=employee_data.address,
        hire_date=employee_data.hire_date,
        salary=employee_data.salary,
        employment_status=employee_data.employment_status,
    )

    db.add(employee)

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Employee could not be created because "
                "of a database constraint."
            ),
        )

    return employee


# ============================================================
# GET ALL EMPLOYEES
# ============================================================

@router.get(
    "/",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
)
def get_employees(
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
    employees = db.scalars(
        select(EmployeeDB).order_by(
            EmployeeDB.id
        )
    ).all()

    return employees


# ============================================================
# GET EMPLOYEES BY DEPARTMENT
# ============================================================

@router.get(
    "/department/{department_id}",
    response_model=list[EmployeeResponse],
    status_code=status.HTTP_200_OK,
)
def get_employees_by_department(
    department_id: int,
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
    # Validate department
    # --------------------------------------------------------

    department = db.scalar(
        select(DepartmentDB).where(
            DepartmentDB.id == department_id
        )
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    # --------------------------------------------------------
    # Get employees
    # --------------------------------------------------------

    employees = db.scalars(
        select(EmployeeDB)
        .where(
            EmployeeDB.department_id == department_id
        )
        .order_by(EmployeeDB.id)
    ).all()

    return employees


# ============================================================
# GET EMPLOYEE BY ID
# ============================================================

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def get_employee(
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
    employee = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.id == employee_id
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return employee


# ============================================================
# UPDATE EMPLOYEE
# ============================================================

@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    employee = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.id == employee_id
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    update_data = employee_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields were provided for update.",
        )

    # --------------------------------------------------------
    # Validate role
    # --------------------------------------------------------

    if "role_id" in update_data:

        role = db.scalar(
            select(RoleDB).where(
                RoleDB.id == update_data["role_id"]
            )
        )

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found.",
            )

        if role.name.strip().lower() == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The admin role cannot be assigned through the API.",
            )

    # --------------------------------------------------------
    # Validate department
    # --------------------------------------------------------

    if "department_id" in update_data:

        department = db.scalar(
            select(DepartmentDB).where(
                DepartmentDB.id
                == update_data["department_id"]
            )
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found.",
            )

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

    if (
        "email" in update_data
        and update_data["email"] is not None
    ):
        existing_employee = db.scalar(
            select(EmployeeDB).where(
                EmployeeDB.email
                == str(update_data["email"]),
                EmployeeDB.id != employee_id,
            )
        )

        if existing_employee is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee with this email already exists.",
            )

        update_data["email"] = str(
            update_data["email"]
        )

    # --------------------------------------------------------
    # Apply changes
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(employee, field, value)

    try:
        db.commit()
        db.refresh(employee)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Employee could not be updated because "
                "of a database constraint."
            ),
        )

    return employee


# ============================================================
# DELETE EMPLOYEE
# ============================================================

@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin),
):
    employee = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.id == employee_id
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    db.delete(employee)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Employee cannot be deleted because "
                "it is referenced by other records."
            ),
        )

    return None