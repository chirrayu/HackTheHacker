"""Reset the database for a clean live capture session."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database.connection import engine, Base, init_db

print("Resetting HACK THE HACKER database...")
Base.metadata.drop_all(bind=engine)
print("All tables dropped.")
init_db()
print("Database re-initialized with clean tables.")
print("Ready for live capture!")
