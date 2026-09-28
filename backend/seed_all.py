"""Comprehensive seed for all HMS tables."""
import sys, random
from datetime import date, time, datetime, timedelta, timezone
sys.path.insert(0, ".")

from database import SessionLocal, engine
from sqlalchemy import text
from models.role import RoleDB
from models.users import UserDB
from models.hospital import HospitalDB
from models.department import DepartmentDB
from models.employee import EmployeeDB
from models.doctor import DoctorDB
from models.patient import PatientDB
from models.room import RoomDB
from models.bed import BedDB
from models.appointments import AppointmentDB
from models.doctorScedule import DoctorScheduleDB
from models.medical_record import MedicalRecordDB
from models.vitals import VitalDB
from models.admission import AdmissionDB
from models.nurse_assignment import NurseAssignmentDB
from models.test import TestTypeDB
from models.lab import LabTestDB
from models.lab_result import LabResultDB
from models.medicine import MedicineDB
from models.medical_batch import MedicineBatchDB
from models.pharmacy import PharmacyDB
from models.pharmacy_Stock import PharmacyStockDB
from models.prescription import PrescriptionDB
from models.prescription_medicine import PrescriptionMedicineDB
from models.invoice import InvoiceDB
from models.invoice_item import InvoiceItemDB
from models.payment import PaymentDB
from utils.security import hash_password

