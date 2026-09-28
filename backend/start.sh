#!/bin/sh
set -e

echo "=== Running DB schema setup ==="
python setup_schema.py

echo "=== Checking if DB needs seeding ==="
HAS_USERS=$(python -c "
from database import SessionLocal
from models.users import UserDB
db = SessionLocal()
try:
    count = db.query(UserDB).count()
    print('1' if count else '0')
finally:
    db.close()
")

if [ "$HAS_USERS" = "1" ]; then
    echo "Users found - skipping seed"
else
    echo "Empty DB - seeding demo data"
    python seed_all.py
fi

echo "=== Ensuring staff login users exist ==="
python ensure_staff_users.py

echo "=== Starting app on port ${PORT:-8000} ==="
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"