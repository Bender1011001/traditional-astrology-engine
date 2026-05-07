from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ChartRequest(BaseModel):
    date: str = Field(..., max_length=20)
    time: str = Field(..., max_length=20)
    city: str = Field(..., max_length=150)
    state: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=150)
    age: Optional[int] = Field(None, ge=0, le=150)
    analysis_date: Optional[str] = Field(None, max_length=20)
    house_system: Optional[str] = Field(None, max_length=20)
    compare_house_systems: Optional[bool] = False
    zodiac_system: Optional[str] = Field(None, max_length=50)
    ayanamsa: Optional[str] = Field(None, max_length=50)
    node_type: Literal["mean", "true"] = "mean"
    rectification_methods: Optional[List[str]] = Field(None, max_items=20)
    time_range_start: Optional[str] = Field(None, max_length=20)
    time_range_end: Optional[str] = Field(None, max_length=20)
    time_range_samples: Optional[int] = Field(None, ge=1, le=100)
    access_token: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    time_unknown: Optional[bool] = False


class CheckoutRequest(BaseModel):
    tier: str = Field(..., max_length=50)
    chart_request: Optional[ChartRequest] = None
    annual: Optional[bool] = False  # New field
    success_url: str
    cancel_url: str


class SynastryRequest(BaseModel):
    person_a: ChartRequest
    person_b: ChartRequest


class KairosRequest(BaseModel):
    activity: str = Field(..., max_length=100)
    city: str = Field(..., max_length=150)
    state: str = Field("", max_length=100)
    start_date: Optional[str] = Field(None, max_length=20)  # YYYY-MM-DD
    hours: int = Field(168, ge=1, le=720)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class HoraryRequest(BaseModel):
    question: str = Field(..., max_length=500)
    city: str = Field(..., max_length=150)
    state: str = Field("", max_length=100)
    date: Optional[str] = Field(None, max_length=20)
    time: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class WorldRequest(BaseModel):
    date: Optional[str] = Field(None, max_length=20)
    time: Optional[str] = Field(None, max_length=20)


class OracleChatRequest(BaseModel):
    query: str = Field(..., max_length=2000)
    context: str = Field(..., max_length=15000)


class TelemetryEvent(BaseModel):
    event_type: str = Field(..., max_length=100)
    element_id: Optional[str] = Field(None, max_length=100)
    url: str = Field(..., max_length=500)
    data: Optional[dict] = None


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    name: Optional[str] = Field("", max_length=150)
    plan_tier: Optional[str] = Field(None, max_length=50)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=255)


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., max_length=255)
    new_password: str = Field(..., max_length=255)


class OwnerSubscriptionUpdateRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    plan_tier: str = Field(..., max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    cancel_at_period_end: Optional[bool] = None
    confirm_downgrade: Optional[bool] = False
    current_period_end: Optional[str] = Field(None, max_length=50)


class ReadingFeedback(BaseModel):
    reading_hash: str = Field(..., max_length=100)
    vote: Literal["good", "bad", "up", "down"]
    source: Optional[str] = Field("basic_reading", max_length=50)
    chart_event_id: Optional[str] = Field(None, max_length=100)
    birth: Optional[dict] = None
    meta: Optional[dict] = None
    time_unknown: Optional[bool] = False
    session_id: Optional[str] = Field(None, max_length=150)
    comment: Optional[str] = Field(None, max_length=1000)
    ts: Optional[str] = Field(None, max_length=50)


class LeadCapture(BaseModel):
    email: str = Field(..., max_length=255)
    segment: Optional[str] = Field(None, max_length=100)
    platform: Optional[str] = Field(None, max_length=100)
    volume: Optional[str] = Field(None, max_length=100)
    pain: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=500)
    ua: Optional[str] = Field(None, max_length=1000)
