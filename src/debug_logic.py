import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Importing logic...")
    from engine.logic import perform_forensic_audit
    print("Logic imported.")
except Exception as e:
    import traceback
    traceback.print_exc()
