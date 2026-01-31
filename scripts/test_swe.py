import swisseph as swe
import sys

with open("test_swe_result.txt", "w") as f:
    f.write(f"DOC: {swe.rise_trans.__doc__}\n")
    
    jd = 2460000.5
    geopos = (-74.006, 40.7128, 0)
    
    try:
        res = swe.rise_trans(jd, swe.SUN, "", swe.FLG_SWIEPH, 0, geopos, 0, 0)
        f.write(f"Success 8 args: {res}\n")
    except Exception as e:
        f.write(f"Fail 8 args: {e}\n")

    try:
        # Try without starname?
        # Maybe arguments are: jd, ipl, flag, geoname...
        # No, pyswisseph typically strictly follows C API or has specific wrappers.
        pass
    except:
        pass
        
    try:
        # Common error: geopos expects tuple of length 3?
        f.write(f"Geopos used: {geopos}\n")
    except:
        pass
