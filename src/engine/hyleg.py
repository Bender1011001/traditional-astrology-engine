from typing import Dict, List, Optional, Tuple
from .models import Chart, Planet, PlanetName, Sect, Sign
from .dignities import DignityCalculator

class HylegAlcocodenEngine:
    """
    Implements the Medieval Hyleg and Alcocoden technique (Bonatti/Lilly).
    Used for Vitality and Longevity forecasting.
    """
    
    # Hylegical Houses (Whole Sign): 1, 10, 11, 7, 9
    # Bonatti adds 11th as succedent but strong.
    # Standard Hylegical Places: 1, 10, 11, 7, 9. (Some sources say 1, 10, 7, 9, 11).
    # We will use 1, 10, 11, 7, 9.
    HYLEGICAL_HOUSES = [1, 10, 11, 7, 9]

    # Planetary Years (Bonatti/Lilly)
    PLANETARY_YEARS = {
        PlanetName.SATURN: {"minor": 30, "mean": 43.5, "major": 57},
        PlanetName.JUPITER: {"minor": 12, "mean": 45.5, "major": 79},
        PlanetName.MARS: {"minor": 15, "mean": 40.5, "major": 66},
        PlanetName.SUN: {"minor": 19, "mean": 69.5, "major": 120},
        PlanetName.VENUS: {"minor": 8, "mean": 45, "major": 82},
        PlanetName.MERCURY: {"minor": 20, "mean": 48, "major": 76},
        PlanetName.MOON: {"minor": 25, "mean": 66.5, "major": 108}
    }

    @staticmethod
    def _is_in_hylegical_house(planet: Planet, chart: Chart) -> bool:
        # Use Whole Sign house as a fallback; require above-horizon if altitude is available.
        house = DignityCalculator.get_house_number(planet.longitude, chart.ascendant)
        if house not in HylegAlcocodenEngine.HYLEGICAL_HOUSES:
            return False
        if planet.altitude is not None:
            return planet.altitude > 0
        return True

    @staticmethod
    def _has_aspect_from_ruler(planet_pos: float, chart: Chart, sect: Sect) -> bool:
        """
        Bonatti Rule: The potential Hyleg must be aspected by one of its rulers.
        """
        rulers = DignityCalculator.get_essential_rulers(planet_pos, sect)
        # Flatten rulers to a set, filtering Nones
        active_rulers = {r for r in rulers.values() if r is not None}
        
        # Check if any of these rulers aspect the position
        # Aspects: 0, 60, 90, 120, 180 within orb.
        # Classic orb is generous, say 10 deg for vitality checks.
        
        for ruler_name in active_rulers:
            ruler_planet = next((p for p in chart.planets if p.name == ruler_name), None)
            if not ruler_planet: continue
            
            diff = abs(ruler_planet.longitude - planet_pos) % 360
            if diff > 180: diff = 360 - diff
            
            # Check major aspects with orb 10
            is_aspect = False
            for aspect in [0, 60, 90, 120, 180]:
                if abs(diff - aspect) <= 12: # Generous moity orb
                    is_aspect = True
                    break
            
            if is_aspect:
                return True
                
        return False

    @staticmethod
    def determine_hyleg(chart: Chart) -> Dict:
        """
        Determines the Hyleg (Giver of Life).
        Priority:
        Day: Sun -> Moon -> Asc.
        Night: Moon -> Sun -> Asc.
        Fallback: Part of Fortune, Syzygy (Simplified to Asc for now if others fail).
        """
        from .lots import calculate_lot_position, LotName
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        candidates = []
        if sect == Sect.DAY:
            candidates = [PlanetName.SUN, PlanetName.MOON]
        else:
            candidates = [PlanetName.MOON, PlanetName.SUN]
            
        # 1. Check Luminaries
        for name in candidates:
            planet = next((p for p in chart.planets if p.name == name), None)
            if not planet: continue
            
            if HylegAlcocodenEngine._is_in_hylegical_house(planet, chart):
                if HylegAlcocodenEngine._has_aspect_from_ruler(planet.longitude, chart, sect):
                    return {"type": "Planet", "name": name.value, "longitude": planet.longitude, "candidate": name}

        # 2. Check Lot of Fortune
        try:
            lot_fortune = calculate_lot_position(chart, LotName.FORTUNE, sect)
            lot_house = DignityCalculator.get_house_number(lot_fortune, chart.ascendant)
            if lot_house in HylegAlcocodenEngine.HYLEGICAL_HOUSES:
                if HylegAlcocodenEngine._has_aspect_from_ruler(lot_fortune, chart, sect):
                    return {"type": "Lot", "name": "Fortune", "longitude": lot_fortune, "candidate": "Fortune"}
        except Exception:
            pass
        
        # 3. Check Ascendant (Prevention of Asc Hyleg provided rulers aspect it)
        # Ascendant is usually valid if luminaries fail.
        # But technically needs aspect from ruler too.
        if HylegAlcocodenEngine._has_aspect_from_ruler(chart.ascendant, chart, sect):
             return {"type": "Angle", "name": "Ascendant", "longitude": chart.ascendant, "candidate": "Ascendant"}

        # 4. Fallback to Syzygy (not implemented), default to Ascendant if valid, else failure
        return {"type": "Fallback", "name": "Ascendant", "longitude": chart.ascendant, "candidate": "Ascendant"}

    @staticmethod
    def determine_alcocoden(hyleg_data: Dict, chart: Chart) -> Dict:
        """
        Determines the Alcocoden (Giver of Years).
        Hellenistic-first: term (bound) ruler of the Hyleg degree that aspects the Hyleg.
        """
        h_lon = hyleg_data["longitude"]
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        # Term (bound) ruler of the Hyleg degree
        rulers = DignityCalculator.get_essential_rulers(h_lon, sect)
        term_ruler = rulers.get("term")
        if not term_ruler:
            return None
        
        cand_planet = next((p for p in chart.planets if p.name == term_ruler), None)
        if not cand_planet:
            return None
        
        diff = abs(cand_planet.longitude - h_lon) % 360
        if diff > 180:
            diff = 360 - diff
        
        is_aspect = False
        for aspect in [0, 60, 90, 120, 180]:
            if abs(diff - aspect) <= 12:
                is_aspect = True
                break
        
        if not is_aspect:
            return None
        
        return {
            "name": term_ruler,
            "score": 2,
            "planet": cand_planet
        }

    @staticmethod
    def calculate_lifespan(hyleg: Dict, alcocoden: Dict, chart: Chart) -> Dict:
        if not alcocoden:
            return {"total_years": 0, "breakdown": ["No Alcocoden found."]}
        
        p_name = alcocoden["name"]
        p_obj = alcocoden["planet"]
        
        # 1. Determine Years Scale (Major, Mean, Minor)
        house = DignityCalculator.get_house_number(p_obj.longitude, chart.ascendant)
        dignity = DignityCalculator.calculate_planet_dignity(p_name, p_obj.longitude, Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT)
        dignity_score = dignity.get("total_score", 0)
        
        years_type = "Minor"
        base_years = HylegAlcocodenEngine.PLANETARY_YEARS[p_name]["minor"]
        
        if house in [1, 4, 7, 10] and dignity_score >= 4:
            years_type = "Major"
            base_years = HylegAlcocodenEngine.PLANETARY_YEARS[p_name]["major"]
        elif house in [2, 5, 8, 11] and dignity_score >= 0:
            years_type = "Mean"
            base_years = HylegAlcocodenEngine.PLANETARY_YEARS[p_name]["mean"]
        
        logs = [f"Base: {years_type} Years of {p_name.value} ({base_years}) due to House {house} and dignity {dignity_score}"]
        total = base_years
        
        # 2. Additions/Subtractions from Aspects
        # Benefics (Jup, Ven) add their Minor years
        # Malefics (Sat, Mars) subtract their Minor years
        # Mercury/Sun/Moon can add/subtract depending on nature/sect?
        # Simplified: Jup/Ven add, Sat/Mars subtract.
        
        for p in chart.planets:
            if p.name == p_name: continue
            
            # Check aspect
            diff = abs(p.longitude - p_obj.longitude) % 360
            if diff > 180: diff = 360 - diff
            
            is_aspect = False
            aspect_type = ""
            if abs(diff - 0) <= 8: aspect_type = "Conjunction"
            elif abs(diff - 60) <= 8: aspect_type = "Sextile"
            elif abs(diff - 90) <= 8: aspect_type = "Square"
            elif abs(diff - 120) <= 8: aspect_type = "Trine"
            elif abs(diff - 180) <= 8: aspect_type = "Opposition"
            
            if aspect_type:
                mod = 0
                if p.name not in HylegAlcocodenEngine.PLANETARY_YEARS:
                    continue
                    
                years_val = HylegAlcocodenEngine.PLANETARY_YEARS[p.name]["minor"]
                
                if p.name in [PlanetName.JUPITER, PlanetName.VENUS]:
                    # Benefics add (Conjunction, Trine, Sextile)
                    # Squares/Oppositions might not add or add less.
                    # Bonatti: Benefics always help unless very afflicted.
                    if aspect_type in ["Conjunction", "Trine", "Sextile"]:
                        mod = years_val
                    elif aspect_type in ["Square", "Opposition"]:
                         mod = years_val / 2 # Partial help
                         
                elif p.name in [PlanetName.SATURN, PlanetName.MARS]:
                    # Malefics subtract (Conj, Sq, Opp)
                    if aspect_type in ["Conjunction", "Square", "Opposition"]:
                        mod = -years_val
                    elif aspect_type in ["Trine", "Sextile"]:
                        mod = -years_val / 4 # Minimal harm? Or maybe helpful?
                        # Malefics in good aspect usually just didn't harm.
                        mod = 0
                
                if mod != 0:
                    total += mod
                    action = "Added" if mod > 0 else "Subtracted"
                    logs.append(f"{action} {abs(mod):.1f} ({p.name.value} {aspect_type})")

        # Safety clamp to prevent negative or zero years in output (unless intended by tradition, but generally 0 is not useful)
        if total < 5:
             logs.append("Vitality score adjusted to minimum threshold.")
             total = max(total, 5.0)

        # Classification
        rating = "Moderate"
        if total >= 70: rating = "Superior"
        elif total >= 50: rating = "Strong"
        elif total >= 25: rating = "Moderate"
        else: rating = "Cautionary (Requires strengthening)"

        return {
            "hyleg": hyleg["name"],
            "alcocoden": p_name.value,
            "base_years_type": years_type,
            "base_years": base_years,
            "total_years": total,
            "vitality_rating": rating,
            "breakdown": logs
        }