db = SessionLocal()
try:
    now = datetime.now(timezone.utc)

    # ── 1. Roles ─────────────────────────────────────────────
    role_names = ["admin", "doctor", "nurse", "receptionist", "pharmacist", "lab_technician", "accountant"]
    role_ids = {}
    for name in role_names:
        r = db.query(RoleDB).filter(RoleDB.name == name).first()
        if not r:
            r = RoleDB(name=name, description=f"{name} role")
            db.add(r); db.flush()
        role_ids[name] = r.id
    print(f"Roles: {role_ids}")

    # ── 2. Users (staff + patients) ──────────────────────────
    staff_emails = {e for _, e, _ in [
        ("Admin User", "admin@hms.com", "Admin@123"),
        ("Dr. Smith", "doctor@hms.com", "Doctor@123"),
        ("Nurse Joy", "nurse@hms.com", "Nurse@123"),
        ("Receptionist Kim", "reception@hms.com", "Recep@123"),
    ]}
    existing_users = {u.email: u for u in db.query(UserDB).all()}

    def get_or_create_user(name, email, pwd, atype, rid=None):
        if email in existing_users:
            return existing_users[email]
        u = UserDB(name=name, email=email, password_hash=hash_password(pwd),
                   account_type=atype, role_id=rid, is_active=True)
        db.add(u); db.flush()
        existing_users[email] = u
        print(f"  user: {email}")
        return u

    # Staff users already exist; create additional staff users for doctor/nurse
    user_admin = get_or_create_user("Admin User", "admin@hms.com", "Admin@123", "member", role_ids["admin"])

    # We'll create doctor/nurse/technician employees linked to NEW user accounts
    # But EmployeeDB is separate from UserDB. Doctors are employees + doctor record.
    # For simplicity, employees don't need user accounts in this schema.

    # Patient users
    patient_data = [
        ("Demo Patient", "patient@hms.com", "Patient@123", "Female", "9800000000", "1988-04-12", "99 Demo Lane, Mumbai"),
        ("Rahul Sharma", "patient1@hms.com", "Patient@123", "Male", "9876543210", "1990-05-15", "123 Main St, Delhi"),
        ("Priya Patel", "patient2@hms.com", "Patient@123", "Female", "9876543211", "1985-08-22", "456 Oak Ave, Mumbai"),
        ("Amit Kumar", "patient3@hms.com", "Patient@123", "Male", "9876543212", "1978-12-01", "789 Pine Rd, Bangalore"),
        ("Sneha Reddy", "patient4@hms.com", "Patient@123", "Female", "9876543213", "1995-03-10", "321 Elm St, Chennai"),
        ("Vikram Singh", "patient5@hms.com", "Patient@123", "Male", "9876543214", "1982-07-25", "654 Maple Dr, Pune"),
    ]
    patients = []
    for pname, pemail, ppwd, pgender, pphone, pdob, paddr in patient_data:
        u = get_or_create_user(pname, pemail, ppwd, "patient")
        existing_patient = db.query(PatientDB).filter(PatientDB.user_id == u.id).first()
        if existing_patient:
            patients.append(existing_patient)
            continue
        pt = PatientDB(name=pname, date_of_birth=date.fromisoformat(pdob),
                       gender=pgender, phone=pphone, email=pemail,
                       address=paddr, user_id=u.id)
        db.add(pt); db.flush()
        patients.append(pt)
        print(f"  patient: {pemail}")
    print(f"Patients: {len(patients)}")

    # ── 3. Hospital (seeded) ─────────────────────────────────
    hosp = db.query(HospitalDB).first()
    if not hosp:
        hosp = HospitalDB(name="City Care Hospital", address="MG Road, Mumbai",
                          phone="02212345678", email="info@citycare.com")
        db.add(hosp); db.flush()
    print(f"Hospital: {hosp.id} {hosp.name}")

    # ── 4. Departments ───────────────────────────────────────
    dept_names = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General Medicine",
                  "Emergency", "Radiology", "Oncology"]
    depts = []
    for dname in dept_names:
        existing = db.query(DepartmentDB).filter(
            DepartmentDB.hospital_id == hosp.id, DepartmentDB.name == dname).first()
        if existing:
            depts.append(existing); continue
        d = DepartmentDB(name=dname, description=f"{dname} department",
                         hospital_id=hosp.id)
        db.add(d); db.flush()
        depts.append(d)
    print(f"Departments: {len(depts)}")

    # ── 5. Employees (doctors, nurses, technicians) ──────────
    def make_emp(name, role_name, dept, gender="Male", phone=None, email=None, salary=60000):
        existing = db.query(EmployeeDB).filter(EmployeeDB.email == email).first() if email else None
        if existing: return existing
        e = EmployeeDB(name=name, role_id=role_ids[role_name], department_id=dept.id,
                       dob=date(1985,1,1), gender=gender, phone=phone, email=email,
                       address="Mumbai", hire_date=date(2020,1,1),
                       salary=salary, employment_status="active")
        db.add(e); db.flush()
        print(f"  employee: {name} ({role_name})")
        return e

    emp_dr_arya = make_emp("Dr. Arya Mehta", "doctor", depts[0], "Female", "9800000001", "arya@hms.com", 90000)
    emp_dr_raj = make_emp("Dr. Raj Gupta", "doctor", depts[1], "Male", "9800000002", "raj@hms.com", 95000)
    emp_dr_pooja = make_emp("Dr. Pooja Das", "doctor", depts[2], "Female", "9800000003", "pooja@hms.com", 88000)
    emp_dr_karan = make_emp("Dr. Karan Bhat", "doctor", depts[4], "Male", "9800000004", "karan@hms.com", 92000)
    emp_nurse_lisa = make_emp("Lisa Nurse", "nurse", depts[5], "Female", "9800000005", "lisa@hms.com", 45000)
    emp_nurse_tom = make_emp("Tom Nurse", "nurse", depts[0], "Male", "9800000006", "tom@hms.com", 45000)
    emp_tech_rekha = make_emp("Rekha Tech", "lab_technician", depts[6], "Female", "9800000007", "rekha@hms.com", 40000)
    emp_reception = make_emp("Aarti Reception", "receptionist", depts[5], "Female", "9800000008", "aarti@hms.com", 35000)
    emp_pharma = make_emp("Suresh Pharmacist", "pharmacist", depts[5], "Male", "9800000009", "suresh@hms.com", 42000)

    # ── 6. Doctors ───────────────────────────────────────────
    def make_doc(emp, spec, exp):
        existing = db.query(DoctorDB).filter(DoctorDB.employee_id == emp.id).first()
        if existing: return existing
        d = DoctorDB(employee_id=emp.id, specialization=spec, experience_years=exp)
        db.add(d); db.flush()
        print(f"  doctor: {emp.name} ({spec})")
        return d

    doc1 = make_doc(emp_dr_arya, "Cardiology", 12)
    doc2 = make_doc(emp_dr_raj, "Neurology", 8)
    doc3 = make_doc(emp_dr_pooja, "Orthopedics", 15)
    doc4 = make_doc(emp_dr_karan, "General Medicine", 10)

    # ── 7. Rooms ─────────────────────────────────────────────
    rooms_data = [
        ("ICU-101", "ICU", "available", depts[5]),
        ("GEN-201", "General", "available", depts[4]),
        ("GEN-202", "General", "occupied", depts[4]),
        ("PVT-301", "Private", "available", depts[0]),
        ("PVT-302", "Private", "maintenance", depts[1]),
    ]
    rooms = []
    for rnum, rtype, rstatus, rdept in rooms_data:
        existing = db.query(RoomDB).filter(RoomDB.hospital_id == hosp.id, RoomDB.room_number == rnum).first()
        if existing:
            rooms.append(existing); continue
        rm = RoomDB(room_number=rnum, room_type=rtype, status=rstatus,
                    hospital_id=hosp.id, department_id=rdept.id)
        db.add(rm); db.flush()
        rooms.append(rm)
    print(f"Rooms: {len(rooms)}")

    # ── 8. Beds ──────────────────────────────────────────────
    beds = []
    for rm in rooms:
        for bn in ["A", "B"]:
            existing = db.query(BedDB).filter(BedDB.room_id == rm.id, BedDB.bed_number == bn).first()
            if existing:
                beds.append(existing); continue
            b = BedDB(bed_number=bn, room_id=rm.id, status="available")
            db.add(b); db.flush()
            beds.append(b)
    print(f"Beds: {len(beds)}")

    # ── 9. Appointments ──────────────────────────────────────
    docs = [doc1, doc2, doc3, doc4]
    statuses = ["scheduled", "completed", "cancelled"]
    appts = []
    for i, pt in enumerate(patients[:4]):
        appt_date = date.today() - timedelta(days=random.randint(0, 30))
        appt_time = time(9 + i, 0)
        existing = db.query(AppointmentDB).filter(
            AppointmentDB.patient_id == pt.id,
            AppointmentDB.doctor_id == docs[i % len(docs)].id,
            AppointmentDB.appointment_date == appt_date
        ).first()
        if existing:
            appts.append(existing); continue
        a = AppointmentDB(
            patient_id=pt.id, doctor_id=docs[i % len(docs)].id,
            appointment_date=appt_date, appointment_time=appt_time,
            reason="Routine checkup" if i % 2 == 0 else "Follow-up",
            status=statuses[i % 3],
        )
        db.add(a); db.flush()
        appts.append(a)
    print(f"Appointments: {len(appts)}")

    # ── 10. Doctor Schedules ─────────────────────────────────
    days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    for doc in docs:
        for day in days[:3]:
            existing = db.query(DoctorScheduleDB).filter(
                DoctorScheduleDB.doctor_id == doc.id,
                DoctorScheduleDB.day_of_week == day).first()
            if existing: continue
            ds = DoctorScheduleDB(doctor_id=doc.id, day_of_week=day,
                                  start_time=time(9, 0), end_time=time(17, 0))
            db.add(ds)
    print("Doctor schedules created")

    # ── 11. Medical Records ──────────────────────────────────
    diagnoses = ["Hypertension", "Type 2 Diabetes", "Migraine", "Fracture - Left Arm", "Common Cold"]
    for i, pt in enumerate(patients[:4]):
        existing = db.query(MedicalRecordDB).filter(
            MedicalRecordDB.patient_id == pt.id).first()
        if existing: continue
        mr = MedicalRecordDB(
            patient_id=pt.id, doctor_id=docs[i % len(docs)].id,
            diagnosis=diagnoses[i % len(diagnoses)],
            notes=f"Initial diagnosis. Patient presents with standard symptoms. Follow-up in 2 weeks.",
            record_date=now - timedelta(days=random.randint(5, 60)),
        )
        db.add(mr)
    print("Medical records created")

    # ── 12. Vitals ───────────────────────────────────────────
    for i, pt in enumerate(patients[:4]):
        existing = db.query(VitalDB).filter(VitalDB.patient_id == pt.id).first()
        if existing: continue
        v = VitalDB(
            patient_id=pt.id,
            recorded_by=emp_nurse_lisa.id,
            temperature=round(random.uniform(97.5, 99.5), 1),
            heart_rate=random.randint(60, 100),
            blood_pressure_systolic=random.randint(110, 140),
            blood_pressure_diastolic=random.randint(70, 90),
            respiratory_rate=random.randint(12, 20),
            oxygen_saturation=round(random.uniform(95.0, 99.9), 2),
            weight=round(random.uniform(55.0, 90.0), 2),
        )
        db.add(v)
    print("Vitals created")

    # ── 13. Admissions ───────────────────────────────────────
    available_beds = [b for b in beds if b.status == "available"]
    admissions = []
    for i, pt in enumerate(patients[:2]):
        if i >= len(available_beds): break
        existing = db.query(AdmissionDB).filter(
            AdmissionDB.patient_id == pt.id,
            AdmissionDB.status == "admitted").first()
        if existing:
            admissions.append(existing); continue
        ad = AdmissionDB(
            patient_id=pt.id, doctor_id=docs[i].id,
            bed_id=available_beds[i].id,
            admission_date=now - timedelta(days=random.randint(1, 10)),
            status="admitted",
        )
        db.add(ad); db.flush()
        admissions.append(ad)
        # Mark bed as occupied
        available_beds[i].status = "occupied"
    print(f"Admissions: {len(admissions)}")

    # ── 14. Nurse Assignments ─────────────────────────────────
    for ad in admissions:
        existing = db.query(NurseAssignmentDB).filter(
            NurseAssignmentDB.admission_id == ad.id).first()
        if existing: continue
        na = NurseAssignmentDB(admission_id=ad.id, nurse_id=emp_nurse_lisa.id)
        db.add(na)
    print("Nurse assignments created")

    # ── 15. Test Types ───────────────────────────────────────
    test_types_data = [
        ("Complete Blood Count", 500),
        ("Blood Sugar Fasting", 200),
        ("Lipid Profile", 800),
        ("Thyroid Panel", 600),
        ("X-Ray Chest", 400),
        ("MRI Brain", 3000),
        ("ECG", 300),
    ]
    test_types = []
    for tname, tprice in test_types_data:
        existing = db.query(TestTypeDB).filter(TestTypeDB.name == tname).first()
        if existing:
            test_types.append(existing); continue
        tt = TestTypeDB(name=tname, price=tprice)
        db.add(tt); db.flush()
        test_types.append(tt)
    print(f"Test types: {len(test_types)}")

    # ── 16. Lab Tests + Results ──────────────────────────────
    lt_statuses = ["completed", "pending", "in_progress"]
    for i, pt in enumerate(patients[:4]):
        existing = db.query(LabTestDB).filter(LabTestDB.patient_id == pt.id).first()
        if existing: continue
        lt = LabTestDB(
            test_type_id=test_types[i % len(test_types)].id,
            patient_id=pt.id, doctor_id=docs[i % len(docs)].id,
            technician_id=emp_tech_rekha.id,
            status=lt_statuses[i % 3],
        )
        db.add(lt); db.flush()
        if lt.status == "completed":
            lr = LabResultDB(
                lab_test_id=lt.id,
                result="Normal range" if i % 2 == 0 else "Slightly elevated",
                unit="g/dL" if i % 2 == 0 else "mg/dL",
                reference_range="12-16" if i % 2 == 0 else "70-110",
                remarks="No further action needed" if i % 2 == 0 else "Repeat test in 1 month",
            )
            db.add(lr)
    print("Lab tests + results created")

    # ── 17. Medicines ────────────────────────────────────────
    meds_data = [
        ("Paracetamol 500mg", "Cipla", 5),
        ("Amoxicillin 250mg", "Sun Pharma", 15),
        ("Metformin 500mg", "Dr. Reddy's", 12),
        ("Atorvastatin 10mg", "Cipla", 25),
        ("Amlodipine 5mg", "Lupin", 18),
        ("Omeprazole 20mg", "Ranbaxy", 10),
        ("Cetirizine 10mg", "Cipla", 8),
    ]
    meds = []
    for mname, mmanuf, mprice in meds_data:
        existing = db.query(MedicineDB).filter(MedicineDB.name == mname).first()
        if existing:
            meds.append(existing); continue
        m = MedicineDB(name=mname, manufacturer=mmanuf, unit_price=mprice)
        db.add(m); db.flush()
        meds.append(m)
    print(f"Medicines: {len(meds)}")

    # ── 18. Medicine Batches ─────────────────────────────────
    batches = []
    for med in meds:
        existing = db.query(MedicineBatchDB).filter(MedicineBatchDB.medicine_id == med.id).first()
        if existing:
            batches.append(existing); continue
        mb = MedicineBatchDB(
            medicine_id=med.id,
            batch_number=f"BATCH-{med.id:03d}-A",
            expiry_date=date.today() + timedelta(days=random.randint(90, 730)),
            unit_cost=float(med.unit_price) * 0.7,
        )
        db.add(mb); db.flush()
        batches.append(mb)
    print(f"Medicine batches: {len(batches)}")

    # ── 19. Pharmacy ─────────────────────────────────────────
    pharm = db.query(PharmacyDB).filter(PharmacyDB.hospital_id == hosp.id).first()
    if not pharm:
        pharm = PharmacyDB(name="Hospital Pharmacy", location="Ground Floor", hospital_id=hosp.id)
        db.add(pharm); db.flush()
    print(f"Pharmacy: {pharm.id}")

    # ── 20. Pharmacy Stock ───────────────────────────────────
    for batch in batches[:5]:
        existing = db.query(PharmacyStockDB).filter(
            PharmacyStockDB.pharmacy_id == pharm.id,
            PharmacyStockDB.batch_id == batch.id).first()
        if existing: continue
        ps = PharmacyStockDB(pharmacy_id=pharm.id, batch_id=batch.id,
                             quantity=random.randint(50, 200))
        db.add(ps)
    print("Pharmacy stock created")

    # ── 21. Prescriptions + Medicines ────────────────────────
    for i, pt in enumerate(patients[:3]):
        existing = db.query(PrescriptionDB).filter(PrescriptionDB.patient_id == pt.id).first()
        if existing: continue
        pr = PrescriptionDB(
            patient_id=pt.id, doctor_id=docs[i].id,
            pharmacy_id=pharm.id,
            prescription_date=date.today() - timedelta(days=random.randint(1, 14)),
        )
        db.add(pr); db.flush()
        pm = PrescriptionMedicineDB(
            prescription_id=pr.id, medicine_id=meds[i].id,
            quantity=random.randint(1, 3),
            dosage="500mg twice daily",
            duration="7 days",
            instructions="After meals",
        )
        db.add(pm)
    print("Prescriptions created")

    # ── 22. Invoices + Items + Payments ──────────────────────
    for i, pt in enumerate(patients[:4]):
        existing = db.query(InvoiceDB).filter(InvoiceDB.patient_id == pt.id).first()
        if existing: continue
        inv = InvoiceDB(patient_id=pt.id, status="unpaid")
        db.add(inv); db.flush()

        items = [
            ("Consultation Fee", 1, 500),
            ("Lab Test - " + test_types[i % len(test_types)].name, 1, float(test_types[i % len(test_types)].price)),
            ("Medicine - " + meds[i].name, 2, float(meds[i].unit_price)),
        ]
        total = 0
        for desc, qty, uprice in items:
            amt = qty * uprice
            total += amt
            ii = InvoiceItemDB(invoice_id=inv.id, description=desc,
                               quantity=qty, unit_price=uprice, amount=amt)
            db.add(ii)

        if i % 2 == 0:
            inv.status = "paid"
            pay = PaymentDB(invoice_id=inv.id, amount=total,
                            payment_method=random.choice(["cash", "card", "upi"]),
                            status="completed",
                            transaction_reference=f"TXN-{inv.id:04d}-{random.randint(1000,9999)}")
            db.add(pay)
    print("Invoices + items + payments created")

    db.commit()
    print("\n=== SEED COMPLETE ===")

except Exception as e:
    db.rollback()
    import traceback; traceback.print_exc()
finally:
    db.close()
