from enum import Enum
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from .models import PlanetName, Chart, Planet, Sect, Sign
from .reference_data import (
    DOMICILES, EXALTATIONS, DOROTHEAN_TRIPLICITY, PTOLEMAIC_TRIPLICITY,
    EGYPTIAN_TERMS, PTOLEMAIC_TERMS, FACES_ORDER, SIGN_ELEMENTS
)

class ReceptionMode(Enum):
    STRICT_BONATTI = "Strict (Bonatti)"
    STANDARD_LILLY = "Standard (Lilly)"

@dataclass
class Reception:
    guest: PlanetName
    host: PlanetName
    dignities: List[str] # ["Domicile", "Term", etc]
    score: int
    is_valid: bool # Based on mode rules (e.g. Bonatti rejects single term)
    is_operative: bool # True if there is an applying aspect (or any aspect in Standard mode?)
    mode: str
    mitigation: str = "None"

@dataclass
class MutualReception:
    planet_a: PlanetName
    planet_b: PlanetName
    reception_a_in_b: Reception
    reception_b_in_a: Reception
    strength_score: int
    type: str # "Pure Domicile", "Mixed", etc.

class ReceptionEngine:
    """
    Implements the Computational Framework for Medieval Astrological Reception.
    Supports Strict (Bonatti) and Standard (Lilly) modes.
    """

    @staticmethod
    def _get_triplicity_rulers(element: str, sect: Sect, mode: ReceptionMode) -> List[PlanetName]:
        if mode == ReceptionMode.STRICT_BONATTI:
            # Day, Night, Part
            rulers = DOROTHEAN_TRIPLICITY[element]
            return list(rulers) # All 3 are valid lords in Bonatti
        else:
            # Ptolemaic (Lilly)
            # Tuple (Day, Night)
            day_ruler, night_ruler = PTOLEMAIC_TRIPLICITY[element]
            # Sect-gated: in a Day chart, only the Day triplicity ruler has rights; in a Night chart,
            # only the Night triplicity ruler has rights. Returning both causes false receptions.
            return [day_ruler] if sect == Sect.DAY else [night_ruler]

    @staticmethod
    def _get_term_ruler(sign: Sign, degree: float, mode: ReceptionMode) -> Optional[PlanetName]:
        try:
            terms = EGYPTIAN_TERMS[sign] if mode == ReceptionMode.STRICT_BONATTI else PTOLEMAIC_TERMS[sign]
        except KeyError:
            logging.warning("Terms key not found for sign: %s", sign)
            raise
            
        for p, limit in terms:
            if degree < limit:
                return p
        return None

    @staticmethod
    def _get_face_ruler(sign: Sign, degree: float) -> PlanetName:
        # Consistent across authors
        sign_idx = list(Sign).index(sign)
        face_idx = int(degree / 10)
        # Handle 30th degree edge case? int(30/10)=3 -> index out of bounds?
        if face_idx >= 3: face_idx = 2
        
        global_idx = (sign_idx * 3) + face_idx
        return FACES_ORDER[global_idx % len(FACES_ORDER)]

    @classmethod
    def analyze_reception(cls, guest: Planet, host: Planet, chart: Chart, mode: ReceptionMode) -> Reception:
        """
        Check if Guest is received by Host (Host has dignity in Guest's place).
        """
        dignities = []
        score = 0
        
        # 1. Domicile
        sign_idx = int(guest.longitude / 30) % 12
        sign = list(Sign)[sign_idx]
        degree = guest.longitude % 30
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        element = SIGN_ELEMENTS[sign]

        # Host check
        try:
            if DOMICILES[sign] == host.name:
                dignities.append("Domicile")
                score += 5
            
            if EXALTATIONS.get(sign) == host.name:
                dignities.append("Exaltation")
                score += 4
                
            triplicity_rulers = cls._get_triplicity_rulers(element, sect, mode)
            if host.name in triplicity_rulers:
                dignities.append("Triplicity")
                score += 3
        except KeyError as e:
            logging.warning("Reception calculation error - missing key: %s", e)
            raise e
            
        term_ruler = cls._get_term_ruler(sign, degree, mode)
        if term_ruler == host.name:
            dignities.append("Term")
            score += 2
            
        face_ruler = cls._get_face_ruler(sign, degree)
        if face_ruler == host.name:
            dignities.append("Face")
            score += 1

        # Validity Check based on Mode
        is_valid = False
        if mode == ReceptionMode.STRICT_BONATTI:
            # Bonatti rules: Needs significant dignity. 
            # Usually Domicile, Exaltation, Triplicity OR (Term AND Face) or variant.
            # Simplified: Score >= 3 (Triplicity) OR (Term and Face = 3) ??
            # Let's say Score >= 2 (at least Term)
            if score >= 3:
                is_valid = True
        else:
            # Standard: Any dignity counts
            if score >= 1:
                is_valid = True
                
        # Operative Check (Requires Aspect)
        # We need to find if there is an aspect in the chart between these two
        # For simplicity, we can pass aspects or calculate them here.
        # Let's assume we want to know if it's functional.
        
        is_operative = False
        mitigation = "None"
        
        # Check AspectEngine for connectivity
        from .aspects import AspectEngine
        all_aspects = AspectEngine.calculate_aspects(chart)
        
        rel_aspect = next((a for a in all_aspects if 
                          (a.planet_a == guest.name and a.planet_b == host.name) or
                          (a.planet_a == host.name and a.planet_b == guest.name)), None)
        
        if rel_aspect and is_valid:
            # Traditional rule: Operative reception usually requires an APPLYING aspect.
            # Standard mode might be more liberal.
            if mode == ReceptionMode.STRICT_BONATTI:
                if rel_aspect.is_applying:
                    is_operative = True
            else:
                is_operative = True # Standard allows separating but decreasingly effective
                
        # Mitigation Logic (The "Save Roll")
        # Rule: A received planet is protected or its debility is saved by the host.
        if is_operative:
            # Check guest condition (Detriment/Fall)
            from .dignities import DignityCalculator
            # This is a bit circular, but we can check the sign.
            # (Wait, check if target_file is updated with recent changes first)
            # Actually, we can check guest's total_score if we had it, 
            # or just look it up.
            
            # Simplified Mitigation Detection
            is_malefic = host.name in [PlanetName.MARS, PlanetName.SATURN]
            if is_malefic:
                mitigation = "Maleficence Neutralized (Host receives Guest)"
            else:
                mitigation = "Active Assistance"

        return Reception(
            guest=guest.name,
            host=host.name,
            dignities=dignities,
            score=score,
            is_valid=is_valid,
            is_operative=is_operative,
            mode=mode.value,
            mitigation=mitigation
        )

    @classmethod
    def calculate_mutual_receptions(cls, chart: Chart, mode: ReceptionMode = ReceptionMode.STANDARD_LILLY) -> List[MutualReception]:
        mutuals = []
        planets = [p for p in chart.planets if p.name in [
            PlanetName.SUN, PlanetName.MOON, PlanetName.MERCURY, 
            PlanetName.VENUS, PlanetName.MARS, PlanetName.JUPITER, PlanetName.SATURN
        ]]
        
        # Pairwise check
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                
                # Check A in B
                rec1 = cls.analyze_reception(p1, p2, chart, mode)
                # Check B in A
                rec2 = cls.analyze_reception(p2, p1, chart, mode)
                
                if rec1.is_valid and rec2.is_valid:
                    # Determine type
                    r_type = "Mixed"
                    s1 = rec1.score
                    s2 = rec2.score
                    
                    if "Domicile" in rec1.dignities and "Domicile" in rec2.dignities:
                        r_type = "Pure Domicile"
                    elif "Exaltation" in rec1.dignities and "Exaltation" in rec2.dignities:
                        r_type = "Pure Exaltation"
                    elif ("Domicile" in rec1.dignities and "Exaltation" in rec2.dignities) or \
                         ("Exaltation" in rec1.dignities and "Domicile" in rec2.dignities):
                        r_type = "Major Mixed"
                    
                    total_score = s1 + s2
                    
                    mutuals.append(MutualReception(
                        planet_a=p1.name,
                        planet_b=p2.name,
                        reception_a_in_b=rec1,
                        reception_b_in_a=rec2,
                        strength_score=total_score,
                        type=r_type
                    ))
                    
        return sorted(mutuals, key=lambda x: x.strength_score, reverse=True)
