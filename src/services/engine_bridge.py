from fastapi.concurrency import run_in_threadpool
from src.engine.calculator.main import calculate_chart_data
from src.engine.forensic_forecast import calculate_5_day_forecast
from src.engine.synastry import SynastryEngine
from src.engine.forensic_engine import Auditor

async def calculate_chart_async(*args, **kwargs):
    """
    Non-blocking wrapper for the CPU-bound chart calculation.
    """
    return await run_in_threadpool(calculate_chart_data, *args, **kwargs)



async def calculate_forecast_async(*args, **kwargs):
    return await run_in_threadpool(calculate_5_day_forecast, *args, **kwargs)

async def generate_full_nativity_async(*args, **kwargs):
    return await run_in_threadpool(Auditor.generate_full_nativity, *args, **kwargs)

class SynastryEngineAsync:
    def __init__(self):
        self.engine = SynastryEngine()
        
    async def analyze_structural_fit(self, *args, **kwargs):
        return await run_in_threadpool(self.engine.analyze_structural_fit, *args, **kwargs)
