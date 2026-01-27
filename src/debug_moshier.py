import swisseph as swe

def test_moshier():
    print(f"Version: {swe.version}")
    jd = 2450000.5
    
    print("Testing FLG_SWIEPH (Expect Fail)...")
    try:
        res = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)
        print(f"Success SWIEPH: {res}")
    except swe.Error as e:
        print(f"Fail SWIEPH: {e}")

    print("Testing FLG_MOSEPH (Expect Success)...")
    try:
        res = swe.calc_ut(jd, swe.MOON, swe.FLG_MOSEPH)
        print(f"Success MOSEPH: {res}")
    except swe.Error as e:
        print(f"Fail MOSEPH: {e}")
        
    print("Testing FLG_JPLEPH (Expect Fail)...")
    try:
        res = swe.calc_ut(jd, swe.MOON, swe.FLG_JPLEPH)
        print(f"Success JPLEPH: {res}")
    except swe.Error as e:
        print(f"Fail JPLEPH: {e}")
        
    print("Testing Default (0)...")
    try:
        res = swe.calc_ut(jd, swe.MOON, 0)
        print(f"Success Default: {res}")
    except swe.Error as e:
        print(f"Fail Default: {e}")

test_moshier()
