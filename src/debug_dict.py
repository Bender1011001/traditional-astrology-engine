import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.chart_calculator import calculate_chart_data
from engine.models import Chart, Planet, PlanetName, Sign
from engine.logic import perform_forensic_audit
from engine.reference_data import EGYPTIAN_TERMS

from engine.reference_data import EGYPTIAN_TERMS, PTOLEMAIC_TERMS

def debug_dico():
    print("Checking PTOLEMAIC_TERMS keys:")
    print(list(PTOLEMAIC_TERMS.keys()))
    print(f"Is Sign.VIRGO in keys? {Sign.VIRGO in PTOLEMAIC_TERMS}")
    
debug_dico()
# ... (rest of the file later, but let's just check this first)
