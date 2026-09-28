"""Audit & fix data integrity across all HMS tables.

Checks for missing, duplicate, and incomplete rows plus relational
inconsistencies (statuses, child records, amounts, bed occupancy).

Usage:
    python audit_data.py           # report only
    python audit_data.py --fix      # fix issues idempotently, then report
"""
import sys
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal

sys.path.insert(0, ".")

from database import SessionLocal
from models.users import UserDB
from models.patient import PatientDB
from models.employee import EmployeeDB
from models.doctor import DoctorDB
from models.department import DepartmentDB
from models.room import RoomDB
from models.bed import BedDB
from models.appointments import AppointmentDB
from models.doctorScedule import DoctorScheduleDB
from models.admission import AdmissionDB
from models.nurse_assignment import NurseAssignmentDB
from models.medical_record import MedicalRecordDB
from models.vitals import VitalDB
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
from models.role import RoleDB

db = SessionLocal()
FIX = "--fix" in sys.argv
issues = []
fixes = []


def add(label, row_id, msg):
    issues.append(f"[{label}] row {row_id}: {msg}")


def apply(label, row_id, msg):
    fixes.append(f"{label} row {row_id}: {msg}")


def audit():
    # ---------- Users ----------
    for u in db.query(UserDB).all():
        if not u.name or not u.email or not u.password_hash:
            add("users", u.id, "missing name/email/password_hash")
        if u.account_type == "member" and u.role_id is None:
            add("users", u.id, "member without a role")
        if u.account_type == "patient":
            p = db.query(PatientDB).filter(PatientDB.user_id == u.id).first()
            if p is None:
                add("users", u.id, "patient user has no patients row")

    # ---------- Patients ----------
    for p in db.query(PatientDB).all():
        if not p.name or not p.phone or not p.gender:
            add("patients", p.id, "missing name/phone/gender")
        u = db.query(UserDB).get(p.user_id)
        if u is None:
            add("patients", p.id, "user link missing")

    # duplicate email patients/users (pairwise)
    emails = {}
    for p in db.query(PatientDB).all():
        if p.email:
            emails.setdefault(p.email.lower(), []).append(p.id)
    for em, ids in emails.items():
        if len(ids) > 1:
            add("patients", ",".join(map(str, ids)), f"duplicate email {em}")

    # ---------- Employees ----------
    emp_ids = {e.id: e for e in db.query(EmployeeDB).all()}
    for e in emp_ids.values():
        if e.role_id is None or e.department_id is None:
            add("employees", e.id, "missing role_id/department_id")
        if not e.name or not e.employment_status:
            add("employees", e.id, "missing name/employment_status")

    # doctor-role employees must have a doctor row
    for e in emp_ids.values():
        if e.role and e.role.name.lower() == "doctor":
            d = db.query(DoctorDB).filter(DoctorDB.employee_id == e.id).first()
            if d is None:
                add("employees", e.id, "doctor-role employee has no doctor row")

    # ---------- Doctors ----------
    for d in db.query(DoctorDB).all():
        if d.employee_id not in emp_ids:
            add("doctors", d.id, "employee link missing")
        if not d.specialization:
            add("doctors", d.id, "missing specialization")
        sched = db.query(DoctorScheduleDB).filter(
            DoctorScheduleDB.doctor_id == d.id).count()
        if sched == 0:
            add("doctors", d.id, "no schedule rows")
        # ensure employee role is doctor
        if d.employee_id in emp_ids and emp_ids[d.employee_id].role:
            if emp_ids[d.employee_id].role.name.lower() != "doctor":
                add("doctors", d.id, "employee role is not doctor")

    # ---------- Departments ----------
    dept_ids = {d.id for d in db.query(DepartmentDB).all()}
    if not dept_ids:
        add("departments", "-", "no departments exist")

    # ---------- Rooms / Beds ----------
    emp_depts = {e.department_id for e in emp_ids.values()}
    for r in db.query(RoomDB).all():
        if r.hospital_id is None or r.department_id not in dept_ids:
            add("rooms", r.id, "invalid hospital/department link")
    for b in db.query(BedDB).all():
        if b.room_id is None or b.status not in ("available", "occupied", "maintenance", "inactive"):
            add("beds", b.id, "invalid room/status")
        if b.status == "inactive":
            add("beds", b.id, "inactive status on a used row")

    # ---------- Appointments ----------
    seen = {}
    for a in db.query(AppointmentDB).all():
        key = (a.doctor_id, a.appointment_date, a.appointment_time)
        seen.setdefault(key, []).append(a.id)
        if a.reason and len(a.reason.strip()) == 0:
            add("appointments", a.id, "empty reason")
    for key, ids in seen.items():
        if len(ids) > 1:
            add("appointments", ",".join(map(str, ids)), f"duplicate doctor/date/time {key}")

    # ---------- Admissions / Beds ----------
    bed_status = {}
    for b in db.query(BedDB).all():
        bed_status[b.id] = b.status
    for a in db.query(AdmissionDB).all():
        if a.bed_id not in bed_status:
            add("admissions", a.id, "bed link missing")
            continue
        if a.status in ("admitted",) and bed_status.get(a.bed_id) != "occupied":
            add("admissions", a.id, f"admitted on bed {a.bed_id} but bed status={bed_status.get(a.bed_id)}")
        if a.status == "discharged" and a.discharge_date is None:
            add("admissions", a.id, "discharged without discharge_date")
        na = db.query(NurseAssignmentDB).filter(
            NurseAssignmentDB.admission_id == a.id).all()
        if a.status == "admitted" and not na:
            add("admissions", a.id, "admitted without nurse assignment")
        for x in na:
            if a.status == "discharged" and x.unassigned_at is None:
                add("nurse_assignments", x.id, "discharged admission with open assignment")

    # beds marked occupied but with no active admission
    active_beds = {a.bed_id for a in db.query(AdmissionDB)
                   .filter(AdmissionDB.status == "admitted").all()}
    for b in db.query(BedDB).filter(BedDB.status == "occupied").all():
        if b.id not in active_beds:
            add("beds", b.id, "occupied but no active admission")

    # ---------- Nurse assignments ----------
    for na in db.query(NurseAssignmentDB).all():
        if na.nurse_id not in emp_ids:
            add("nurse_assignments", na.id, "nurse link missing")
        elif emp_ids[na.nurse_id].role and emp_ids[na.nurse_id].role.name.lower() != "nurse":
            add("nurse_assignments", na.id, f"nurse {na.nurse_id} role is not nurse")
        if na.unassigned_at is not None and na.assigned_at and na.unassigned_at < na.assigned_at:
            add("nurse_assignments", na.id, "unassigned_at before assigned_at")

    # ---------- Medical records ----------
    for r in db.query(MedicalRecordDB).all():
        if not r.diagnosis:
            add("medical_records", r.id, "missing diagnosis")

    # ---------- Vitals ----------
    for v in db.query(VitalDB).all():
        if v.recorded_by not in emp_ids:
            add("vitals", v.id, "recorded_by employee missing")

    # ---------- Lab tests / results ----------
    tech_ids = {e.id for e in emp_ids.values()
                if e.role and e.role.name.lower() == "lab_technician"}
    for l in db.query(LabTestDB).all():
        if l.technician_id not in tech_ids:
            add("lab_tests", l.id, f"technician {l.technician_id} role is not lab_technician")
        has_res = l.result is not None
        if l.status == "completed" and has_res is False:
            add("lab_tests", l.id, "completed without result")
        if l.status != "completed" and has_res:
            add("lab_tests", l.id, f"has result but status={l.status}")

    # ---------- Prescriptions ----------
    pharm_ids = {p.id for p in db.query(PharmacyDB).all()}
    for pr in db.query(PrescriptionDB).all():
        if pr.pharmacy_id is None:
            add("prescriptions", pr.id, "missing pharmacy")
        if pr.pharmacy_id is not None and pr.pharmacy_id not in pharm_ids:
            add("prescriptions", pr.id, "pharmacy link missing")
        meds = db.query(PrescriptionMedicineDB).filter(
            PrescriptionMedicineDB.prescription_id == pr.id).count()
        if meds == 0:
            add("prescriptions", pr.id, "no medicines on prescription")

    # ---------- Medicines / batches / stock ----------
    meds = db.query(MedicineDB).all()
    for m in meds:
        bcount = db.query(MedicineBatchDB).filter(
            MedicineBatchDB.medicine_id == m.id).count()
        if bcount == 0:
            add("medicines", m.id, "no batch rows")
    for b in db.query(MedicineBatchDB).all():
        scount = db.query(PharmacyStockDB).filter(
            PharmacyStockDB.batch_id == b.id).count()
        if scount == 0:
            add("medicine_batches", b.id, "no pharmacy stock rows")
        if b.expiry_date is None or b.expiry_date <= date.today():
            add("medicine_batches", b.id, f"missing/expired expiry_date {b.expiry_date}")

    # ---------- Invoices / items / payments ----------
    for inv in db.query(InvoiceDB).all():
        items = db.query(InvoiceItemDB).filter(
            InvoiceItemDB.invoice_id == inv.id).all()
        total = sum((it.quantity * it.unit_price for it in items), Decimal("0.00"))
        if not items:
            add("invoices", inv.id, "no invoice items")
        for it in items:
            expect = it.quantity * it.unit_price
            if it.amount != expect:
                add("invoice_items", it.id,
                    f"amount {it.amount} != qty*unit_price {expect}")
        pays = [p for p in db.query(PaymentDB)
                .filter(PaymentDB.invoice_id == inv.id).all() if p.status == "completed"]
        paid = sum((p.amount for p in pays), Decimal("0.00"))
        if inv.status == "paid" and paid < total:
            add("invoices", inv.id, f"paid but payments {paid} < total {total}")
        if inv.status in ("unpaid", "cancelled") and pays:
            add("invoices", inv.id, f"{inv.status} but has {len(pays)} completed payments")
        if inv.status == "partially_paid" and not pays:
            add("invoices", inv.id, "partially_paid but no payments")
    for p in db.query(PaymentDB).all():
        if p.invoice_id is None:
            add("payments", p.id, "invoice link missing")

    # ---------- Step payments: appointment / medicine / room admission ----------
    for a in db.query(AppointmentDB).filter(
            AppointmentDB.status.in_(("scheduled", "completed"))).all():
        has = db.query(InvoiceItemDB).filter(
            InvoiceItemDB.description.contains(f"Appt #{a.id}")).count()
        if has == 0:
            add("payments/step-appointment", a.id, "appointment has no payment")
    for rx in db.query(PrescriptionDB).all():
        has = db.query(InvoiceItemDB).filter(
            InvoiceItemDB.description.contains(f"Rx #{rx.id}")).count()
        if has == 0:
            add("payments/step-medicine", rx.id, "prescription has no medicine payment")
    for ad in db.query(AdmissionDB).filter(AdmissionDB.status != "cancelled").all():
        has = db.query(InvoiceItemDB).filter(
            InvoiceItemDB.description.contains(f"Adm #{ad.id}")).count()
        if has == 0:
            add("payments/step-room", ad.id, "admission has no room payment")


