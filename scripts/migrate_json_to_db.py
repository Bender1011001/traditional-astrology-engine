import json
import os
import sys
from typing import Dict, Any

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.core import SessionLocal, engine, Base
from src.database.models import AstrologicalDelineation

# Ensure tables are created
Base.metadata.create_all(bind=engine)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'data')

def migrate():
    db = SessionLocal()
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
        print(f"Found {len(files)} JSON files in {DATA_DIR}")

        total_records = 0
        for filename in files:
            category = filename.replace('.json', '')
            path = os.path.join(DATA_DIR, filename)
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Processing {filename} ({category})...")
            
            # Key-value pairs (flat)
            if isinstance(data, dict):
                for key, content in data.items():
                    # Check if already exists to avoid duplicates (idempotent)
                    existing = db.query(AstrologicalDelineation).filter(
                        AstrologicalDelineation.category == category,
                        AstrologicalDelineation.key == key
                    ).first()
                    
                    if existing:
                        # Update content if manual override is not set
                        if not existing.is_manual_override:
                            existing.content = content
                    else:
                        new_record = AstrologicalDelineation(
                            category=category,
                            key=key,
                            content=content
                        )
                        db.add(new_record)
                        total_records += 1
            
            # Commit per file to avoid huge transactions
            db.commit()
            
        print(f"Migration completed. Added {total_records} new records.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
