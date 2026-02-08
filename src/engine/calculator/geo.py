from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable
from timezonefinder import TimezoneFinder
import os
import time
from datetime import datetime
import pytz

# Initialize Geocoder
_ua_base = os.getenv("NOMINATIM_USER_AGENT", "astrology_app/1.0")
_ua_contact = os.getenv("NOMINATIM_CONTACT", "").strip()
_user_agent = f"{_ua_base} ({_ua_contact})" if _ua_contact else _ua_base
_timeout = int(os.getenv("NOMINATIM_TIMEOUT", "10"))
_max_attempts = max(1, int(os.getenv("NOMINATIM_MAX_ATTEMPTS", "3")))
_backoff_seconds = float(os.getenv("NOMINATIM_BACKOFF_SECONDS", "1.0"))

geolocator = Nominatim(user_agent=_user_agent, timeout=_timeout)
tf = TimezoneFinder()

def get_coordinates(city: str, state: str = "") -> tuple[float, float]:
    """
    Get latitude and longitude for a given city and state.
    """
    query = f"{city}, {state}" if state else city
    last_error = None
    for attempt in range(1, _max_attempts + 1):
        try:
            location = geolocator.geocode(query, exactly_one=True)
            if location:
                return location.latitude, location.longitude
            raise ValueError(f"Could not find location: {query}")
        except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError) as e:
            last_error = e
            if attempt < _max_attempts:
                time.sleep(_backoff_seconds * attempt)
                continue
            raise ValueError(
                f"Geocoding failed after {_timeout}s and {_max_attempts} attempts. "
                f"Last error: {e}"
            ) from e
    raise ValueError(f"Geocoding failed: {last_error}")

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
