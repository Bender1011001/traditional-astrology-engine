from src.database.core import SessionLocal
from src.database.models import SubscriptionPlan

def seed_plans():
    db = SessionLocal()
    try:
        # 1. Calibration Audit ($27)
        calibration = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == "CALIBRATION").first()
        if not calibration:
            calibration = SubscriptionPlan(
                tier="CALIBRATION",
                price_monthly=27.0,
                stripe_price_id_monthly="price_1SxwoSC8BJritqvrkPJpwmbD",
                chart_quota=1, 
                api_quota=0,
                features={
                    "name": "Calibration Audit",
                    "description": "Proof of Accuracy (Past/Personality) condensed report. Deliverable: PDF Report Only. Key Feature: Past & Personality Validation."
                }
            )
            db.add(calibration)
        else:
            calibration.stripe_price_id_monthly = "price_1SxwoSC8BJritqvrkPJpwmbD"
            calibration.price_monthly = 27.0
            calibration.features = {
                "name": "Calibration Audit",
                "description": "Proof of Accuracy (Past/Personality) condensed report. Deliverable: PDF Report Only. Key Feature: Past & Personality Validation."
            }

        # 2. Full Forensic Audit ($197)
        full = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == "FULL").first()
        if not full:
            full = SubscriptionPlan(
                tier="FULL",
                price_monthly=197.0,
                stripe_price_id_monthly="price_1SxwoSC8BJritqvrlaH1xd0A",
                chart_quota=1,
                api_quota=1, 
                features={
                    "name": "Full Forensic Audit + AI Source Code",
                    "description": "Complete Forensic Analysis + AI Agent Data. Deliverable: Digital Soul Packet (PDF + JSON + MD). Key Feature: Includes Raw Data for AI Agents."
                }
            )
            db.add(full)
        else:
            full.stripe_price_id_monthly = "price_1SxwoSC8BJritqvrlaH1xd0A"
            full.price_monthly = 197.0
            full.features = {
                "name": "Full Forensic Audit + AI Source Code",
                "description": "Complete Forensic Analysis + AI Agent Data. Deliverable: Digital Soul Packet (PDF + JSON + MD). Key Feature: Includes Raw Data for AI Agents."
            }

        db.commit()
        print("Plans seeded/updated successfully.")
    except Exception as e:
        print(f"Error seeding plans: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_plans()
