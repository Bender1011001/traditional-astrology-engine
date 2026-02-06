import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import engine.chart_calculator as cc
    print(f"Module found: {cc}")
    print(f"Attributes: {dir(cc)}")
    from engine.chart_calculator import calculate_chart_data
    print("Function imported successfully.")
except Exception as e:
    print(f"Error: {e}")
