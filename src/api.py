import sys
import os
import json

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # Fail silently; environment variables may be set elsewhere.
        pass

_load_dotenv()

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
from engine.chat_oracle import get_chat_response, explain_reading_in_plain_terms
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import swisseph as swe
import uvicorn
import os
import stripe
import jwt
import hashlib
from datetime import timedelta


from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse
from engine.pdf_generator import PDFReportGenerator

MEDICAL_DISCLAIMER = (
    "FOR HISTORICAL AND EDUCATIONAL RESEARCH PURPOSES ONLY. NOT MEDICAL ADVICE. "
    "DO NOT USE FOR HEALTH DECISIONS OR SURGERY SCHEDULING."
)

app = FastAPI(
    title="Traditional Astrology Engine",
    description="A high-precision engine for pre-1700s Traditional Astrology, including Natal, Horary, Electional, and Medical (Iatromathematics) analysis.",
    version="1.1.0",
    terms_of_service="/LICENSE",
    contact={
        "name": "Project Maintainer",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# --- PAYMENT CONFIGURATION ---
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
JWT_SECRET = os.getenv('JWT_SECRET', 'development-secret-key-change-me')

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

def create_access_token(chart_hash: str, tier: str, expires_days: int = 30) -> str:
    payload = {
        'chart_hash': chart_hash,
        'tier': tier,
        'exp': datetime.utcnow() + timedelta(days=expires_days)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def validate_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))

def _load_glossary() -> dict:
    path = os.path.join(os.path.dirname(__file__), "database", "data", "glossary.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}

def _append_jsonl(filename: str, record: dict) -> None:
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        path = os.path.join(LOG_DIR, filename)
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
    except Exception:
        # Logging must never break the API.
        pass

def _build_plain_reading_context(report: dict, advanced_prediction: Optional[dict]) -> str:
    if not report:
        return ""

    summary = report.get("summary", {}) if isinstance(report, dict) else {}
    planets = []
    for p in report.get("planets", []) if isinstance(report, dict) else []:
        impacts = []
        for impact in (p.get("impacts") or [])[:3]:
            cause = impact.get("cause")
            effect = impact.get("effect")
            if cause or effect:
                impacts.append(f"{cause}: {effect}".strip(": "))

        planets.append({
            "planet": p.get("planet"),
            "sign": p.get("sign"),
            "house": p.get("house_number"),
            "power": p.get("power_label"),
            "sect_status": p.get("sect_status"),
            "delineation": p.get("delineation_text"),
            "house_delineation": p.get("house_delineation_text"),
            "impacts": impacts
        })

    context = {
        "summary": {
            "sect": summary.get("sect"),
            "temperament": summary.get("temperament"),
            "lunar_phase": summary.get("lunar_phase"),
            "lunar_phase_profile": summary.get("lunar_phase_profile"),
            "dominant_elements": summary.get("dominant_elements"),
            "team_note": summary.get("team_note"),
            "constructive_team": summary.get("constructive_team"),
            "destructive_team": summary.get("destructive_team")
        },
        "soul_guardian": report.get("soul_guardian") if isinstance(report, dict) else None,
        "daily_oracle": report.get("daily_oracle") if isinstance(report, dict) else None,
        "vitality": report.get("vitality") if isinstance(report, dict) else None,
        "planets": planets,
        "lots": report.get("lots") if isinstance(report, dict) else None,
        "prediction": report.get("prediction") if isinstance(report, dict) else None,
        "advanced_prediction": advanced_prediction
    }

    return json.dumps(context, ensure_ascii=True, indent=2)

def _client_meta(http_request: Request) -> dict:
    client_host = http_request.client.host if http_request.client else None
    return {
        "ip": client_host,
        "user_agent": http_request.headers.get("user-agent"),
        "referer": http_request.headers.get("referer")
    }

def _log_event(event_type: str, payload: dict, http_request: Request, session_id: str | None = None, ts: str | None = None) -> None:
    record = {
        "ts": ts or datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "session_id": session_id,
        "payload": payload,
        "client": _client_meta(http_request)
    }
    _append_jsonl("events.jsonl", record)

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
        jd=res.get("meta", {}).get("julian_day"),
        houses=res.get("houses"),
        house_system=(res.get("meta", {}).get("house_system") or {}).get("code")
    )

class ChartRequest(BaseModel):
    date: str
    time: str
    city: str
    state: str = ""
    age: Optional[int] = None
    analysis_date: Optional[str] = None
    house_system: Optional[str] = None
    compare_house_systems: Optional[bool] = False
    zodiac_system: Optional[str] = None
    ayanamsa: Optional[str] = None
    rectification_methods: Optional[list[str]] = None
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None
    time_range_samples: Optional[int] = None
    access_token: Optional[str] = None

class CheckoutRequest(BaseModel):
    tier: str  # 'onetime' or 'subscription'
    chart_request: ChartRequest
    success_url: str
    cancel_url: str

def generate_chart_hash(req: ChartRequest) -> str:
    # Normalize inputs for hashing
    date = req.date.strip()
    time = req.time.strip()
    city = req.city.strip().lower()
    state = (req.state or "").strip().lower()
    raw = f"{date}_{time}_{city}_{state}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@app.post("/api/calculate")
async def calculate_chart(chart_request: ChartRequest, http_request: Request):
    """
    Calculates a full natal chart including forensic audit, 5-day forecast, and plain-language synthesis.
    """
    _log_event("chart_request_server", {"form": chart_request.dict()}, http_request)
    result = calculate_chart_data(
        chart_request.date,
        chart_request.time,
        chart_request.city,
        chart_request.state,
        chart_request.house_system,
        bool(chart_request.compare_house_systems),
        chart_request.zodiac_system,
        chart_request.ayanamsa,
        chart_request.time_range_start,
        chart_request.time_range_end,
        chart_request.time_range_samples
    )
    if "error" in result:
        _log_event("chart_error_server", {"error": result["error"]}, http_request)
        raise HTTPException(status_code=400, detail=result["error"])
    
    # --- AUTH / TIER CHECK ---
    chart_hash = generate_chart_hash(chart_request)
    tier = "free"
    
    if chart_request.access_token:
        payload = validate_token(chart_request.access_token)
        if payload and payload.get("chart_hash") == chart_hash:
            # If subscription, check if valid (simplified here)
            # If one-time, it's valid if token is valid
            tier = "paid"
            
    # Add tier metadata to result
    result["meta"]["tier"] = tier
    result["meta"]["chart_hash"] = chart_hash
        
    # INTEGRATION: Run Forensic Audit using ingested data

    try:
        chart_model = result_to_model(result)

        # Prediction Params
        age = chart_request.age
        
        # Default analysis date to today if not provided
        if chart_request.analysis_date:
            try:
                ad = datetime.strptime(chart_request.analysis_date, "%Y-%m-%d")
            except:
                ad = datetime.now()
        else:
            ad = datetime.now()

        # Birth date for downstream timelines
        bd = None
        try:
            bd = datetime.strptime(chart_request.date, "%Y-%m-%d")
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

        # Plain-language reading (internal LLM)
        try:
            # If free tier, we might want to truncate the context here or handle it in explain_reading_in_plain_terms
            # For now, we will pass the tier to the context builder if we modify it, 
            # or relying on the logic engine to output less.
            # But the plan says: "Generate sections 1 + partial section 2"
            
            # Note: ACTUAL filtering of content sent to LLM should happen here or inside _build_plain_reading_context
            # For now, we build the full context but mark the result with the tier so frontend can hide it?
            # No, backend must secure it to prevent API cost bleeding.
            
            # Simple implementation for now:
            # The current _build_plain_reading_context builds a large JSON.
            # We can't easily filter "Section 1" without deeply knowing the content structure.
            # We will rely on post-processing in this step for MVP or trusting the frontend for display 
            # (which doesn't solve API cost, but solves UX).
            # To strictly solve API cost as per plan, we need to limit the LLM generation.
            
            plain_context = _build_plain_reading_context(audit_report, result.get("advanced_prediction"))
            
            # If free, append a system note to the context for the LLM?
            # Or truncate the generated reading.
            
            plain_reading = explain_reading_in_plain_terms(plain_context)
            if plain_reading:
                result["plain_reading"] = plain_reading
        except Exception as pe:

            print(f"Plain Reading Error: {pe}")
            
    except Exception as e:
        print(f"Audit Error: {e}")
        # Don't fail the whole request, just omit report or add error
        result["forensic_error"] = str(e)

    _log_event("chart_result_server", {"result": result}, http_request)
    return result

@app.get("/api/surgery_check")
async def surgery_check(body_part: str, jd: float):
    """
    Performs a traditional 'Surgery Rule' check for a specific body part and date.
    NOTE: For historical research only. NOT medical advice.
    """
    # This is a simplified check for current transits
    # In a real app, you'd pass the natal chart too
    # For now, we use a dummy natal chart or just focus on transits
    dummy_chart = Chart(sun_altitude=1, planets=[], ascendant=0, mc=0)
    res = MedicalAstrology.can_perform_surgery(body_part, jd, dummy_chart)
    res["medical_disclaimer"] = MEDICAL_DISCLAIMER
    return res

class SynastryRequest(BaseModel):
    person_a: ChartRequest
    person_b: ChartRequest

@app.post("/api/synastry")
async def calculate_synastry(request: SynastryRequest):
    """
    Analyzes the 'Structural Fit' between two people using Traditional Synastry rules.
    """
    # Calculate both charts
    res_a = calculate_chart_data(
        request.person_a.date,
        request.person_a.time,
        request.person_a.city,
        request.person_a.state,
        request.person_a.house_system,
        bool(request.person_a.compare_house_systems),
        request.person_a.zodiac_system,
        request.person_a.ayanamsa
    )
    res_b = calculate_chart_data(
        request.person_b.date,
        request.person_b.time,
        request.person_b.city,
        request.person_b.state,
        request.person_b.house_system,
        bool(request.person_b.compare_house_systems),
        request.person_b.zodiac_system,
        request.person_b.ayanamsa
    )
    
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
    """
    Finds the 'Golden Window' (Electional Astrology) for a specific activity within a time range.
    """
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
    """
    Casts a Horary chart and provides an 'Oracle' interpretation for a specific question.
    """
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
    """
    Renders the 'Universal Overdrive' dashboard for global astrological events.
    """
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

class LogEventRequest(BaseModel):
    session_id: Optional[str] = None
    event_type: str
    payload: dict = {}
    ts: Optional[str] = None

class ReadingFeedbackRequest(BaseModel):
    reading_hash: str
    vote: str
    source: Optional[str] = None
    meta: Optional[dict] = None
    birth: Optional[dict] = None
    time_unknown: Optional[bool] = None
    session_id: Optional[str] = None
    ts: Optional[str] = None

def _load_feedback_counts() -> dict:
    path = os.path.join(LOG_DIR, "reading_feedback.json")
    if not os.path.exists(path):
        return {"by_hash": {}, "total": {"up": 0, "down": 0, "total": 0}}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {"by_hash": {}, "total": {"up": 0, "down": 0, "total": 0}}

def _save_feedback_counts(data: dict) -> None:
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        path = os.path.join(LOG_DIR, "reading_feedback.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=True, indent=2)
    except Exception:
        pass

@app.post("/api/log_event")
async def log_event(event: LogEventRequest, http_request: Request):
    _log_event(event.event_type, event.payload or {}, http_request, session_id=event.session_id, ts=event.ts)
    return {"status": "ok"}

@app.post("/api/reading_feedback")
async def reading_feedback(feedback: ReadingFeedbackRequest, http_request: Request):
    vote = (feedback.vote or "").strip().lower()
    if vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="Invalid vote.")

    counts = _load_feedback_counts()
    by_hash = counts.setdefault("by_hash", {})
    entry = by_hash.setdefault(feedback.reading_hash, {"up": 0, "down": 0, "total": 0})
    entry[vote] = int(entry.get(vote, 0)) + 1
    entry["total"] = int(entry.get("up", 0)) + int(entry.get("down", 0))
    entry["updated_at"] = datetime.utcnow().isoformat() + "Z"

    totals = counts.setdefault("total", {"up": 0, "down": 0, "total": 0})
    totals[vote] = int(totals.get(vote, 0)) + 1
    totals["total"] = int(totals.get("up", 0)) + int(totals.get("down", 0))

    _save_feedback_counts(counts)
    _log_event("reading_feedback_server", {
        "reading_hash": feedback.reading_hash,
        "vote": vote,
        "source": feedback.source,
        "meta": feedback.meta,
        "birth": feedback.birth,
        "time_unknown": feedback.time_unknown
    }, http_request, session_id=feedback.session_id, ts=feedback.ts)

    return {
        "reading_hash": feedback.reading_hash,
        "counts": entry,
        "all_time": totals
    }

@app.post("/api/ask_oracle")
async def ask_oracle(oracle_request: OracleChatRequest, http_request: Request):
    """
    Chat with the AI Oracle about a specific chart result.
    """
    _log_event("oracle_query_server", {"query": oracle_request.query}, http_request)
    answer = get_chat_response(oracle_request.query, oracle_request.context)
    _log_event("oracle_response_server", {"answer": answer}, http_request)
    return {"answer": answer}

@app.post("/api/rectification")
async def rectification(request: ChartRequest):
    """
    Runs primary rectification protocols (Animodar, Trutina Hermetis) to refine birth time.
    """
    res = calculate_chart_data(
        request.date,
        request.time,
        request.city,
        request.state,
        request.house_system,
        bool(request.compare_house_systems),
        request.zodiac_system,
        request.ayanamsa
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    chart_model = result_to_model(res)
    jd = res["meta"]["julian_day"]
    lat = res["meta"]["lat"]
    lon = res["meta"]["lon"]

    requested_methods = request.rectification_methods or ["animodar", "trutina_hermetis"]
    normalized = [m.strip().lower() for m in requested_methods if isinstance(m, str) and m.strip()]
    supported = {"animodar", "trutina_hermetis"}
    computed_methods = [m for m in normalized if m in supported]
    unsupported = [m for m in normalized if m not in supported]

    syzygy = RectificationEngine.find_prenatal_syzygy(jd) if computed_methods else {}
    animodar = RectificationEngine.animodar_rectification(chart_model, jd, lat, lon) if "animodar" in computed_methods else []
    trutina = RectificationEngine.trutina_hermetis(jd, lat, lon) if "trutina_hermetis" in computed_methods else []

    return {
        "meta": res.get("meta", {}),
        "rectification_meta": {
            "requested_methods": normalized,
            "computed_methods": computed_methods,
            "unsupported_methods": unsupported
        },
        "syzygy": syzygy,
        "animodar": animodar,
        "trutina_hermetis": trutina
    }

@app.get("/api/glossary")
async def get_glossary():
    """
    Returns a glossary of traditional astrological terms and their definitions.
    """
    return _load_glossary()

@app.post("/api/export")
async def export_chart_data(request: dict):
    """
    Exports chart result as a CSV-friendly structure or simple text dump.
    """
    # Simply returns a flattened version of the forensic report for researchers
    report = request.get("forensic_report", {})
    planets = report.get("planets", [])
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["Planet", "Sign", "Longitude", "House", "Power", "Sect Status", "Solar Status", "Delineation"])
    
    for p in planets:
        writer.writerow([
            p.get("planet"),
            p.get("sign"),
            p.get("longitude"),
            p.get("house_number"),
            p.get("power_label"),
            p.get("sect_status"),
            p.get("solar_status"),
            p.get("delineation_text", "").replace("\n", " ")
        ])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=astrology_export.csv"}
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=codex_caelestis_report.pdf"}
    )

