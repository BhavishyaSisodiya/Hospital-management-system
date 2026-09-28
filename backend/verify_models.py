from sqlalchemy import inspect
from sqlalchemy.orm import configure_mappers

from database import Base
import models


def verify_models():
    print("\nChecking SQLAlchemy models...\n")

    # Force SQLAlchemy to configure every mapper
    configure_mappers()

    print("✓ SQLAlchemy mappers configured successfully")

    expected_tables = {
        "users",
        "hospitals",
        "departments",
        "roles",
        "employees",
        "doctors",
        "patients",
        "appointments",
        "doctor_schedules",
        "medical_records",
        "vitals",
        "admissions",
        "rooms",
        "beds",
        "nurse_assignments",
        "test_types",
        "lab_tests",
        "lab_results",
        "medicines",
        "medicine_batches",
        "pharmacies",
        "pharmacy_stock",
        "prescriptions",
        "prescription_medicines",
        "invoices",
        "invoice_items",
        "payments",
    }

    actual_tables = set(Base.metadata.tables.keys())

    print(f"✓ Models loaded: {len(actual_tables)}")
    print(f"✓ Tables found: {len(actual_tables)}")

    missing = expected_tables - actual_tables
    unexpected = actual_tables - expected_tables

    if missing:
        print("\n❌ Missing tables:")
        for table in sorted(missing):
            print(f"   - {table}")

    if unexpected:
        print("\n❌ Unexpected tables:")
        for table in sorted(unexpected):
            print(f"   - {table}")

    if missing or unexpected:
        raise RuntimeError("Model/table verification failed")

    print("\n✓ All 27 expected tables are registered")

    # Verify every table has a primary key
    for table in Base.metadata.sorted_tables:
        if not table.primary_key.columns:
            raise RuntimeError(
                f"Table '{table.name}' has no primary key"
            )

    print("✓ All tables have primary keys")

    print("\n===================================")
    print("   MODEL VERIFICATION SUCCESSFUL")
    print("===================================\n")


if __name__ == "__main__":
    verify_models()