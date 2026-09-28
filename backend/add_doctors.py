"""Add additional doctors (employee + DoctorDB + login + schedules), idempotent."""
import sys
from datetime import date, time

sys.path.insert(0, ".")

from database import SessionLocal
from models.role import RoleDB
from models.users import UserDB
from models.hospital import HospitalDB
from models.department import DepartmentDB
from models.employee import EmployeeDB
from models.doctor import DoctorDB
from models.doctorScedule import DoctorScheduleDB
from utils.security import hash_password

DOCTORS = [
    ("Dr. Ananya Rao", "ananya@hms.com", "Cardiology", 11),
    ("Dr. Vikram Iyer", "vikram@hms.com", "Neurology", 14),
    ("Dr. Meera Nair", "meera@hms.com", "Pediatrics", 9),
    ("Dr. Arjun Kapoor", "arjun@hms.com", "General Medicine", 16),
    ("Dr. Kavya Menon", "kavya@hms.com", "Radiology", 7),
    ("Dr. Rohan Desai", "rohan@hms.com", "Orthopedics", 13),
]

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]

db = SessionLocal()
try:
    role_ids = {r.name: r.id for r in db.query(RoleDB).all()}
    hosp = db.query(HospitalDB).first()
    if not hosp:
        raise SystemExit("No hospital seeded. Run setup_schema.py + seed_all.py first.")

    dept_by_name = {
        d.name: d
        for d in db.query(DepartmentDB)
        .filter(DepartmentDB.hospital_id == hosp.id)
        .all()
    }

    existing_users = {u.email: u for u in db.query(UserDB).all()}

    created = 0
    for name, email, spec, exp in DOCTORS:
        # department lookup
        dept = dept_by_name.get(spec)
        if dept is None:
            print(f"SKIP {name}: department '{spec}' not found")
            continue

        employee = (
            db.query(EmployeeDB).filter(EmployeeDB.email == email).first()
        )
        if employee is None:
            employee = EmployeeDB(
                name=name,
                role_id=role_ids["doctor"],
                department_id=dept.id,
                dob=date(1980, 1, 1),
                gender="Female" if "Ananya" in name or "Meera" in name or "Kavya" in name else "Male",
                phone="98" + str(hash(email) % 10_000_000).zfill(7),
                email=email,
                address="Mumbai",
                hire_date=date(2018, 6, 1),
                salary=95000,
                employment_status="active",
            )
            db.add(employee)
            db.flush()
            print(f"  employee: {name}")

        doctor = (
            db.query(DoctorDB).filter(DoctorDB.employee_id == employee.id).first()
        )
        if doctor is None:
            doctor = DoctorDB(
                employee_id=employee.id,
                specialization=spec,
                experience_years=exp,
            )
            db.add(doctor)
            db.flush()
            print(f"  doctor: {name} ({spec})")

        # create a login account (doctor role)
        if email not in existing_users:
            user = UserDB(
                name=name,
                email=email,
                password_hash=hash_password("Doctor@123"),
                account_type="member",
                role_id=role_ids["doctor"],
                is_active=True,
            )
            db.add(user)
            db.flush()
            existing_users[email] = user
            # link employee.user if the field exists (best effort)
            try:
                employee.user_id = user.id
            except Exception:
                pass
            print(f"  login: {email} / Doctor@123")

        # schedules
        for day in DAYS:
            has = (
                db.query(DoctorScheduleDB)
                .filter(
                    DoctorScheduleDB.doctor_id == doctor.id,
                    DoctorScheduleDB.day_of_week == day,
                )
                .first()
            )
            if has:
                continue
            db.add(
                DoctorScheduleDB(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                )
            )
        created += 1
        print(f"OK: {name} ({spec})")

    db.commit()
    print(f"\nADD DOCTORS COMPLETE: {created} new doctors ensured")
    print("Logins: <firstname>@hms.com / Doctor@123")

except Exception:
    db.rollback()
    import traceback

    traceback.print_exc()
finally:
    db.close()