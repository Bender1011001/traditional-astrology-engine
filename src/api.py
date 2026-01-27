import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from engine.chart_calculator import calculate_chart_data
from engine.logic import perform_forensic_audit
from engine.forensic_forecast import calculate_5_day_forecast
from engine.models import Chart, Planet, PlanetName
from engine.medical import MedicalAstrology
from engine.synastry import SynastryEngine
from engine.electional import ElectionalEngine
from engine.horary import build_horary_oracle
from engine.mundane import build_world_dashboard
from engine.prediction import AdvancedPredictionEngine
from engine.rectification import RectificationEngine
from engine.chart_calculator import get_local_datetime_now
from engine.chat_oracle import get_chat_response
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import swisseph as swe
import uvicorn
import os

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

app = FastAPI()

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self' https://photon.komoot.io;"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://traditional-astrology.com", "http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def result_to_model(res):
    model_planets = []
    sun_alt = 0.0
    for name, data in res.get("planets", {}).items():
        try:
            p_enum = PlanetName(name)
        except ValueError:
            continue
        model_planets.append(
            Planet(
                name=p_enum,
                longitude=data["longitude"],
                latitude=data.get("latitude", 0.0),
                speed=data.get("speed", 0.0),
                altitude=data.get("altitude", 0.0)
            )
        )
        if name == "Sun":
            sun_alt = data.get("altitude", 0.0)

    angles = res.get("angles", {})
    return Chart(
        sun_altitude=sun_alt,
        planets=model_planets,
        ascendant=angles.get("Ascendant", 0.0),
        mc=angles.get("MC", 0.0),
        north_node=res.get("planets", {}).get("North_Node", {}).get("longitude", 0.0),
        south_node=res.get("planets", {}).get("South_Node", {}).get("longitude", 0.0),
        geo_lat=res.get("meta", {}).get("lat"),
        geo_lon=res.get("meta", {}).get("lon"),
        jd=res.get("meta", {}).get("julian_day")
    )

class ChartRequest(BaseModel):
    date: str
    time: str
    city: str
    state: str = ""
    age: Optional[int] = None
    analysis_date: Optional[str] = None

@app.post("/api/calculate")
async def calculate_chart(request: ChartRequest):
    result = calculate_chart_data(request.date, request.time, request.city, request.state)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    # INTEGRATION: Run Forensic Audit using ingested data
    try:
        chart_model = result_to_model(result)

        # Prediction Params
        age = request.age
        
        # Default analysis date to today if not provided
        if request.analysis_date:
            try:
                ad = datetime.strptime(request.analysis_date, "%Y-%m-%d")
            except:
                ad = datetime.now()
        else:
            ad = datetime.now()

        # Birth date for downstream timelines
        bd = None
        try:
            bd = datetime.strptime(request.date, "%Y-%m-%d")
        except:
            bd = None

        # If age not provided, calculate it from birth date
        if age is None:
            if bd:
                age = ad.year - bd.year - ((ad.month, ad.day) < (bd.month, bd.day))
            else:
                age = 0
                
        month = ad.month
        day = ad.day

        # Calculate analysis JD for medical checks
        try:
            # Pyswisseph julday needs year, month, day, hour (fractional)
            # ad might be from datetime.now() or strptime
            hr = ad.hour + ad.minute/60.0 + ad.second/3600.0
            analysis_jd = swe.julday(ad.year, ad.month, ad.day, hr)
        except Exception as e:
            print(f"JD Calculation Error: {e}")
            analysis_jd = result["meta"]["julian_day"]
            
        result["meta"]["analysis_jd"] = analysis_jd

        audit_report = perform_forensic_audit(chart_model, result["meta"]["julian_day"], age=age, month=month, day=day, birth_date=bd, analysis_date=ad, analysis_jd=analysis_jd)
        result["forensic_report"] = audit_report
        
        # 5-Day Forecast
        try:
            forecast_data = calculate_5_day_forecast(chart_model, result["meta"]["julian_day"], ad)
            result["forensic_forecast"] = forecast_data
        except Exception as fe:
            print(f"Forecast Error: {fe}")
            result["forensic_forecast_error"] = str(fe)

        # Advanced Prediction (Firdaria, Solar Return, Arcs, Muntha, Lunar Phase)
        try:
            birth_dt = None
            try:
                birth_dt = datetime.fromisoformat(result["meta"]["utc_time"])
            except Exception:
                birth_dt = bd
            if birth_dt and birth_dt.tzinfo is not None:
                birth_dt = birth_dt.replace(tzinfo=None)
            if birth_dt:
                predictor = AdvancedPredictionEngine(
                    chart_model,
                    birth_dt,
                    result["meta"]["julian_day"],
                    result["meta"]["lat"],
                    result["meta"]["lon"]
                )
                result["advanced_prediction"] = predictor.get_prediction_report(ad)
        except Exception as pe:
            print(f"Advanced Prediction Error: {pe}")
            result["advanced_prediction_error"] = str(pe)
            
    except Exception as e:
        print(f"Audit Error: {e}")
        # Don't fail the whole request, just omit report or add error
        result["forensic_error"] = str(e)

    return result

