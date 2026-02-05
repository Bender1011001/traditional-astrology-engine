import os
import sys
import json
from datetime import datetime

# Adjust path
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from src.engine.forensic_engine import Auditor
from src.engine.chat_oracle import explain_reading_in_plain_terms

def run_full_reading():
    print("=" * 60)
    print("  FULL READING: November 1, 1984 8:32 PM Cortez, CO")
    print("=" * 60)
    print()

    # Generate audit
    result = Auditor.generate_full_nativity(
        date_str="1984-11-01",
        time_str="20:32",
        city="Cortez",
        state="CO"
    )

    if "error" in result:
        print(f"Audit Error: {result['error']}")
        return

    print("Audit complete. Preparing LLM synthesis...")
    print()
    
    # Prepare context - truncate to fit token limits
    context_json = json.dumps(result, indent=2, default=str)[:20000]
    
    prompt = f"""You are a forensic astrologer generating a practitioner-grade dossier.

NATAL DATA:
- Date: November 1, 1984
- Time: 8:32 PM (20:32)
- Location: Cortez, Colorado, USA

FORENSIC AUDIT DATA:
{context_json[:60000]}

Generate a comprehensive 5000+ word forensic astrological dossier covering:
1. Universal Context (Eclipses, Mundane Cycles)
2. Soul Architecture (Almuten Figuris, Lots of Spirit/Fortune)
3. Temperament & Vitality (Sect, Solar/Lunar conditions)
4. Career & Praxis (10th House, MC Ruler)
5. Relationships (7th House, Venus/Mars)
6. Psychological Depths (Water Houses)
7. Temporal Forecast (Decennials, next 5 years)

Use authoritative Hellenistic and Medieval techniques. No fluff. Write like William Lilly.
"""
    
    print("Calling LLM (Multi-Turn Interrogation)...")
    synthesis = explain_reading_in_plain_terms(prompt, tier="paid")
    
    print()
    print("=" * 60)
    print("FINAL SYNTHESIZED REPORT")
    print("=" * 60)
    print()
    print(synthesis)

if __name__ == "__main__":
    run_full_reading()
