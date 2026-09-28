"""Create/fix staff login accounts (doctor/nurse/reception/etc).

This also LINKS each staff login account to a real EmployeeDB record
(and DoctorDB for doctors) so that "my appointments", "my patients",
"my schedule", etc. endpoints can resolve the logged-in user.

Without this linkage every "me"-style endpoint returns:
    Employee profile not found for this {doctor,nurse}.
and the UI shows no data.

For the doctor login it also seeds demo clinical data (appointments,
schedule, medical records, prescriptions, lab tests) linked to that
account so the doctor portal is not empty on first login.
"""

import sys
from datetime import date, datetime, time, timedelta, timezone

sys.path.insert(0, ".")

from database import SessionLocal
from models.role import RoleDB
from models.department import DepartmentDB
from models.users import UserDB
from models.employee import EmployeeDB
from models.doctor import DoctorDB
from models.doctorScedule import DoctorScheduleDB
from models.patient import PatientDB
from models.appointments import AppointmentDB
from models.medical_record import MedicalRecordDB
from models.vitals import VitalDB
from models.prescription import PrescriptionDB
from models.prescription_medicine import PrescriptionMedicineDB
from models.pharmacy import PharmacyDB
from models.medicine import MedicineDB
from models.test import TestTypeDB
from models.lab import LabTestDB
from models.lab_result import LabResultDB
from models.admission import AdmissionDB
from models.nurse_assignment import NurseAssignmentDB
from utils.security import hash_password

STAFF = [
    {
        "name": "Dr. Smith",
        "email": "doctor@hms.com",
        "password": "Doctor@123",
        "role_name": "doctor",
        "department": "General Medicine",
        "specialization": "General Medicine",
        "experience_years": 10,
        "phone": "9800000101",
        "gender": "Male",
    },
    {
        "name": "Nurse Joy",
        "email": "nurse@hms.com",
        "password": "Nurse@123",
        "role_name": "nurse",
        "department": "Emergency",
        "phone": "9800000102",
        "gender": "Female",
    },
    {
        "name": "Receptionist Kim",
        "email": "reception@hms.com",
        "password": "Recep@123",
        "role_name": "receptionist",
        "department": "Emergency",
        "phone": "9800000103",
        "gender": "Female",
    },
    {
        "name": "Alex Pharmacist",
        "email": "pharmacist@hms.com",
        "password": "Pharma@123",
        "role_name": "pharmacist",
        "department": "Emergency",
        "phone": "9800000104",
        "gender": "Male",
    },
    {
        "name": "Rita Labtech",
        "email": "labtech@hms.com",
        "password": "Labtech@123",
        "role_name": "lab_technician",
        "department": "Radiology",
        "phone": "9800000105",
        "gender": "Female",
    },
    {
        "name": "Elena Accountant",
        "email": "accountant@hms.com",
        "password": "Acc@123",
        "role_name": "accountant",
        "department": "Emergency",
        "phone": "9800000106",
        "gender": "Female",
    },
]


def _dept_named(db, roles_departments, preferred):
    dept = next((d for d in roles_departments if d.name == preferred), None)
    return dept or (roles_departments[0] if roles_departments else None)


def ensure_staff(db):
    roles = {r.name: r.id for r in db.query(RoleDB).all()}
    all_departments = db.query(DepartmentDB).order_by(DepartmentDB.id).all()

    created = 0
    for item in STAFF:
        role_name = item["role_name"]
        email = item["email"]

        # -- 1) Login user --------------------------------------------------
        user = db.query(UserDB).filter(UserDB.email == email).first()
        if user is None:
            user = UserDB(
                name=item["name"],
                email=email,
                password_hash=hash_password(item["password"]),
                account_type="member",
                role_id=roles.get(role_name),
                is_active=True,
            )
            db.add(user)
            db.flush()
            created += 1
            print(f"  created staff user: {email}")
        elif user.account_type != "member" or user.role_id is None:
            user.account_type = "member"
            user.role_id = roles.get(role_name)
            print(f"  fixed staff user: {email} -> member/{role_name}")

        # -- 2) Employee linked to that login ------------------------------
        # Every "me" endpoint matches EmployeeDB.email == current_user.email.
        employee = (
            db.query(EmployeeDB).filter(EmployeeDB.email == email).first()
        )
        dept = _dept_named(db, all_departments, item["department"])
        if employee is None:
            if dept is None:
                print(f"  SKIP employee for {email}: no department configured")
                continue
            employee = EmployeeDB(
                name=item["name"],
                role_id=roles.get(role_name),
                department_id=dept.id,
                dob=date(1985, 1, 1),
                gender=item.get("gender", "Male"),
                phone=item.get("phone"),
                email=email,
                address="Mumbai",
                hire_date=date(2020, 1, 1),
                salary=60000,
                employment_status="active",
            )
            db.add(employee)
            db.flush()
            created += 1
            print(f"  created employee: {email} ({role_name})")
        else:
            employee.role_id = roles.get(role_name)
            if dept is not None:
                employee.department_id = dept.id
            if employee.employment_status not in (
                "active",
                "on_leave",
            ):
                employee.employment_status = "active"
            print(f"  linked employee: {email}")

        if role_name == "doctor":
            ensure_doctor(db, employee, item)

        if role_name == "nurse":
            ensure_nurse(db, employee)

    return created


