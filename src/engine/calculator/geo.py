from __future__ import annotations

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable
from timezonefinder import TimezoneFinder
import os
import time
import json
import hashlib
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__name__)

from src.engine.cache_manager import CACHE_DIR

# Initialize Geocoder
_ua_base = os.getenv("NOMINATIM_USER_AGENT", "astrology_app/1.0")
_ua_contact = os.getenv("NOMINATIM_CONTACT", "").strip()
_user_agent = f"{_ua_base} ({_ua_contact})" if _ua_contact else _ua_base
_timeout = int(os.getenv("NOMINATIM_TIMEOUT", "10"))
_max_attempts = max(1, int(os.getenv("NOMINATIM_MAX_ATTEMPTS", "3")))
_backoff_seconds = float(os.getenv("NOMINATIM_BACKOFF_SECONDS", "1.0"))

geolocator = Nominatim(user_agent=_user_agent, timeout=_timeout)
tf = TimezoneFinder()

_GEOCODE_CACHE_FILE = os.path.join(CACHE_DIR, "geocode_cache.json")
_GEOCODE_CACHE_TTL_DAYS = int(os.getenv("GEOCODE_CACHE_TTL_DAYS", "3650"))
_HTTP_TIMEOUT_SECONDS = int(os.getenv("GEOCODE_HTTP_TIMEOUT", "10"))


def _normalize_query(city: str, state: str = "") -> str:
    city = (city or "").strip()
    state = (state or "").strip()
    query = f"{city}, {state}" if state else city
    # Normalize spacing/case to maximize cache hits.
    return " ".join(query.split()).strip().lower()


def _load_geocode_cache() -> dict:
    try:
        if not os.path.exists(_GEOCODE_CACHE_FILE):
            return {}
        with open(_GEOCODE_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception as e:
        logger.debug("Geocode cache load failed: %s", e)
        return {}


def _save_geocode_cache(cache: dict) -> None:
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        tmp = _GEOCODE_CACHE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f)
        os.replace(tmp, _GEOCODE_CACHE_FILE)
    except Exception as e:
        logger.debug("Geocode cache save failed: %s", e)
        # Best-effort cache; never break chart calculation.
        return


def _cache_key(query_norm: str) -> str:
    return hashlib.sha256(query_norm.encode("utf-8")).hexdigest()


def _cache_get(query_norm: str) -> tuple[float, float] | None:
    cache = _load_geocode_cache()
    k = _cache_key(query_norm)
    row = cache.get(k)
    if not isinstance(row, dict):
        return None

    created = row.get("created")
    if created:
        try:
            created_dt = datetime.fromisoformat(created)
            if created_dt < (datetime.utcnow() - timedelta(days=_GEOCODE_CACHE_TTL_DAYS)):
                return None
        except Exception as e:
            logger.debug("Cache TTL parse failed: %s", e)
            return None

    lat = row.get("lat")
    lon = row.get("lon")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        return float(lat), float(lon)
    return None


def _cache_set(query_norm: str, lat: float, lon: float) -> None:
    cache = _load_geocode_cache()
    k = _cache_key(query_norm)
    cache[k] = {"created": datetime.utcnow().replace(microsecond=0).isoformat(), "lat": float(lat), "lon": float(lon)}
    _save_geocode_cache(cache)


def _http_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": _user_agent,
            "Accept": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT_SECONDS) as resp:
        data = resp.read().decode("utf-8", errors="replace")
    return json.loads(data)


