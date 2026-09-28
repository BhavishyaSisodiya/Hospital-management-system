from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal

from models.patient import PatientDB
from models.doctor import DoctorDB
from models.appointments import AppointmentDB
from models.department import DepartmentDB
from models.medical_record import MedicalRecordDB
from models.lab import LabTestDB
from models.lab_result import LabResultDB
from models.prescription import PrescriptionDB
from models.users import UserDB

from utils.dependencies import require_role, require_patient


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# Database session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(
            "admin",
            "receptionist",
            "doctor",
            "nurse",
            "pharmacist",
            "lab_technician",
            "accountant",
        )
    )
):

    total_patients = db.query(PatientDB).count()

    total_doctors = db.query(DoctorDB).count()

    total_appointments = db.query(
        AppointmentDB
    ).count()

    total_departments = db.query(
        DepartmentDB
    ).count()

    return {
        "patients": total_patients,
        "doctors": total_doctors,
        "appointments": total_appointments,
        "departments": total_departments,
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "total_departments": total_departments,
    }


@router.get("/patient-stats")
def get_patient_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_patient),
):

    patient = current_user.patient

    if patient is None:
        return {
            "appointments": 0,
            "medical_records": 0,
            "lab_results": 0,
            "prescriptions": 0,
        }

    total_appointments = (
        db.query(AppointmentDB)
        .filter(AppointmentDB.patient_id == patient.id)
        .count()
    )

    total_medical_records = (
        db.query(MedicalRecordDB)
        .filter(MedicalRecordDB.patient_id == patient.id)
        .count()
    )

    total_prescriptions = (
        db.query(PrescriptionDB)
        .filter(PrescriptionDB.patient_id == patient.id)
        .count()
    )

    total_lab_results = (
        db.query(LabResultDB)
        .join(LabTestDB, LabResultDB.lab_test_id == LabTestDB.id)
        .filter(LabTestDB.patient_id == patient.id)
        .count()
    )

    return {
        "appointments": total_appointments,
        "medical_records": total_medical_records,
        "lab_results": total_lab_results,
        "prescriptions": total_prescriptions,
    }