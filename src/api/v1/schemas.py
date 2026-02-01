from pydantic import BaseModel
from typing import Optional, List

class ChartRequest(BaseModel):
    date: str
    time: str
    city: str
    state: Optional[str] = None
    age: Optional[int] = None
    analysis_date: Optional[str] = None
    house_system: Optional[str] = None
    compare_house_systems: Optional[bool] = False
    zodiac_system: Optional[str] = None
    ayanamsa: Optional[str] = None
    rectification_methods: Optional[List[str]] = None
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None
    time_range_samples: Optional[int] = None
    access_token: Optional[str] = None

class CheckoutRequest(BaseModel):
    tier: str  # 'onetime' or 'subscription'
    chart_request: Optional[ChartRequest] = None # Make optional to fix subscription flow
    annual: Optional[bool] = False # New field
    success_url: str
    cancel_url: str

class SynastryRequest(BaseModel):
    person_a: ChartRequest
    person_b: ChartRequest

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

class OracleChatRequest(BaseModel):
    query: str
    context: str

class TelemetryEvent(BaseModel):
    event_type: str
    element_id: Optional[str] = None
    url: str
    data: Optional[dict] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = ""
