from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Literal, Optional

from .models import Planet, PlanetName, Sign
from .reference_data import EGYPTIAN_TERMS, MOIETIES

# ==========================================
# 1. ANTISCIA & CONTRA-ANTISCIA (Shadow Points)
# ==========================================


@dataclass
class AntisciaPoint:
    original_lon: float
    antiscia_lon: float
    contra_antiscia_lon: float
    antiscia_sign: Sign
    contra_antiscia_sign: Sign


def normalize_deg(deg: float) -> float:
    return deg % 360.0


def get_sign_from_lon(lon: float) -> Sign:
    idx = int((lon % 360.0) / 30.0) % 12
    return list(Sign)[idx]


def calculate_antiscia_points(longitude: float) -> AntisciaPoint:
    """
    Calculates the Antiscia (Solstice Reflection) and Contra-Antiscia (Equinox Reflection).
    Formula: Antiscia = (180 - longitude) % 360
    Contra = (Antiscia + 180) % 360
    """
    antiscia = normalize_deg(180.0 - longitude)
    contra_antiscia = normalize_deg(antiscia + 180.0)

    return AntisciaPoint(
        original_lon=longitude,
        antiscia_lon=antiscia,
        contra_antiscia_lon=contra_antiscia,
        antiscia_sign=get_sign_from_lon(antiscia),
        contra_antiscia_sign=get_sign_from_lon(contra_antiscia),
    )


def check_antiscia_aspect(
    p1_lon: float, p1_name: PlanetName, p2_lon: float, p2_name: PlanetName
) -> Optional[Dict]:
    """
    Checks if Planet 2 is conjunct the Antiscion or Contra-Antiscion of Planet 1.
    Uses strict 'Moiety' orbs as per Lilly.
    """
    shadows = calculate_antiscia_points(p1_lon)

    # Get Moieties (Orbs)
    orb1 = MOIETIES.get(p1_name, 5.0)
    orb2 = MOIETIES.get(p2_name, 5.0)
    mean_orb = (orb1 + orb2) / 2.0

    # Check CONJUNCTION to ANTISCIA
    dist_ant = abs(p2_lon - shadows.antiscia_lon)
    if dist_ant > 180:
        dist_ant = 360 - dist_ant

    if dist_ant <= mean_orb:
        return {
            "type": "Antiscia",
            "quality": "Hidden Support",
            "orb": dist_ant,
            "exact": dist_ant <= 1.0,
        }

    # Check CONJUNCTION to CONTRA-ANTISCIA
    dist_contra = abs(p2_lon - shadows.contra_antiscia_lon)
    if dist_contra > 180:
        dist_contra = 360 - dist_contra

    if dist_contra <= mean_orb:
        return {
            "type": "Contra-Antiscia",
            "quality": "Hidden Friction",
            "orb": dist_contra,
            "exact": dist_contra <= 1.0,
        }

    return None


def calculate_antiscia_configurations(
    chart_planets: List[Planet], *, orb_limit: float = 1.0
) -> List[Dict]:
    """Return source-auditable major aspects made through the antiscia.

    Firmicus, *Mathesis* II.29.9, does not limit the doctrine to a body
    conjoining another body's antiscion.  He explicitly names trine, square,
    sextile, and opposition through the reflected point as operative like the
    corresponding ordinary configurations.  His passage supplies no numerical
    orb, so customer publication uses a disclosed conservative one-degree
    configured limit rather than the legacy planetary-moiety allowance.
    """
    if orb_limit < 0:
        raise ValueError("Antiscia orb_limit must be non-negative")
    angles = (
        ("Conjunction", 0.0),
        ("Sextile", 60.0),
        ("Square", 90.0),
        ("Trine", 120.0),
        ("Opposition", 180.0),
    )
    traditional = {
        PlanetName.SUN,
        PlanetName.MOON,
        PlanetName.MERCURY,
        PlanetName.VENUS,
        PlanetName.MARS,
        PlanetName.JUPITER,
        PlanetName.SATURN,
    }
    planets = [planet for planet in chart_planets if planet.name in traditional]
    results: List[Dict] = []
    for index, first in enumerate(planets):
        antiscion = calculate_antiscia_points(first.longitude).antiscia_lon
        for second in planets[index + 1 :]:
            separation = abs(((second.longitude - antiscion + 180.0) % 360.0) - 180.0)
            aspect_name = None
            aspect_angle = None
            orb = None
            for candidate_name, candidate_angle in angles:
                candidate_orb = abs(separation - candidate_angle)
                if candidate_orb <= orb_limit:
                    aspect_name = candidate_name
                    aspect_angle = candidate_angle
                    orb = candidate_orb
                    break
            if aspect_name is None or aspect_angle is None or orb is None:
                continue
            results.append(
                {
                    "planet_1": first.name.value,
                    "planet_2": second.name.value,
                    "antiscion_of": first.name.value,
                    "antiscion_longitude": antiscion,
                    "aspect": aspect_name,
                    "aspect_angle": aspect_angle,
                    "orb": round(orb, 6),
                    "orb_limit": orb_limit,
                    "source_rule_id": "firmicus_antiscia_major_configurations",
                }
            )
    return results


# ==========================================
# 2. DODECATEMORIA (Twelfth-Parts)
# ==========================================


@dataclass
class Dodecatemorion:
    method: Literal["Valens", "Paul"]
    longitude: float
    sign: Sign
    term_ruler: str
    term_nature: str


