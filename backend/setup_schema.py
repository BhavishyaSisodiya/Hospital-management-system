import sys
from sqlalchemy import inspect

import models
from database import Base, engine

inspector = inspect(engine)
tables = inspector.get_table_names()

needs_rebuild = "users" not in tables

if "users" in tables:
    cols = [c["name"] for c in inspector.get_columns("users")]
    if "account_type" not in cols:
        needs_rebuild = True

if needs_rebuild:
    print("=== Rebuilding schema (Base.metadata) ===")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Schema ready.")
else:
    print("Schema already present and up-to-date.")

sys.exit(0)