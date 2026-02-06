import swisseph as swe
import inspect

def debug_swe():
    try:
        print(f"Swe Version: {swe.version}")
    except:
        pass
    try:
        sig = inspect.signature(swe.rise_trans)
        print(f"Signature: {sig}")
    except ValueError:
        print("Signature not available (C extension).")
        print(f"Doc: {swe.rise_trans.__doc__}")

    # Test variations
    jd = 2450000.5
    sun = swe.SUN
    lat = 40.0
    lon = -74.0
    geopos = (lon, lat, 0)
    flags = swe.FLG_SWIEPH

    print("\nAttempt 1: 5 args with tuple (jd, sun, star, flags, geopos)")
    try:
        res = swe.rise_trans(jd, sun, 0, flags, geopos)
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")

    print("\nAttempt 2: 7 args scalars (jd, sun, star, flags, lon, lat, h)")
    try:
        res = swe.rise_trans(jd, sun, 0, flags, lon, lat, 0)
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")

    print("\nAttempt 3: 4 args (jd, sun, flags, geopos) - No starname")
    try:
        res = swe.rise_trans(jd, sun, flags, geopos)
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")

    print("\nAttempt 4: 9 args (jd, sun, star, flags, lon, lat, h, p, t)")
    try:
        res = swe.rise_trans(jd, sun, 0, flags, lon, lat, 0, 0, 0)
        print("Success!")
    except Exception as e:
        print(f"Failed: {e}")

debug_swe()