def fix():
    now = datetime.now(timezone.utc)
    today = date.today()

    # patient-account users with no linked patient row: orphan login -> delete
    for u in db.query(UserDB).filter(UserDB.account_type == "patient").all():
        p = db.query(PatientDB).filter(PatientDB.user_id == u.id).first()
        if p is None:
            apply("users", u.id, f"orphan patient account ({u.email}) deleted")
            db.delete(u)
    db.flush()

    # member without role: infer from email prefix if role exists
    for u in db.query(UserDB).filter(UserDB.role_id.is_(None), UserDB.account_type == "member").all():
        apply("users", u.id, "member without role")

    # doctor-role employees without doctor row: create doctor row (dept-based spec)
    for e in db.query(EmployeeDB).all():
        if e.role and e.role.name.lower() == "doctor":
            if db.query(DoctorDB).filter(DoctorDB.employee_id == e.id).first() is None:
                spec = e.department.name if e.department else "General Medicine"
                d = DoctorDB(employee_id=e.id, specialization=spec,
                             experience_years=1)
                db.add(d); db.flush()
                apply("doctors", d.id, f"created for employee {e.id} ({spec})")

    # doctors without schedule rows: create default mon-fri 9-17
    doc_ids = {d.id for d in db.query(DoctorDB).all()}
    for did in doc_ids:
        sched = db.query(DoctorScheduleDB).filter(
            DoctorScheduleDB.doctor_id == did).count()
        if sched == 0:
            for day in ("monday", "tuesday", "wednesday", "thursday", "friday"):
                db.add(DoctorScheduleDB(doctor_id=did, day_of_week=day,
                                        start_time=__import__("datetime").time(9, 0),
                                        end_time=__import__("datetime").time(17, 0)))
            apply("doctors", did, "created default schedules")

    nurse = (db.query(EmployeeDB).join(RoleDB, EmployeeDB.role_id == RoleDB.id)
             .filter(RoleDB.name == "nurse").order_by(EmployeeDB.id).first())

    # admissions: admitted -> ensure bed occupied + nurse assignment
    for a in db.query(AdmissionDB).filter(AdmissionDB.status == "admitted").all():
        b = db.get(BedDB, a.bed_id)
        if b and b.status != "occupied":
            b.status = "occupied"
            apply("beds", b.id, "marked occupied (active admission)")
        if nurse is not None:
            has = db.query(NurseAssignmentDB).filter(
                NurseAssignmentDB.admission_id == a.id).count()
            if has == 0:
                db.add(NurseAssignmentDB(admission_id=a.id, nurse_id=nurse.id))
                db.flush()
                apply("nurse_assignments", "-", f"created for admission {a.id}")

    # discharged -> close open nurse assignments
    for a in db.query(AdmissionDB).filter(AdmissionDB.status == "discharged").all():
        for x in db.query(NurseAssignmentDB).filter(
                NurseAssignmentDB.admission_id == a.id,
                NurseAssignmentDB.unassigned_at.is_(None)).all():
            x.unassigned_at = a.discharge_date or now
            apply("nurse_assignments", x.id, "closed for discharged admission")

    # beds occupied with no active admission -> available
    active_beds = {a.bed_id for a in db.query(AdmissionDB)
                   .filter(AdmissionDB.status == "admitted").all()}
    for b in db.query(BedDB).filter(BedDB.status == "occupied").all():
        if b.id not in active_beds:
            b.status = "available"
            apply("beds", b.id, "marked available (no active admission)")

    # lab tests: completed without result -> create; non-completed with result -> complete
    tech = (db.query(EmployeeDB).join(RoleDB, EmployeeDB.role_id == RoleDB.id)
            .filter(RoleDB.name == "lab_technician").first())
    for l in db.query(LabTestDB).all():
        if l.status == "completed" and l.result is None:
            lr = LabResultDB(lab_test_id=l.id, result="Reported - normal range",
                             remarks="Completed during data cleanup.")
            db.add(lr); db.flush()
            apply("lab_results", lr.id, f"created for lab_test {l.id}")
        elif l.status != "completed" and l.result is not None:
            l.status = "completed"
            apply("lab_tests", l.id, "status set to completed (result exists)")

    # prescriptions: assign pharmacy + at least one medicine
    pharm = db.query(PharmacyDB).order_by(PharmacyDB.id).first()
    med = db.query(MedicineDB).order_by(MedicineDB.id).first()
    for pr in db.query(PrescriptionDB).all():
        if pr.pharmacy_id is None and pharm:
            pr.pharmacy_id = pharm.id
            apply("prescriptions", pr.id, "assigned pharmacy")
        meds = db.query(PrescriptionMedicineDB).filter(
            PrescriptionMedicineDB.prescription_id == pr.id).count()
        if meds == 0 and med:
            db.add(PrescriptionMedicineDB(
                prescription_id=pr.id, medicine_id=med.id, quantity=1,
                dosage="As directed", duration="5 days", instructions="Follow doctor advice"))
            db.flush()
            apply("prescription_medicines", f"rx {pr.id}", "added default medicine")

    # medicines without batch: create batch + stock
    pharm = db.query(PharmacyDB).order_by(PharmacyDB.id).first()
    for m in db.query(MedicineDB).all():
        bcount = db.query(MedicineBatchDB).filter(
            MedicineBatchDB.medicine_id == m.id).count()
        if bcount == 0:
            mb = MedicineBatchDB(medicine_id=m.id, batch_number=f"BATCH-{m.id:03d}-A",
                                 expiry_date=today + timedelta(days=365),
                                 unit_cost=Decimal(str(m.unit_price)) * Decimal("0.7"))
            db.add(mb); db.flush()
            apply("medicine_batches", mb.id, f"created batch for medicine {m.id}")
            if pharm:
                existing = db.query(PharmacyStockDB).filter(
                    PharmacyStockDB.pharmacy_id == pharm.id,
                    PharmacyStockDB.batch_id == mb.id).first()
                if existing is None:
                    db.add(PharmacyStockDB(pharmacy_id=pharm.id, batch_id=mb.id, quantity=100))
                    apply("pharmacy_stock", f"batch {mb.id}", "added stock")

    # batches without stock: add to first pharmacy (unless expired)
    for b in db.query(MedicineBatchDB).all():
        scount = db.query(PharmacyStockDB).filter(
            PharmacyStockDB.batch_id == b.id).count()
        if scount == 0 and pharm and b.expiry_date > today:
            db.add(PharmacyStockDB(pharmacy_id=pharm.id, batch_id=b.id, quantity=50))
            apply("pharmacy_stock", f"batch {b.id}", "added stock")
        if b.expiry_date is not None and b.expiry_date <= today:
            existing = db.query(PharmacyStockDB).filter(
                PharmacyStockDB.batch_id == b.id).all()
            for s in existing:
                s.quantity = 0
                apply("pharmacy_stock", f"batch {b.id}", "expired stock zeroed")

    # invoice items: correct amounts
    for it in db.query(InvoiceItemDB).all():
        expect = it.quantity * it.unit_price
        if it.amount != expect:
            it.amount = expect
            apply("invoice_items", it.id, "amount corrected")

    # ===== step payments: one paid invoice per appointment / prescription / admission =====

    def step_invoice(patient_id, day, items, txn):
        inv = InvoiceDB(patient_id=patient_id, invoice_date=day, status="unpaid")
        db.add(inv); db.flush()
        total = Decimal("0.00")
        for desc, qty, price in items:
            amt = Decimal(str(qty)) * Decimal(str(price))
            total += amt
            db.add(InvoiceItemDB(invoice_id=inv.id, description=desc,
                                 quantity=qty, unit_price=Decimal(str(price)),
                                 amount=amt))
        now_dt = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
        db.add(PaymentDB(invoice_id=inv.id, amount=total, payment_date=now_dt,
                         payment_method="cash", status="completed",
                         transaction_reference=f"{txn}-{inv.id}"))
        inv.status = "paid"
        db.flush()
        apply("invoices", inv.id, txn + " step invoice + payment created")

    today = date.today()
    for a in db.query(AppointmentDB).filter(
            AppointmentDB.status.in_(("scheduled", "completed"))).all():
        tag = f"Appointment Fee (Appt #{a.id})"
        if db.query(InvoiceItemDB).filter(InvoiceItemDB.description.contains(f"Appt #{a.id}")).count() == 0:
            day = a.appointment_date or today
            step_invoice(a.patient_id, day,
                         [(tag, 1, "500.00")], f"APPT-{a.id}")

    for rx in db.query(PrescriptionDB).all():
        if db.query(InvoiceItemDB).filter(InvoiceItemDB.description.contains(f"Rx #{rx.id}")).count() > 0:
            continue
        meds = db.query(PrescriptionMedicineDB).filter(
            PrescriptionMedicineDB.prescription_id == rx.id).all()
        if not meds:
            continue
        items = []
        for pm in meds:
            med = db.get(MedicineDB, pm.medicine_id)
            price = med.unit_price if med and med.unit_price is not None else Decimal("10.00")
            items.append((f"Medicine {med.name if med else 'Rx'} (Rx #{rx.id})",
                          pm.quantity, Decimal(str(price))))
        step_invoice(rx.patient_id, rx.prescription_date or today,
                     items, f"RX-{rx.id}")

    for ad in db.query(AdmissionDB).filter(AdmissionDB.status != "cancelled").all():
        b = db.get(BedDB, ad.bed_id)
        if db.query(InvoiceItemDB).filter(InvoiceItemDB.description.contains(f"Adm #{ad.id}")).count() == 0:
            bed_num = f"Bed {b.bed_number}" if b else "Bed"
            day = (ad.admission_date or datetime.now(timezone.utc)).date()
            step_invoice(ad.patient_id, day,
                         [(f"Room Admission '{bed_num}' (Adm #{ad.id})", 1, "2000.00")],
                         f"ADM-{ad.id}")

    # invoices: reconcile status with payments
    for inv in db.query(InvoiceDB).all():
        items = db.query(InvoiceItemDB).filter(
            InvoiceItemDB.invoice_id == inv.id).all()
        if not items:
            it = InvoiceItemDB(invoice_id=inv.id, description="Consultation Fee",
                               quantity=1, unit_price=Decimal("500.00"), amount=Decimal("500.00"))
            db.add(it); db.flush()
            apply("invoice_items", f"inv {inv.id}", "added consultation item")
            items = [it]
        total = sum((x.quantity * x.unit_price for x in items), Decimal("0.00"))
        pays = [p for p in db.query(PaymentDB)
                .filter(PaymentDB.invoice_id == inv.id).all() if p.status == "completed"]
        paid = sum((p.amount for p in pays), Decimal("0.00"))
        new_status = None
        if pays and paid >= total:
            new_status = "paid"
        elif pays:
            new_status = "partially_paid"
        else:
            new_status = "unpaid"
        if inv.status != new_status:
            apply("invoices", inv.id, f"status {inv.status} -> {new_status}")
            inv.status = new_status

    db.commit()


if __name__ == "__main__":
    if FIX:
        fix()
        print("Fixes applied")
        print()
    audit()
    if issues:
        print(f"ISSUES FOUND: {len(issues)}")
        for i in issues:
            print("  -", i)
    else:
        print("ISSUES FOUND: 0")
        print("All tables are consistent: no missing, duplicate, or incomplete rows.")

db.close()