import swisseph as swe
from datetime import datetime, timedelta

def find_mercury_cazimi():
    # Start checking from now (Feb 5, 2026, 18:00) for the next 48 hours
    start_jd = swe.julday(2026, 2, 5, 18, 0)
    
    best_jd = start_jd
    min_diff = 360
    
    print("Searching for Mercury-Sun Conjunction (Cazimi)...")
    
    # Precise scan every 10 minutes for the next 2 days
    for i in range(288): 
        jd = start_jd + (i * 10 / 1440.0)
        
        sun_res = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0]
        merc_res = swe.calc_ut(jd, swe.MERCURY, swe.FLG_SWIEPH)[0]
        
        sun_lon = sun_res[0]
        merc_lon = merc_res[0]
        
        diff = abs(sun_lon - merc_lon) % 360
        diff = min(diff, 360 - diff)
        
        if diff < min_diff:
            min_diff = diff
            best_jd = jd
            
    y, m, d, h = swe.revjul(best_jd)
    # Convert fractional hours to m/s
    hours = int(h)
    minutes = int((h - hours) * 60)
    seconds = int(((h - hours) * 60 - minutes) * 60)
    
    print(f"Optimal Moment (UTC): {y}-{m}-{d} {hours:02d}:{minutes:02d}:{seconds:02d}")
    print(f"Minimum Distance: {min_diff:.6f} degrees")
    
    # PST is UTC-8
    pst_h = (hours - 8) % 24
    print(f"Optimal Moment (PST): {pst_h:02d}:{minutes:02d}:{seconds:02d}")
    
    if min_diff < 0.28:
        print("✓ YES: This is a CAZIMI moment.")
    else:
        print("✗ NO: This is only a conjunction, not Cazimi.")

if __name__ == "__main__":
    find_mercury_cazimi()
