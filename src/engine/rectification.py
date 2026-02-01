import swisseph as swe
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from .models import PlanetName, Sign, Sect, Chart, Planet
from .dignities import DignityCalculator
from .chart_calculator import get_julian_day

class RectificationEngine:
    """
    Implements traditional rectification protocols:
    1. Animodar (Ptolemaic Method)
    2. Trutina Hermetis (Pre-natal Epoch)
    """

    @staticmethod
    def find_prenatal_syzygy(jd_birth: float) -> Dict:
        """
        Finds the prenatal syzygy (New or Full Moon) before birth.
        Returns JD, type, and longitude.
        """
        # Search backwards from birth JD
        jd = jd_birth
        
        # We search for the first occurrence of either a New Moon or Full Moon before birth
        # Using swe.houses_armc or similar is not needed, we just need the relative positions of Sun and Moon
        
        def get_sun_moon_diff(jd_test: float) -> float:
            sun_res = swe.calc_ut(jd_test, swe.SUN, swe.FLG_SWIEPH)[0][0]
            moon_res = swe.calc_ut(jd_test, swe.MOON, swe.FLG_SWIEPH)[0][0]
            return (moon_res - sun_res) % 360

        # Step back by 1 day until we cross 0 or 180
        curr_jd = jd
        prev_diff = get_sun_moon_diff(curr_jd)
        
        # Refine search
        # A lunation is ~29.5 days, so we don't need to go back more than 30 days
        for _ in range(30 * 24): # Hourly steps for 30 days
            curr_jd -= (1/24.0)
            curr_diff = get_sun_moon_diff(curr_jd)
            
            # Check for crossing 0 (New Moon) or 180 (Full Moon)
            # Crossing 0: prev_diff was small positive, curr_diff is large (near 360)
            if (prev_diff < 10 and curr_diff > 350) or (prev_diff >= 0 and curr_diff < 0): # New Moon
                # Refine to exact New Moon
                return RectificationEngine._refine_syzygy(curr_jd, 0)
            
            # Crossing 180: prev_diff was > 180, curr_diff is < 180
            if prev_diff >= 180 and curr_diff < 180:
                return RectificationEngine._refine_syzygy(curr_jd, 180)
            
            prev_diff = curr_diff

        return {}

    @staticmethod
    def _refine_syzygy(jd_approx: float, target_diff: float) -> Dict:
        # Binary search or simple iteration to find exact JD where diff == target_diff
        low = jd_approx
        high = jd_approx + (1/24.0)
        
        for _ in range(20):
            mid = (low + high) / 2
            sun_lon = swe.calc_ut(mid, swe.SUN, swe.FLG_SWIEPH)[0][0]
            moon_lon = swe.calc_ut(mid, swe.MOON, swe.FLG_SWIEPH)[0][0]
            diff = (moon_lon - sun_lon) % 360
            
            if target_diff == 0:
                if diff > 180: # Wrapped around
                    low = mid
                else:
                    high = mid
            else: # target_diff == 180
                if diff > 180:
                    high = mid
                else:
                    low = mid
        
        final_jd = (low + high) / 2
        sun_lon = swe.calc_ut(final_jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
        moon_lon = swe.calc_ut(final_jd, swe.MOON, swe.FLG_SWIEPH)[0][0]
        
        return {
            "jd": final_jd,
            "type": "New Moon" if target_diff == 0 else "Full Moon",
            "longitude": sun_lon if target_diff == 0 else (sun_lon if abs(sun_lon - (moon_lon - 180)%360) < 1 else moon_lon)
            # Ptolemy: For Full Moon, use the degree of the luminary above the horizon? 
            # Or more simply: the degree of the syzygy itself.
        }

    @staticmethod
    def animodar_rectification(chart: Chart, birth_jd: float, lat: float, lon: float) -> List[Dict]:
        """
        Animodar (Ptolemaic Method):
        1. Find prenatal syzygy degree.
        2. Find the planet with most dignity at that degree.
        3. The degree of that planet in the birth chart is the 'corrected' degree for Asc or MC.
        """
        syzygy = RectificationEngine.find_prenatal_syzygy(birth_jd)
        if not syzygy:
            return []
            
        syz_lon = syzygy["longitude"]
        syz_jd = syzygy["jd"]
        
        # Determine chart sect at syzygy for triplicity
        sun_res = swe.calc_ut(syz_jd, swe.SUN, swe.FLG_SWIEPH)[0]
        sun_lon = sun_res[0]
        sun_lat = sun_res[1]
        
        # Calculate Sun altitude at syzygy location
        geopos = (lon, lat, 0)
        xin = (sun_lon, sun_lat, sun_res[2])
        azresult = swe.azalt(syz_jd, swe.ECL2HOR, geopos, 0, 0, xin)
        sun_alt = azresult[1]
        syz_sect = Sect.DAY if sun_alt > 0 else Sect.NIGHT
        
        rulers = DignityCalculator.get_essential_rulers(syz_lon, syz_sect)
        
        # Ptolemy's Ruler: The planet that has the most dignity at the syzygy degree.
        # We calculate scores for each of the 5 rulers.
        scores = {}
        for d_type, p_name in rulers.items():
            if not p_name: continue
            weight = {"domicile": 5, "exaltation": 4, "triplicity": 3, "term": 2, "face": 1}[d_type]
            scores[p_name] = scores.get(p_name, 0) + weight
            
        if not scores:
            return []
            
        rectifying_planet_name = max(scores, key=scores.get)
        
        # Find this planet in the birth chart
        rectifying_planet = next((p for p in chart.planets if p.name == rectifying_planet_name), None)
        if not rectifying_planet:
            return []
            
        target_degree = rectifying_planet.degree_in_sign
        
        # Suggestions: Ascendant or MC should have this degree in its sign.
        results = []
        
        # Suggestion 1: Correct Ascendant
        current_asc_deg = chart.ascendant % 30
        diff_asc = abs(current_asc_deg - target_degree)
        if diff_asc > 15: diff_asc = 30 - diff_asc
        
        results.append({
            "method": "Animodar",
            "rectifying_planet": rectifying_planet_name.value,
            "target_degree": target_degree,
            "suggestion": "Correct Ascendant to match degree",
            "current_degree": current_asc_deg,
            "difference": diff_asc,
            "confidence": max(0, 100 - diff_asc * 5)
        })
        
        # Suggestion 2: Correct MC
        current_mc_deg = chart.mc % 30
        diff_mc = abs(current_mc_deg - target_degree)
        if diff_mc > 15: diff_mc = 30 - diff_mc
        
        results.append({
            "method": "Animodar",
            "rectifying_planet": rectifying_planet_name.value,
            "target_degree": target_degree,
            "suggestion": "Correct MC to match degree",
            "current_degree": current_mc_deg,
            "difference": diff_mc,
            "confidence": max(0, 100 - diff_mc * 5)
        })
        
        return results

    @staticmethod
    def trutina_hermetis(birth_jd: float, lat: float, lon: float) -> List[Dict]:
        """
        Trutina Hermetis (Pre-natal Epoch):
        'The degree of the Moon at birth was the Ascendant at conception, and vice versa.'
        Average gestation: 273 days.
        """
        # 1. Get Birth Moon and Birth Ascendant
        res_moon = swe.calc_ut(birth_jd, swe.MOON, swe.FLG_SWIEPH)[0]
        birth_moon_lon = res_moon[0]
        
        cusps, ascmc = swe.houses(birth_jd, lat, lon, b'P')
        birth_asc = ascmc[0]
        
        # 2. Search around 273 days before birth
        target_conception_jd = birth_jd - 273
        
        # The Rule: 
        # Conception Ascendant = Birth Moon
        # Conception Moon = Birth Ascendant
        
        suggestions = []
        
        # We search a window of +/- 15 days around the 273 day mark
        for day_offset in range(-15, 16):
            check_jd = target_conception_jd + day_offset
            
            # Find when Moon matches Birth Ascendant on this day
            # Moon moves ~13 degrees/day
            # There will be one time on this day when Moon is at birth_asc
            
            # Rough estimate for Moon position at start of day
            m_start = swe.calc_ut(check_jd, swe.MOON, swe.FLG_SWIEPH)[0][0]
            # Time of day (in fractions) when Moon reaches birth_asc
            diff = (birth_asc - m_start) % 360
            time_fraction = diff / 13.17 # Approximate Moon speed
            
            conception_jd = check_jd + time_fraction
            
            # Refine conception_jd to exact Moon = Birth Asc
            for _ in range(5):
                m_curr = swe.calc_ut(conception_jd, swe.MOON, swe.FLG_SWIEPH)[0][0]
                m_diff = (birth_asc - m_curr + 180) % 360 - 180
                conception_jd += m_diff / 13.17
            
            # Now, at this conception_jd, check if the Ascendant matches the Birth Moon
            _, c_ascmc = swe.houses(conception_jd, lat, lon, b'P')
            c_asc = c_ascmc[0]
            
            c_asc_diff = abs(c_asc - birth_moon_lon)
            if c_asc_diff > 180: c_asc_diff = 360 - c_asc_diff
            
            # If the difference is small, this is a potential conception time
            # Since Ascendant moves 360 degrees in 24 hours, even a small time change affects it
            # We look for the moment in that day when Ascendant = Birth Moon
            
            # Actually, the Trutina Hermetis is more often used to find birth time from conception.
            # But we can reverse it: Find a conception time that satisfies the rule, 
            # and then see how it affects the birth time suggestion.
            
            if c_asc_diff < 15: # Within 1 hour approx
                 # Refine: find exact JD on that day when c_asc == birth_moon_lon
                 # Then the Moon at that moment should be the Birth Ascendant
                 suggestions.append({
                     "conception_jd": conception_jd,
                     "conception_asc": c_asc,
                     "birth_moon_lon": birth_moon_lon,
                     "difference": c_asc_diff,
                     "gestation_days": birth_jd - conception_jd
                 })

        # Process suggestions to find the best match and derive corrected birth time
        # For simplicity, we'll return the matches found.
        # A more advanced version would adjust the birth JD to make the rule perfect.
        
        results = []
        for s in suggestions:
            # If the rule were perfect:
            # New Birth Asc = Conception Moon
            # New Birth Moon = Conception Asc
            
            # We suggest a corrected birth time based on the Conception Moon being the Birth Ascendant
            c_moon = swe.calc_ut(s["conception_jd"], swe.MOON, swe.FLG_SWIEPH)[0][0]
            
            results.append({
                "method": "Trutina Hermetis",
                "suggested_ascendant": c_moon,
                "conception_date": swe.revjul(s["conception_jd"]),
                "gestation_days": round(s["gestation_days"], 2),
                "confidence": max(0, 100 - s["difference"] * 6)
            })
            
    @staticmethod
    def pauline_monomoiria_rectification(chart: Chart) -> List[Dict]:
        """
        Pauline Trigonal Monomoiria Rectification (Reconstructing Paul p. 30):
        Protocol:
        1. Identify the Sect Light (Sun by day, Moon by night).
        2. Calculate the 'Trigonal Monomoiria' ruler of the Sect Light.
        3. The Ascendant degree must have a 'sympathetic' relationship 
           (usually being in the Monomoiria of the same planet, 
           or the planet being in the Ascendant).
        """
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        sect_light = next((p for p in chart.planets if p.name == (PlanetName.SUN if sect == Sect.DAY else PlanetName.MOON)), None)
        
        if not sect_light:
            return []
            
        # Get Trigonal Monomoiria Ruler of Sect Light
        from .advanced_mechanics import MonomoiriaEngine
        light_ruler = MonomoiriaEngine.get_trigonal_monomoiria(sect_light.longitude, sect)
        
        # Current Ascendant Monomoiria ruler
        asc_ruler = MonomoiriaEngine.get_trigonal_monomoiria(chart.ascendant, sect)
        
        results = []
        is_matched = (light_ruler == asc_ruler)
        
        # Alternative: Is the light_ruler in the Ascendant sign?
        asc_sign = list(Sign)[int(chart.ascendant / 30) % 12]
        ruler_in_asc = False
        ruler_planet = next((p for p in chart.planets if p.name == light_ruler), None)
        if ruler_planet and list(Sign)[int(ruler_planet.longitude / 30) % 12] == asc_sign:
            ruler_in_asc = True

        results.append({
            "method": "Pauline Monomoiria",
            "sect_light": sect_light.name.value,
            "monomoiria_ruler": light_ruler.value,
            "asc_monomoiria_ruler": asc_ruler.value,
            "is_matched": is_matched,
            "ruler_in_ascendant": ruler_in_asc,
            "suggestion": f"Adjust birth time so Ascendant degree is ruled by {light_ruler.value} (Monomoiria).",
            "confidence": 85 if is_matched or ruler_in_asc else 40
        })
        
        return results