def _geocode_us_census(city: str, state: str) -> tuple[float, float] | None:
    """
    Free fallback geocoder for US locations (no API key).
    """
    if not city or not state:
        return None

    base = "https://geocoding.geo.census.gov/geocoder/locations/address"
    params = {
        "city": city,
        "state": state,
        "benchmark": "2020",
        "format": "json",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    try:
        payload = _http_json(url)
        matches = (
            payload.get("result", {})
            .get("addressMatches", [])
        )
        if not matches:
            # Try the more forgiving one-line endpoint
            base2 = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
            params2 = {"address": f"{city}, {state}", "benchmark": "2020", "format": "json"}
            url2 = base2 + "?" + urllib.parse.urlencode(params2)
            payload2 = _http_json(url2)
            matches = payload2.get("result", {}).get("addressMatches", [])

        if matches:
            coords = matches[0].get("coordinates", {})
            lon = coords.get("x")
            lat = coords.get("y")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                return float(lat), float(lon)
    except Exception as e:
        logger.debug("US Census geocoding failed: %s", e)
        return None
    return None


def _geocode_open_meteo(city: str, state: str = "") -> tuple[float, float] | None:
    """
    Free fallback geocoder (rate limits exist, but different from Nominatim).
    """
    if not city:
        return None

    base = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 5,
        "language": "en",
        "format": "json",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    try:
        payload = _http_json(url)
        results = payload.get("results") or []
        if not results:
            return None

        state_norm = (state or "").strip().lower()
        best = None
        if state_norm:
            # Prefer entries whose admin1 matches the requested state code/name.
            for r in results:
                admin1 = (r.get("admin1") or "").strip().lower()
                cc = (r.get("country_code") or "").strip().upper()
                # US only filter if state provided (avoid Fairfield UK, etc).
                if cc == "US" and (state_norm in admin1 or admin1.startswith(state_norm)):
                    best = r
                    break
        if best is None:
            # Otherwise prefer US result if any, else first result.
            best = next((r for r in results if (r.get("country_code") or "").upper() == "US"), results[0])

        lat = best.get("latitude")
        lon = best.get("longitude")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            return float(lat), float(lon)
    except Exception as e:
        logger.debug("Open-Meteo geocoding failed: %s", e)
        return None
    return None


def get_coordinates(city: str, state: str = "") -> tuple[float, float]:
    """
    Get latitude and longitude for a given city and state.
    """
    query_norm = _normalize_query(city, state)
    # Tests should be deterministic: avoid using a persistent on-disk cache during pytest runs.
    if not os.getenv("PYTEST_CURRENT_TEST"):
        cached = _cache_get(query_norm)
        if cached:
            return cached

    query = f"{city}, {state}" if state else city
    last_error = None
    for attempt in range(1, _max_attempts + 1):
        try:
            location = geolocator.geocode(query, exactly_one=True)
            if location:
                lat, lon = float(location.latitude), float(location.longitude)
                _cache_set(query_norm, lat, lon)
                return lat, lon
            raise ValueError(f"Could not find location: {query}")
        except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError) as e:
            last_error = e
            if attempt < _max_attempts:
                time.sleep(_backoff_seconds * attempt)
                continue

    # Fallbacks: if Nominatim is rate-limited/down, try alternate free sources.
    state_str = (state or "").strip()

    # US Census tends to be stable for US city/state.
    us_census = _geocode_us_census((city or "").strip(), state_str)
    if us_census:
        _cache_set(query_norm, us_census[0], us_census[1])
        return us_census

    # Open-Meteo geocoding is a decent general fallback.
    open_meteo = _geocode_open_meteo((city or "").strip(), state_str)
    if open_meteo:
        _cache_set(query_norm, open_meteo[0], open_meteo[1])
        return open_meteo

    raise ValueError(
        f"Geocoding failed after {_timeout}s and {_max_attempts} attempts. "
        f"Last error: {last_error}"
    )


def get_coordinates_with_meta(city: str, state: str = "") -> tuple[float, float, dict]:
    """
    Same as `get_coordinates`, but returns metadata about how the coordinates were obtained.

    This is used to make reports auditable: the system must be able to show which
    provider (or cache) supplied the latitude/longitude.
    """
    query_norm = _normalize_query(city, state)

    # Tests should be deterministic: avoid using a persistent on-disk cache during pytest runs.
    if not os.getenv("PYTEST_CURRENT_TEST"):
        cached = _cache_get(query_norm)
        if cached:
            return cached[0], cached[1], {"source": "cache", "query_norm": query_norm}

    # Attempt Nominatim first (may be rate-limited).
    query = f"{city}, {state}" if state else city
    last_error = None
    for attempt in range(1, _max_attempts + 1):
        try:
            location = geolocator.geocode(query, exactly_one=True)
            if location:
                lat, lon = float(location.latitude), float(location.longitude)
                _cache_set(query_norm, lat, lon)
                return lat, lon, {"source": "nominatim", "query": query, "query_norm": query_norm}
            raise ValueError(f"Could not find location: {query}")
        except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError) as e:
            last_error = e
            if attempt < _max_attempts:
                time.sleep(_backoff_seconds * attempt)
                continue

    # Fallbacks
    state_str = (state or "").strip()

    us_census = _geocode_us_census((city or "").strip(), state_str)
    if us_census:
        _cache_set(query_norm, us_census[0], us_census[1])
        return us_census[0], us_census[1], {"source": "us_census", "query": f"{city}, {state_str}", "query_norm": query_norm}

    open_meteo = _geocode_open_meteo((city or "").strip(), state_str)
    if open_meteo:
        _cache_set(query_norm, open_meteo[0], open_meteo[1])
        return open_meteo[0], open_meteo[1], {"source": "open_meteo", "query": f"{city}, {state_str}", "query_norm": query_norm}

    raise ValueError(
        f"Geocoding failed after {_timeout}s and {_max_attempts} attempts. "
        f"Last error: {last_error}"
    )

def get_timezone(lat: float, lon: float) -> str:
    """
    Resolve timezone for a given coordinate pair.
    """
    tz_str = tf.timezone_at(lng=lon, lat=lat)
    if not tz_str:
        raise ValueError("Could not determine timezone")
    return tz_str

def get_local_datetime_now(city: str, state: str) -> datetime:
    """
    Get current local time for a city/state.
    """
    lat, lon = get_coordinates(city, state)
    tz_str = get_timezone(lat, lon)
    tz = pytz.timezone(tz_str)
    return datetime.now(tz)