@app.get("/api/surgery_check")
async def surgery_check(body_part: str, jd: float):
    # This is a simplified check for current transits
    # In a real app, you'd pass the natal chart too
    # For now, we use a dummy natal chart or just focus on transits
    dummy_chart = Chart(sun_altitude=1, planets=[], ascendant=0, mc=0)
    res = MedicalAstrology.can_perform_surgery(body_part, jd, dummy_chart)
    return res

class SynastryRequest(BaseModel):
    person_a: ChartRequest
    person_b: ChartRequest

@app.post("/api/synastry")
async def calculate_synastry(request: SynastryRequest):
    # Calculate both charts
    res_a = calculate_chart_data(request.person_a.date, request.person_a.time, request.person_a.city, request.person_a.state)
    res_b = calculate_chart_data(request.person_b.date, request.person_b.time, request.person_b.city, request.person_b.state)
    
    if "error" in res_a:
        raise HTTPException(status_code=400, detail=f"Person A Error: {res_a['error']}")
    if "error" in res_b:
        raise HTTPException(status_code=400, detail=f"Person B Error: {res_b['error']}")
        
    chart_a = result_to_model(res_a)
    chart_b = result_to_model(res_b)
    
    engine = SynastryEngine()
    analysis = engine.analyze_structural_fit(chart_a, chart_b)
    
    return {
        "person_a": res_a,
        "person_b": res_b,
        "synastry": analysis
    }

class KairosRequest(BaseModel):
    activity: str
    city: str
    state: str = ""
    start_date: Optional[str] = None # YYYY-MM-DD
    hours: int = 168

class HoraryRequest(BaseModel):
    question: str
    city: str
    state: str = ""
    date: Optional[str] = None
    time: Optional[str] = None

class WorldRequest(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None

@app.post("/api/kairos")
async def find_kairos(request: KairosRequest):
    engine = ElectionalEngine()
    
    if request.start_date:
        try:
            start_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
        except:
            start_dt = datetime.now()
    else:
        start_dt = datetime.now()
        
    res = engine.find_kairos(
        start_dt=start_dt,
        city=request.city,
        state=request.state,
        hours_to_scan=request.hours,
        activity=request.activity
    )
    
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
        
    return res

@app.post("/api/horary")
async def horary_oracle(request: HoraryRequest):
    question = (request.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required for horary.")

    date_str = request.date
    time_str = request.time
    if not date_str or not time_str:
        try:
            local_dt = get_local_datetime_now(request.city, request.state)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Location error: {str(e)}")
        date_str = local_dt.strftime("%Y-%m-%d")
        time_str = local_dt.strftime("%H:%M")

    res = calculate_chart_data(date_str, time_str, request.city, request.state)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    chart_model = result_to_model(res)
    oracle = build_horary_oracle(question, chart_model)

    return {
        "meta": res.get("meta", {}),
        "oracle": oracle
    }

@app.post("/api/world")
async def world_dashboard(request: WorldRequest):
    dt = None
    if request.date or request.time:
        date_str = request.date or datetime.utcnow().strftime("%Y-%m-%d")
        time_str = request.time or "12:00"
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Date parsing error: {str(e)}")
    else:
        dt = datetime.utcnow()

    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
    dashboard = build_world_dashboard(jd)
    dashboard["timestamp"] = dt.isoformat() + "Z"
    dashboard["timestamp"] = dt.isoformat() + "Z"
    return dashboard

class OracleChatRequest(BaseModel):
    query: str
    context: str

@app.post("/api/ask_oracle")
async def ask_oracle(request: OracleChatRequest):
    answer = get_chat_response(request.query, request.context)
    return {"answer": answer}

@app.post("/api/rectification")
async def rectification(request: ChartRequest):
    res = calculate_chart_data(request.date, request.time, request.city, request.state)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    chart_model = result_to_model(res)
    jd = res["meta"]["julian_day"]
    lat = res["meta"]["lat"]
    lon = res["meta"]["lon"]

    syzygy = RectificationEngine.find_prenatal_syzygy(jd)
    animodar = RectificationEngine.animodar_rectification(chart_model, jd, lat, lon)
    trutina = RectificationEngine.trutina_hermetis(jd, lat, lon)

    return {
        "meta": res.get("meta", {}),
        "syzygy": syzygy,
        "animodar": animodar,
        "trutina_hermetis": trutina
    }

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
