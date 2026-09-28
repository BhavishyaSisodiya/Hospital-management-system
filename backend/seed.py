import sys
sys.path.insert(0, ".")
from database import SessionLocal
from models.users import UserDB
from models.role import RoleDB
from utils.security import hash_password

db = SessionLocal()
try:
    # Create roles
    role_map = {}
    for name in ["admin", "doctor", "nurse", "receptionist", "pharmacist", "lab_technician", "accountant"]:
        r = db.query(RoleDB).filter(RoleDB.name == name).first()
        if not r:
            r = RoleDB(name=name, description=f"{name} role")
            db.add(r)
            db.flush()
        role_map[name] = r.id
    print(f"Roles: {role_map}")

    # Create users
    users = [
        ("Admin User", "admin@hms.com", "Admin@123", "member", role_map["admin"]),
        ("Dr. Smith", "doctor@hms.com", "Doctor@123", "member", role_map["doctor"]),
        ("Nurse Joy", "nurse@hms.com", "Nurse@123", "member", role_map["nurse"]),
        ("Receptionist Kim", "reception@hms.com", "Recep@123", "member", role_map["receptionist"]),
        ("Test Patient", "patient@hms.com", "Patient@123", "patient", None),
    ]
    for name, email, pwd, atype, rid in users:
        if db.query(UserDB).filter(UserDB.email == email).first():
            print(f"Exists: {email}")
            continue
        u = UserDB(name=name, email=email, password_hash=hash_password(pwd),
                   account_type=atype, role_id=rid, is_active=True)
        db.add(u)
        db.flush()
        print(f"Created: {email}")

    db.commit()
    print("Done!")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
    import traceback; traceback.print_exc()
finally:
    db.close()
