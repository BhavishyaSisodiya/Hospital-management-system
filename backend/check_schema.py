import sys
sys.path.insert(0, ".")
import models
from database import Base, engine
from sqlalchemy import inspect

insp = inspect(engine)
with engine.connect() as conn:
    missing_all = []
    for table in Base.metadata.sorted_tables:
        db_cols = {c["name"] for c in insp.get_columns(table.name)}
        model_cols = {c.name for c in table.columns}
        missing = model_cols - db_cols
        extra = db_cols - model_cols
        if missing or extra:
            missing_all.append((table.name, sorted(missing), sorted(extra)))
    if not missing_all:
        print("ALL TABLES IN SYNC")
    for t, m, e in missing_all:
        print(f"\nTABLE {t}:")
        if m: print(f"  missing from DB: {m}")
        if e: print(f"  extra in DB (not in model): {e}")