def get_egyptian_term_ruler(lon: float) -> str:
    sign_idx = int((lon % 360.0) / 30.0) % 12
    sign = list(Sign)[sign_idx]
    deg_in_sign = lon % 30.0

    terms = EGYPTIAN_TERMS.get(sign, [])
    for ruler, limit in terms:
        if deg_in_sign < limit:
            return ruler.value
    return "Unknown"


def calculate_dodecatemorion(
    longitude: float, method: Literal["Valens", "Paul"] = "Valens"
) -> Dodecatemorion:
    sign_idx = int((longitude % 360.0) / 30.0) % 12
    sign_start = sign_idx * 30.0
    deg_in_sign = longitude % 30.0

    # ``Valens`` is a legacy API token for the configured x12 variant. The
    # historical attribution is unresolved and must not leak into customer
    # prose as a verified claim.
    multiplier = 12.0 if method == "Valens" else 13.0

    projected_arc = deg_in_sign * multiplier
    abs_dodec = normalize_deg(sign_start + projected_arc)

    term_ruler = get_egyptian_term_ruler(abs_dodec)

    return Dodecatemorion(
        method=method,
        longitude=abs_dodec,
        sign=get_sign_from_lon(abs_dodec),
        term_ruler=term_ruler,
        term_nature="Neutral",
    )


# ==========================================
# 3. PLANETARY DAYS & HOURS (Chronocrators)
# ==========================================


@dataclass
class PlanetaryHourInfo:
    day_of_week: str
    day_lord: str
    hour_lord: str
    hour_number: int  # 1-24
    is_daytime: bool
    radicality: str
    night_lord: str


CHALDEAN_ORDER = [
    PlanetName.SATURN,
    PlanetName.JUPITER,
    PlanetName.MARS,
    PlanetName.SUN,
    PlanetName.VENUS,
    PlanetName.MERCURY,
    PlanetName.MOON,
]


def calculate_planetary_hours(
    dt: datetime, lat: float, lon: float, asc_sign: Sign = None, asc_lord: str = None  # type: ignore
) -> PlanetaryHourInfo:
    """
    Calculates the Planetary Hour and Radicality using the Unequal/Temporal Hour method.

    Delegates core sunrise/sunset calculation to PlanetaryHourEngine (which handles
    the JD search correctly) and adds radicality assessment on top.
    """
    from .planetary_hours import PlanetaryHourEngine

    report = PlanetaryHourEngine.calculate_hours(dt, lat, lon)
    if not report or "error" in report:
        return None  # type: ignore

    day_lord_name = PlanetName(report["day_ruler"])
    hour_lord_name = PlanetName(report["hour_ruler"])
    is_day = report["phase"] == "DAY"
    hour_number = report["hour_number_civil"]

    # Night lord: 13th hour from day lord in Chaldean order
    start_idx = CHALDEAN_ORDER.index(day_lord_name)
    night_lord_idx = (start_idx + 12) % 7
    night_lord = CHALDEAN_ORDER[night_lord_idx]

    # Radicality check
    radicality = "Unknown"
    if asc_lord:
        if hour_lord_name == PlanetName(asc_lord):
            radicality = "Radical (Identity)"
        elif asc_sign:
            radicality = "Caution (No Identity)"
        else:
            radicality = "Caution (No Identity)"

    return PlanetaryHourInfo(
        day_of_week=day_lord_name.value + "'s Day",
        day_lord=day_lord_name.value,
        hour_lord=hour_lord_name.value,
        hour_number=hour_number,
        is_daytime=is_day,
        radicality=radicality,
        night_lord=night_lord.value,
    )


# ==========================================
# 4. HELPER EXPORT
# ==========================================
class ClassicalMechanicsEngine:
    @staticmethod
    def get_antiscia(longitude: float) -> AntisciaPoint:
        return calculate_antiscia_points(longitude)

    @staticmethod
    def get_dodecatemorion(longitude: float, method="Valens") -> Dodecatemorion:
        return calculate_dodecatemorion(longitude, method)

    @staticmethod
    def get_planetary_hours(
        dt: datetime,
        lat: float,
        lon: float,
        asc_sign: Sign = None,  # type: ignore
        asc_lord: str = None,  # type: ignore
    ) -> PlanetaryHourInfo:
        return calculate_planetary_hours(dt, lat, lon, asc_sign, asc_lord)

    @staticmethod
    def check_shadow_aspects(chart_planets: List[Planet]) -> List[Dict]:
        results = []
        for i, p1 in enumerate(chart_planets):
            for j, p2 in enumerate(chart_planets):
                if i >= j:
                    continue
                aspect = check_antiscia_aspect(
                    p1.longitude, p1.name, p2.longitude, p2.name
                )
                if aspect:
                    results.append(
                        {
                            "planet_1": p1.name.value,
                            "planet_2": p2.name.value,
                            "type": aspect["type"],
                            "quality": aspect["quality"],
                            "orb": round(aspect["orb"], 2),
                            "partile": aspect["exact"],
                        }
                    )
        return results

    @staticmethod
    def get_antiscia_configurations(
        chart_planets: List[Planet], *, orb_limit: float = 1.0
    ) -> List[Dict]:
        return calculate_antiscia_configurations(
            chart_planets, orb_limit=orb_limit
        )