def ensure_doctor(db, employee, item):
    doctor = (
        db.query(DoctorDB)
        .filter(DoctorDB.employee_id == employee.id)
        .first()
    )
    if doctor is None:
        doctor = DoctorDB(
            employee_id=employee.id,
            specialization=item["specialization"],
            experience_years=item["experience_years"],
        )
        db.add(doctor)
        db.flush()
        print(f"  created doctor profile: {item['email']}")

    # Weekly schedule (Mon-Fri 9:00-17:00)
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
    ]
    for day in days:
        existing = (
            db.query(DoctorScheduleDB)
            .filter(
                DoctorScheduleDB.doctor_id == doctor.id,
                DoctorScheduleDB.day_of_week == day,
            )
            .first()
        )
        if existing:
            continue
        db.add(
            DoctorScheduleDB(
                doctor_id=doctor.id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
            )
        )
    print("  doctor schedule ensured")

    db.commit()

    seed_doctor_patients(db, doctor)
    seed_doctor_clinical(db, doctor)


def seed_doctor_patients(db, doctor):
    """Reassign a few seeded patients' appointments/records to this doctor so
    the doctor portal shows data."""
    patients = db.query(PatientDB).order_by(PatientDB.id).limit(5).all()
    if not patients:
        return

    now = date.today()
    for idx, patient in enumerate(patients):
        appt_date = now + timedelta(days=idx // 4)
        appt_time = time(9 + (idx % 4), (idx % 2) * 30)
        exists = (
            db.query(AppointmentDB)
            .filter(
                AppointmentDB.doctor_id == doctor.id,
                AppointmentDB.patient_id == patient.id,
            )
            .first()
        )
        if not exists:
            try:
                db.add(
                    AppointmentDB(
                        patient_id=patient.id,
                        doctor_id=doctor.id,
                        appointment_date=appt_date,
                        appointment_time=appt_time,
                        reason=(
                            "Routine checkup"
                            if idx % 2 == 0
                            else "Follow-up consultation"
                        ),
                        status=(
                            "scheduled"
                            if idx % 3 != 0
                            else "completed"
                        ),
                    )
                )
                db.commit()
            except Exception:
                db.rollback()

    print(f"  seeded appointments for doctor id={doctor.id}")


def seed_doctor_clinical(db, doctor):
    """Seed medical records, prescriptions and lab tests so the doctor's
    clinical pages show data."""
    patients = db.query(PatientDB).order_by(PatientDB.id).limit(3).all()
    medicines = db.query(MedicineDB).order_by(MedicineDB.id).all()
    pharmacies = db.query(PharmacyDB).order_by(PharmacyDB.id).all()
    test_types = db.query(TestTypeDB).order_by(TestTypeDB.id).all()
    technicians = (
        db.query(EmployeeDB)
        .join(RoleDB, EmployeeDB.role_id == RoleDB.id)
        .filter(RoleDB.name == "lab_technician")
        .all()
    )

    diagnosis_pool = [
        "Hypertension",
        "Type 2 Diabetes",
        "Migraine",
        "Lower back pain",
        "Acute gastritis",
    ]
    med_pool = ["Paracetamol 500mg", "Metformin 500mg", "Omeprazole 20mg"]
    now_ts = datetime.now(timezone.utc)

    for idx, patient in enumerate(patients):
        # medical record
        has_record = (
            db.query(MedicalRecordDB)
            .filter(
                MedicalRecordDB.doctor_id == doctor.id,
                MedicalRecordDB.patient_id == patient.id,
            )
            .first()
        )
        if not has_record:
            try:
                db.add(
                    MedicalRecordDB(
                        patient_id=patient.id,
                        doctor_id=doctor.id,
                        diagnosis=diagnosis_pool[idx % len(diagnosis_pool)],
                        notes=(
                            "Patient reports symptoms over the last 2 weeks. "
                            "Follow-up scheduled."
                        ),
                        record_date=now_ts - timedelta(days=idx + 2),
                    )
                )
                db.commit()
            except Exception:
                db.rollback()

        # vitals
        has_vital = (
            db.query(VitalDB)
            .filter(
                VitalDB.recorded_by == doctor.employee_id,
                VitalDB.patient_id == patient.id,
            )
            .first()
        )
        if not has_vital:
            try:
                db.add(
                    VitalDB(
                        patient_id=patient.id,
                        recorded_by=doctor.employee_id,
                        temperature=98.4,
                        heart_rate=76,
                        blood_pressure_systolic=122,
                        blood_pressure_diastolic=80,
                        respiratory_rate=16,
                        oxygen_saturation=98.5,
                        weight=70.0,
                    )
                )
                db.commit()
            except Exception:
                db.rollback()

        # prescription
        if medicines and pharmacies:
            has_rx = (
                db.query(PrescriptionDB)
                .filter(
                    PrescriptionDB.doctor_id == doctor.id,
                    PrescriptionDB.patient_id == patient.id,
                )
                .first()
            )
            if not has_rx:
                try:
                    rx = PrescriptionDB(
                        patient_id=patient.id,
                        doctor_id=doctor.id,
                        pharmacy_id=pharmacies[0].id,
                        prescription_date=date.today()
                        - timedelta(days=idx + 1),
                    )
                    db.add(rx)
                    db.flush()
                    med_name = med_pool[idx % len(med_pool)]
                    med = next(
                        (m for m in medicines if m.name == med_name),
                        medicines[0],
                    )
                    db.add(
                        PrescriptionMedicineDB(
                            prescription_id=rx.id,
                            medicine_id=med.id,
                            quantity=2,
                            dosage="500mg twice daily",
                            duration="7 days",
                            instructions="After meals",
                        )
                    )
                    db.commit()
                except Exception:
                    db.rollback()

        # lab test + result
        if test_types:
            has_lab = (
                db.query(LabTestDB)
                .filter(
                    LabTestDB.doctor_id == doctor.id,
                    LabTestDB.patient_id == patient.id,
                )
                .first()
            )
            if not has_lab:
                try:
                    lt = LabTestDB(
                        test_type_id=test_types[idx % len(test_types)].id,
                        patient_id=patient.id,
                        doctor_id=doctor.id,
                        technician_id=(
                            technicians[0].id if technicians else None
                        ),
                        status="completed",
                        test_date=now_ts - timedelta(days=idx + 1),
                    )
                    db.add(lt)
                    db.flush()
                    db.add(
                        LabResultDB(
                            lab_test_id=lt.id,
                            result=(
                                "Normal range"
                                if idx % 2 == 0
                                else "Slightly elevated"
                            ),
                            unit="g/dL" if idx % 2 == 0 else "mg/dL",
                            reference_range="12-16",
                            remarks="No further action needed",
                        )
                    )
                    db.commit()
                except Exception:
                    db.rollback()

    print(f"  seeded clinical data for doctor id={doctor.id}")


def ensure_nurse(db, employee):
    """Assign the nurse to active admissions so nurse pages show data."""
    try:
        admissions = (
            db.query(AdmissionDB)
            .filter(AdmissionDB.status == "admitted")
            .order_by(AdmissionDB.id)
            .all()
        )
    except Exception:
        admissions = []

    assigned = 0
    for admission in admissions[:3]:
        exists = (
            db.query(NurseAssignmentDB)
            .filter(
                NurseAssignmentDB.nurse_id == employee.id,
                NurseAssignmentDB.admission_id == admission.id,
            )
            .first()
        )
        if exists:
            assigned += 1
            continue
        try:
            db.add(
                NurseAssignmentDB(
                    admission_id=admission.id,
                    nurse_id=employee.id,
                    assigned_at=datetime.now(timezone.utc),
                )
            )
            db.commit()
            db.refresh(admission)
            assigned += 1
        except Exception:
            db.rollback()

    print(f"  ensured {assigned} nurse assignments for {employee.email}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        count = ensure_staff(db)
        db.commit()
        print(f"STAFF USERS OK ({count} created/linked)")
    except Exception as exc:
        db.rollback()
        import traceback

        traceback.print_exc()
        raise
    finally:
        db.close()