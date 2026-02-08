from datetime import datetime, timedelta
import pytz
import swisseph as swe

def get_julian_day(dt_utc: datetime) -> float:
    """
    Calculate Julian Day from UTC datetime.
    """
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                      dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)

def _localize_with_historical_tz(local_tz: pytz.tzinfo.BaseTzInfo, naive_dt: datetime) -> tuple[datetime, datetime, dict]:
    meta = {
        "tz_abbrev": None,
        "utc_offset_hours": None,
        "dst_offset_hours": None,
        "tz_warning": None,
        "tz_resolution": None
    }
    try:
        localized = local_tz.localize(naive_dt, is_dst=None)
        meta["tz_resolution"] = "exact"
    except pytz.AmbiguousTimeError:
        localized = local_tz.localize(naive_dt, is_dst=False)
        meta["tz_resolution"] = "ambiguous_standard_time"
        meta["tz_warning"] = "Ambiguous local time due to DST; defaulted to standard time."
    except pytz.NonExistentTimeError:
        localized = local_tz.localize(naive_dt, is_dst=True)
        meta["tz_resolution"] = "nonexistent_shifted_to_dst"
        meta["tz_warning"] = "Non-existent local time during DST transition; defaulted to post-transition (DST)."

    utc_dt = localized.astimezone(pytz.utc)
    offset = localized.utcoffset() or timedelta(0)
    dst = localized.dst() or timedelta(0)
    meta["tz_abbrev"] = localized.tzname()
    meta["utc_offset_hours"] = round(offset.total_seconds() / 3600.0, 4)
    meta["dst_offset_hours"] = round(dst.total_seconds() / 3600.0, 4)
    if meta["tz_abbrev"] == "LMT":
        meta["tz_warning"] = (meta["tz_warning"] + " " if meta["tz_warning"] else "") + "Local Mean Time (LMT) in effect; standard time may not have been adopted."
    return localized, utc_dt, meta
