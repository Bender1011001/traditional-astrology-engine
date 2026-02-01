from fastapi.concurrency import run_in_threadpool
from src.engine.chart_calculator import calculate_chart_data
from src.engine.logic import perform_forensic_audit
from src.engine.forensic_forecast import calculate_5_day_forecast
from src.engine.synastry import SynastryEngine
# Add other imports as needed

async def calculate_chart_async(*args, **kwargs):
    """
    Non-blocking wrapper for the CPU-bound chart calculation.
    """
    return await run_in_threadpool(calculate_chart_data, *args, **kwargs)

async def perform_forensic_audit_async(*args, **kwargs):
    return await run_in_threadpool(perform_forensic_audit, *args, **kwargs)

async def calculate_forecast_async(*args, **kwargs):
    return await run_in_threadpool(calculate_5_day_forecast, *args, **kwargs)

class SynastryEngineAsync:
    def __init__(self):
        self.engine = SynastryEngine()
        
    async def analyze_structural_fit(self, *args, **kwargs):
        return await run_in_threadpool(self.engine.analyze_structural_fit, *args, **kwargs)
