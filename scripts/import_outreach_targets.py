import os
import sys
from datetime import date


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.database.core import SessionLocal, engine  # noqa: E402
from src.database.models import Base, OutreachTarget  # noqa: E402


CSV_PATH = os.path.join(ROOT, "docs", "outreach", "outreach_targets.csv")


def main():
    reset = "--reset" in sys.argv
    if not os.path.exists(CSV_PATH):
        raise SystemExit(f"Missing CSV: {CSV_PATH}. Run scripts/extract_outreach_targets.py first.")

    # Ensure new table exists.
    Base.metadata.create_all(bind=engine)

    import csv

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    db = SessionLocal()
    try:
        if reset:
            db.query(OutreachTarget).delete()
            db.commit()

        upserted = 0
        for r in rows:
            name = (r.get("name") or "").strip()
            if not name:
                continue

            existing = db.query(OutreachTarget).filter(OutreachTarget.name == name).first()
            if not existing:
                existing = OutreachTarget(name=name)
                db.add(existing)

            existing.segment = (r.get("segment") or "").strip() or None
            existing.platform_primary = (r.get("platform_primary") or "").strip() or None
            existing.primary_contact = (r.get("primary_contact") or "").strip() or None
            existing.secondary_contact = (r.get("secondary_contact") or "").strip() or None
            existing.notes = (r.get("notes") or "").strip() or None
            existing.source = (r.get("source") or "").strip() or None
            existing.last_verified = (r.get("last_verified") or date.today().isoformat()).strip()
            upserted += 1

        db.commit()
        print(f"Upserted {upserted} outreach targets.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
