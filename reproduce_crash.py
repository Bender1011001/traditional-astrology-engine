
import sys
import os

sys.path.insert(0, os.path.abspath("src"))

from engine.chart_calculator import calculate_chart_data
import traceback

try:
    print("Running calculation test...")
    result = calculate_chart_data("2023-10-27", "12:00", "New York", "NY")
    print("Result:", result)
except Exception:
    traceback.print_exc()