@app.post("/api/create-checkout")
async def create_checkout(checkout_request: CheckoutRequest):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured.")

    chart_hash = generate_chart_hash(checkout_request.chart_request)
    
    try:
        if checkout_request.tier == 'onetime':
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Full Natal Chart Reading (Forensic Audit)'},
                        'unit_amount': 999,  # $9.99
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=checkout_request.success_url + f'?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=checkout_request.cancel_url,
                metadata={'chart_hash': chart_hash, 'tier': 'onetime'}
            )
        elif checkout_request.tier == 'subscription':
            # Note: Requires a price ID from Stripe Dashboard
            # fallback to error if not set, or use a hardcoded price ID if known
            price_id = os.getenv("STRIPE_SUBSCRIPTION_PRICE_ID")
            if not price_id:
                 raise HTTPException(status_code=500, detail="Subscription price ID not configured.")
                 
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=checkout_request.success_url + f'?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=checkout_request.cancel_url,
                metadata={'chart_hash': chart_hash, 'tier': 'subscription'}
            )
        else:
             raise HTTPException(status_code=400, detail="Invalid tier.")
             
        return {'checkout_url': session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/stripe-webhook")
async def stripe_webhook(request: Request):
    if not STRIPE_WEBHOOK_SECRET:
         raise HTTPException(status_code=500, detail="Stripe webhook secret not configured.")
         
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        chart_hash = metadata.get('chart_hash')
        tier = metadata.get('tier', 'onetime')
        
        if chart_hash:
            # Generate token
            # For one-time: 30 days. For sub: maybe longer or check sub status. 
            # Simplification: give 30 days for now, sub renewal handles separately (or logic upgrades later)
            token = create_access_token(chart_hash, 'paid', expires_days=30)
            
            # TODO: Store token or email mapping if needed. 
            # Ideally send email here.
            pass
            
            # If we wanted to return it here we can't (it's a webhook).
            # The client needs to verify or get it via email or redirect handling.
            # In the Plan: "Redirect to success page -> Regenerate with full access"
            # It seems the CLIENT logic on success page waits for this? 
            # Or the success page calls an endpoint to 'claim' the purchase?
            # Actually, standard flow: Success page gets session_id, calls backend to "verify_session".
            
    return {'status': 'success'}

@app.get("/api/verify-checkout-session")
async def verify_checkout_session(session_id: str):
    """
    Called by the frontend success page to exchange a session_id for a token.
    """
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe not configured.")
        
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
             metadata = session.get('metadata', {})
             chart_hash = metadata.get('chart_hash')
             tier = metadata.get('tier', 'onetime')
             
             if chart_hash:
                 token = create_access_token(chart_hash, 'paid', expires_days=30)
                 return {"access_token": token, "chart_hash": chart_hash}
                 
        raise HTTPException(status_code=400, detail="Payment not completed.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
