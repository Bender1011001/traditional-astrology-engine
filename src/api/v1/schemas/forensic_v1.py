from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class ForensicMeta(BaseModel):
    subject_name: str
    timestamp: datetime
    julian_day: float
    city: str
    coords: Dict[str, float]
    age: int

class ForensicPlanet(BaseModel):
    name: str
    longitude: float
    sign: str
    dignities: Dict[str, Any]
    solar_status: str
    maltreatments: List[Dict[str, Any]]
    impacts: List[Dict[str, Any]]
    delineation: Optional[str] = None

class ForensicAnalysis(BaseModel):
    dignity: Dict[str, Any]
    fate: Dict[str, Any]
    medical: Dict[str, Any]
    teams: Dict[str, Any]
    aspects: List[Dict[str, Any]]

class AstronomyData(BaseModel):
    planets: Dict[str, Any]
    houses: List[float]
    angles: Dict[str, Optional[float]]

class TechnicalDataV1(BaseModel):
    meta: ForensicMeta
    astronomy: AstronomyData
    analysis: ForensicAnalysis
    planets_forensic: List[ForensicPlanet]

class HumanTranslationV1(BaseModel):
    report_markdown: str
    executive_summary: str

class ForensicResponseV1(BaseModel):
    technical_data: TechnicalDataV1
    human_translation: HumanTranslationV1
