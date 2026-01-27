from enum import Enum
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
    mode: str

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
            rulers = PTOLEMAIC_TRIPLICITY[element]
            # Lilly usually considers the primary ruler of the sect as the main lord, 
            # but for reception, being "in the triplicity of X" usually implies X has rights.
            # However, Ptolemaic table only has 2 rulers. 
            # We return both.
            return list(rulers)

    @staticmethod
    def _get_term_ruler(sign: Sign, degree: float, mode: ReceptionMode) -> Optional[PlanetName]:
        try:
            terms = EGYPTIAN_TERMS[sign] if mode == ReceptionMode.STRICT_BONATTI else PTOLEMAIC_TERMS[sign]
        except KeyError:
            print(f"DEBUG TERM ERROR: Missing key {sign} in Terms dict.")
            # Print keys for debugging
            if mode == ReceptionMode.STRICT_BONATTI:
                print(f"Egyptian keys: {list(EGYPTIAN_TERMS.keys())}")
            else:
                print(f"Ptolemaic keys: {list(PTOLEMAIC_TERMS.keys())}")
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
            print(f"DEBUG RECEPTION ERROR: Key {e} | Sign: {sign} | Dicts involved: DOMICILES keys={list(DOMICILES.keys())}, SIGN_ELEMENTS keys={list(SIGN_ELEMENTS.keys())}")
            raise e
            
        term_ruler = cls._get_term_ruler(sign, degree, mode)
        if term_ruler == host.name:
            dignities.append("Term")
            score += 2
            
        face_ruler = cls._get_face_ruler(sign, degree)
        if face_ruler == host.name:
            dignities.append("Face")
            score += 1

        # Validity Check (Bonatti Rules)
        is_valid = False
        if len(dignities) > 0:
            if mode == ReceptionMode.STANDARD_LILLY:
                is_valid = True
            else:
                # Bonatti Strict Rules
                # Valid if Domicile OR Exaltation
                # OR (Triplicity AND (Term OR Face))
                # OR (Term AND Face)
                has_major = "Domicile" in dignities or "Exaltation" in dignities
                has_trip = "Triplicity" in dignities
                has_term = "Term" in dignities
                has_face = "Face" in dignities
                
                if has_major:
                    is_valid = True
                elif has_trip and (has_term or has_face):
                    is_valid = True
                elif has_term and has_face:
                    is_valid = True
                else:
                    is_valid = False

        return Reception(
            guest=guest.name,
            host=host.name,
            dignities=dignities,
            score=score,
            is_valid=is_valid,
            mode=mode.value
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
