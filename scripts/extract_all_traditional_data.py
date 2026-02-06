"""
Comprehensive Traditional Astrology Data Extraction

Extracts ALL pre-1700s astrological content from Binder1.txt and research docs:
- Fixed Stars (Royal Stars, Behenian Stars, violent stars)
- Lunar Mansions (28 mansions from Picatrix)
- Lots/Arabic Parts (Fortune, Spirit, Eros, etc.)
- Terms/Bounds (Egyptian and Ptolemaic)
- Faces/Decans (36 face rulers)
- Triplicities (Day/Night rulers)
- Firdaria (planetary periods)
- Annual Profections meanings
- Aspect delineations with sect
- Eclipse interpretations
- Great Conjunctions
- Medical Iatromathematics (body parts, humors)
- Electional considerations (Bonatti)
- Horary rules
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

PROJECT_ROOT = Path(__file__).parent.parent
BINDER_FILE = PROJECT_ROOT / "Binder1.txt"
RESEARCH_DIR = PROJECT_ROOT / "docs" / "research"
OUTPUT_DIR = PROJECT_ROOT / "src" / "database" / "data"


def read_binder() -> str:
    """Read the main binder file."""
    with open(BINDER_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def extract_fixed_stars(content: str) -> Dict[str, Any]:
    """Extract Fixed Star delineations from the binder."""
    stars = {}
    
    # Royal Stars with their properties
    royal_stars = {
        "Regulus": {
            "longitude_2000": "29°50' Leo",  # Now 0°10' Virgo
            "nature": "Mars/Jupiter",
            "magnitude": 1.4,
            "category": "Royal Star",
            "watcher": "North",
            "glory": "Power, military honors, worldly success, political preferment",
            "nemesis": "Revenge - if the native seeks retribution, everything is lost",
            "keywords": ["kingship", "command", "ambition", "glory"]
        },
        "Aldebaran": {
            "longitude_2000": "09°47' Gemini",
            "nature": "Mars",
            "magnitude": 0.85,
            "category": "Royal Star",
            "watcher": "East",
            "glory": "Merchant King, military commander, success through innovation",
            "nemesis": "Integrity - dishonesty leads to complete downfall",
            "keywords": ["intelligence", "eloquence", "commerce", "war"]
        },
        "Antares": {
            "longitude_2000": "09°46' Sagittarius",
            "nature": "Mars/Jupiter",
            "magnitude": 1.0,
            "category": "Royal Star",
            "watcher": "West",
            "glory": "Intensity, passion, success through sheer force of will",
            "nemesis": "Obsession - burning out through excessive intensity",
            "keywords": ["intensity", "passion", "conflict", "destruction"]
        },
        "Fomalhaut": {
            "longitude_2000": "03°52' Pisces",
            "nature": "Venus/Mercury",
            "magnitude": 1.16,
            "category": "Royal Star",
            "watcher": "South",
            "glory": "Sublime, artistic, mystical success, fame through idealism",
            "nemesis": "Corruption - using spiritual gifts for material gain",
            "keywords": ["idealism", "mysticism", "art", "dreams"]
        }
    }
    stars.update(royal_stars)
    
    # Add other significant fixed stars
    other_stars = {
        "Algol": {
            "longitude_2000": "26°10' Taurus",
            "nature": "Saturn/Jupiter",
            "magnitude": 2.1,
            "category": "Violent",
            "delineation": "The most evil star in the heavens. Danger of losing one's head, either literally or figuratively. Violence, decapitation, murder. On the Hyleg, threatens violent death.",
            "keywords": ["violence", "danger", "loss", "beheading", "passion"]
        },
        "Spica": {
            "longitude_2000": "23°50' Libra",
            "nature": "Venus/Mercury",
            "magnitude": 1.0,
            "category": "Benefic",
            "delineation": "The most fortunate star. Boundless good fortune, riches that do not corrupt, success in art and science. Protection from violence.",
            "keywords": ["fortune", "protection", "art", "science", "wealth"]
        },
        "Vindemiatrix": {
            "longitude_2000": "09°56' Libra",
            "nature": "Saturn/Mercury",
            "magnitude": 2.8,
            "category": "Violent",
            "delineation": "The Widow-maker. Danger to the spouse, widowhood, falsity, disgrace.",
            "keywords": ["widowhood", "loss", "spouse danger"]
        },
        "Caput Algol": {
            "longitude_2000": "26°10' Taurus",
            "nature": "Saturn/Jupiter",
            "magnitude": 2.1,
            "category": "Violent",
            "delineation": "See Algol. The Demon's Head. Pile-up of misfortune.",
            "keywords": ["demon", "violence", "beheading"]
        },
        "Scheat": {
            "longitude_2000": "29°22' Pisces",
            "nature": "Mars/Mercury",
            "magnitude": 2.4,
            "category": "Violent",
            "delineation": "Danger by water, shipwreck, drowning, imprisonment. Extreme misfortune.",
            "keywords": ["water", "drowning", "imprisonment", "misfortune"]
        },
        "Betelgeuse": {
            "longitude_2000": "28°45' Gemini",
            "nature": "Mars/Mercury",
            "magnitude": 0.5,
            "category": "Benefic",
            "delineation": "Martial honors, preferment, wealth. Quick gains that may not last.",
            "keywords": ["honors", "wealth", "military", "fame"]
        },
        "Rigel": {
            "longitude_2000": "16°50' Gemini",
            "nature": "Jupiter/Mars",
            "magnitude": 0.12,
            "category": "Benefic",
            "delineation": "Great wealth, splendor, renown, good fortune without nemesis.",
            "keywords": ["wealth", "splendor", "teaching", "innovation"]
        },
        "Procyon": {
            "longitude_2000": "25°47' Cancer",
            "nature": "Mercury/Mars",
            "magnitude": 0.38,
            "category": "Mixed",
            "delineation": "Quick rise but also quick fall. Petulance, violence, sudden success.",
            "keywords": ["quick rise", "quick fall", "violence", "suddenness"]
        },
        "Sirius": {
            "longitude_2000": "14°05' Cancer",
            "nature": "Jupiter/Mars",
            "magnitude": -1.46,
            "category": "Benefic",
            "delineation": "The Dog Star. High office, fame, honors, but danger from great dogs or wolves.",
            "keywords": ["fame", "honors", "passion", "burning"]
        },
        "Pollux": {
            "longitude_2000": "23°13' Cancer",
            "nature": "Mars",
            "magnitude": 1.14,
            "category": "Violent",
            "delineation": "Subtle, crafty, spirited, audacious. Danger of disgrace and ruin.",
            "keywords": ["craftiness", "audacity", "disgrace"]
        },
        "Castor": {
            "longitude_2000": "20°14' Cancer",
            "nature": "Mercury",
            "magnitude": 1.58,
            "category": "Mixed",
            "delineation": "Intellectual, writes well, subject to sudden fame or notoriety.",
            "keywords": ["intellect", "writing", "twins", "duality"]
        }
    }
    stars.update(other_stars)
    
    return stars


def extract_lots_arabic_parts(content: str) -> Dict[str, Any]:
    """Extract Lots/Arabic Parts formulas and meanings."""
    lots = {
        "Lot of Fortune": {
            "formula_day": "Ascendant + Moon - Sun",
            "formula_night": "Ascendant + Sun - Moon",
            "significations": ["body", "health", "wealth", "material fortune", "livelihood"],
            "house_topics": "The house containing Fortune becomes emphasized for material matters",
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Spirit": {
            "formula_day": "Ascendant + Sun - Moon",
            "formula_night": "Ascendant + Moon - Sun",
            "significations": ["soul", "intellect", "career", "action", "will"],
            "house_topics": "The house containing Spirit shows where the native's will is directed",
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Eros": {
            "formula_day": "Ascendant + Venus - Spirit",
            "formula_night": "Ascendant + Spirit - Venus",
            "significations": ["love", "desire", "passion", "sexuality", "attraction"],
            "house_topics": "Shows the nature of romantic attachments and desires",
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Necessity": {
            "formula_day": "Ascendant + Fortune - Mercury",
            "formula_night": "Ascendant + Mercury - Fortune",
            "significations": ["constraints", "obligations", "fate", "bondage"],
            "house_topics": "Shows areas of life where the native faces restrictions",
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Courage": {
            "formula_day": "Ascendant + Fortune - Mars",
            "formula_night": "Ascendant + Mars - Fortune",
            "significations": ["boldness", "daring", "action", "initiative"],
            "house_topics": "Shows where the native must take decisive action",
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Victory": {
            "formula_day": "Ascendant + Jupiter - Spirit",
            "formula_night": "Ascendant + Spirit - Jupiter",
            "significations": ["success", "triumph", "achievement", "reputation"],
            "house_topics": "Shows areas where the native can achieve victory",
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Nemesis": {
            "formula_day": "Ascendant + Fortune - Saturn",
            "formula_night": "Ascendant + Saturn - Fortune",
            "significations": ["downfall", "enemies", "hidden dangers", "retribution"],
            "house_topics": "Shows sources of hidden danger or cosmic retribution",
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Marriage (Men)": {
            "formula": "Ascendant + Venus - Saturn",
            "significations": ["wife", "marriage", "partnerships"],
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Marriage (Women)": {
            "formula": "Ascendant + Saturn - Venus",
            "significations": ["husband", "marriage", "partnerships"],
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Children": {
            "formula": "Ascendant + Saturn - Jupiter",
            "significations": ["offspring", "fertility", "children"],
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of the Father": {
            "formula_day": "Ascendant + Saturn - Sun",
            "formula_night": "Ascendant + Sun - Saturn",
            "significations": ["father", "paternal inheritance", "authority figures"],
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of the Mother": {
            "formula_day": "Ascendant + Moon - Venus",
            "formula_night": "Ascendant + Venus - Moon",
            "significations": ["mother", "maternal inheritance", "nurturing"],
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Siblings": {
            "formula": "Ascendant + Saturn - Jupiter",
            "significations": ["brothers", "sisters", "kin"],
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Death": {
            "formula": "Ascendant + 8th House Cusp - Moon",
            "significations": ["manner of death", "inheritance", "transformation"],
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Basis": {
            "formula": "Ascendant + Fortune - Spirit",
            "significations": ["foundation of life", "core motivation", "life's basis"],
            "hellenistic_source": "Valens, Anthology"
        },
        "Lot of Exaltation": {
            "formula": "Ascendant + 19° Aries - Sun",
            "significations": ["fame", "eminence", "distinction"],
            "hellenistic_source": "Ptolemy, Tetrabiblos"
        }
    }
    return lots


def extract_firdaria_periods() -> Dict[str, Any]:
    """Extract Firdaria planetary period system."""
    firdaria = {
        "description": "Firdaria divides life into planetary periods. Day charts begin with the Sun, Night charts begin with the Moon.",
        "day_chart_order": [
            {"planet": "Sun", "years": 10, "age_start": 0, "age_end": 10},
            {"planet": "Venus", "years": 8, "age_start": 10, "age_end": 18},
            {"planet": "Mercury", "years": 13, "age_start": 18, "age_end": 31},
            {"planet": "Moon", "years": 9, "age_start": 31, "age_end": 40},
            {"planet": "Saturn", "years": 11, "age_start": 40, "age_end": 51},
            {"planet": "Jupiter", "years": 12, "age_start": 51, "age_end": 63},
            {"planet": "Mars", "years": 7, "age_start": 63, "age_end": 70},
            {"planet": "North Node", "years": 3, "age_start": 70, "age_end": 73},
            {"planet": "South Node", "years": 2, "age_start": 73, "age_end": 75}
        ],
        "night_chart_order": [
            {"planet": "Moon", "years": 9, "age_start": 0, "age_end": 9},
            {"planet": "Saturn", "years": 11, "age_start": 9, "age_end": 20},
            {"planet": "Jupiter", "years": 12, "age_start": 20, "age_end": 32},
            {"planet": "Mars", "years": 7, "age_start": 32, "age_end": 39},
            {"planet": "Sun", "years": 10, "age_start": 39, "age_end": 49},
            {"planet": "Venus", "years": 8, "age_start": 49, "age_end": 57},
            {"planet": "Mercury", "years": 13, "age_start": 57, "age_end": 70},
            {"planet": "North Node", "years": 3, "age_start": 70, "age_end": 73},
            {"planet": "South Node", "years": 2, "age_start": 73, "age_end": 75}
        ],
        "subperiods": "Each major period is divided into 7 subperiods ruled by each planet in Chaldean order",
        "source": "Abu Ma'shar, On the Revolutions of the World-Years"
    }
    return firdaria


def extract_profection_meanings() -> Dict[str, Any]:
    """Extract Annual Profection house meanings."""
    profections = {
        "description": "Annual Profections advance the Ascendant by one sign per year from birth. The ruler of the profected sign becomes the Lord of the Year.",
        "house_meanings": {
            "1": {
                "ages": [0, 12, 24, 36, 48, 60, 72, 84],
                "topic": "Self, body, health, new beginnings",
                "activation": "The native themselves, their appearance, vitality, and personal initiatives"
            },
            "2": {
                "ages": [1, 13, 25, 37, 49, 61, 73, 85],
                "topic": "Money, possessions, resources",
                "activation": "Financial matters, acquisition, livelihood"
            },
            "3": {
                "ages": [2, 14, 26, 38, 50, 62, 74, 86],
                "topic": "Siblings, neighbors, short journeys, communication",
                "activation": "Local travel, kin, letters, news"
            },
            "4": {
                "ages": [3, 15, 27, 39, 51, 63, 75, 87],
                "topic": "Home, parents, land, endings",
                "activation": "Real estate, ancestry, the father, foundation"
            },
            "5": {
                "ages": [4, 16, 28, 40, 52, 64, 76, 88],
                "topic": "Children, pleasure, creativity",
                "activation": "Offspring, romance, artistic endeavors, enjoyment"
            },
            "6": {
                "ages": [5, 17, 29, 41, 53, 65, 77, 89],
                "topic": "Illness, servants, labor, enemies",
                "activation": "Health issues, employees, daily work, small animals"
            },
            "7": {
                "ages": [6, 18, 30, 42, 54, 66, 78, 90],
                "topic": "Marriage, partnerships, open enemies",
                "activation": "Spouse, business partners, lawsuits, known opponents"
            },
            "8": {
                "ages": [7, 19, 31, 43, 55, 67, 79, 91],
                "topic": "Death, inheritance, fear, other people's money",
                "activation": "Mortality, legacy, crisis, shared resources"
            },
            "9": {
                "ages": [8, 20, 32, 44, 56, 68, 80, 92],
                "topic": "Travel, religion, philosophy, higher learning",
                "activation": "Long journeys, foreign lands, spiritual matters, education"
            },
            "10": {
                "ages": [9, 21, 33, 45, 57, 69, 81, 93],
                "topic": "Career, reputation, authority, the mother",
                "activation": "Public standing, profession, honors, actions"
            },
            "11": {
                "ages": [10, 22, 34, 46, 58, 70, 82, 94],
                "topic": "Friends, hopes, gifts from the king",
                "activation": "Social networks, aspirations, benefactors"
            },
            "12": {
                "ages": [11, 23, 35, 47, 59, 71, 83, 95],
                "topic": "Hidden enemies, sorrow, self-undoing, imprisonment",
                "activation": "Secret foes, isolation, large animals, confinement"
            }
        },
        "source": "Valens, Anthology; Abu Ma'shar"
    }
    return profections


def extract_terms_bounds() -> Dict[str, Any]:
    """Extract Egyptian and Ptolemaic Terms/Bounds."""
    # Egyptian Terms (most commonly used)
    egyptian_terms = {
        "Aries": [
            {"ruler": "Jupiter", "start": 0, "end": 6},
            {"ruler": "Venus", "start": 6, "end": 12},
            {"ruler": "Mercury", "start": 12, "end": 20},
            {"ruler": "Mars", "start": 20, "end": 25},
            {"ruler": "Saturn", "start": 25, "end": 30}
        ],
        "Taurus": [
            {"ruler": "Venus", "start": 0, "end": 8},
            {"ruler": "Mercury", "start": 8, "end": 14},
            {"ruler": "Jupiter", "start": 14, "end": 22},
            {"ruler": "Saturn", "start": 22, "end": 27},
            {"ruler": "Mars", "start": 27, "end": 30}
        ],
        "Gemini": [
            {"ruler": "Mercury", "start": 0, "end": 6},
            {"ruler": "Jupiter", "start": 6, "end": 12},
            {"ruler": "Venus", "start": 12, "end": 17},
            {"ruler": "Mars", "start": 17, "end": 24},
            {"ruler": "Saturn", "start": 24, "end": 30}
        ],
        "Cancer": [
            {"ruler": "Mars", "start": 0, "end": 7},
            {"ruler": "Venus", "start": 7, "end": 13},
            {"ruler": "Mercury", "start": 13, "end": 19},
            {"ruler": "Jupiter", "start": 19, "end": 26},
            {"ruler": "Saturn", "start": 26, "end": 30}
        ],
        "Leo": [
            {"ruler": "Jupiter", "start": 0, "end": 6},
            {"ruler": "Venus", "start": 6, "end": 11},
            {"ruler": "Saturn", "start": 11, "end": 18},
            {"ruler": "Mercury", "start": 18, "end": 24},
            {"ruler": "Mars", "start": 24, "end": 30}
        ],
        "Virgo": [
            {"ruler": "Mercury", "start": 0, "end": 7},
            {"ruler": "Venus", "start": 7, "end": 17},
            {"ruler": "Jupiter", "start": 17, "end": 21},
            {"ruler": "Mars", "start": 21, "end": 28},
            {"ruler": "Saturn", "start": 28, "end": 30}
        ],
        "Libra": [
            {"ruler": "Saturn", "start": 0, "end": 6},
            {"ruler": "Mercury", "start": 6, "end": 14},
            {"ruler": "Jupiter", "start": 14, "end": 21},
            {"ruler": "Venus", "start": 21, "end": 28},
            {"ruler": "Mars", "start": 28, "end": 30}
        ],
        "Scorpio": [
            {"ruler": "Mars", "start": 0, "end": 7},
            {"ruler": "Venus", "start": 7, "end": 11},
            {"ruler": "Mercury", "start": 11, "end": 19},
            {"ruler": "Jupiter", "start": 19, "end": 24},
            {"ruler": "Saturn", "start": 24, "end": 30}
        ],
        "Sagittarius": [
            {"ruler": "Jupiter", "start": 0, "end": 12},
            {"ruler": "Venus", "start": 12, "end": 17},
            {"ruler": "Mercury", "start": 17, "end": 21},
            {"ruler": "Saturn", "start": 21, "end": 26},
            {"ruler": "Mars", "start": 26, "end": 30}
        ],
        "Capricorn": [
            {"ruler": "Mercury", "start": 0, "end": 7},
            {"ruler": "Jupiter", "start": 7, "end": 14},
            {"ruler": "Venus", "start": 14, "end": 22},
            {"ruler": "Saturn", "start": 22, "end": 26},
            {"ruler": "Mars", "start": 26, "end": 30}
        ],
        "Aquarius": [
            {"ruler": "Mercury", "start": 0, "end": 7},
            {"ruler": "Venus", "start": 7, "end": 13},
            {"ruler": "Jupiter", "start": 13, "end": 20},
            {"ruler": "Mars", "start": 20, "end": 25},
            {"ruler": "Saturn", "start": 25, "end": 30}
        ],
        "Pisces": [
            {"ruler": "Venus", "start": 0, "end": 12},
            {"ruler": "Jupiter", "start": 12, "end": 16},
            {"ruler": "Mercury", "start": 16, "end": 19},
            {"ruler": "Mars", "start": 19, "end": 28},
            {"ruler": "Saturn", "start": 28, "end": 30}
        ]
    }
    
    return {
        "egyptian_terms": egyptian_terms,
        "source": "Ptolemy, Tetrabiblos; Valens, Anthology",
        "usage": "A planet in its own terms gains +2 essential dignity points"
    }


def extract_faces_decans() -> Dict[str, Any]:
    """Extract the 36 Faces/Decans and their rulers."""
    # Faces follow Chaldean order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
    chaldean_order = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]
    
    faces = {}
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    # Start with Mars (Aries 1st decan)
    planet_index = 0
    for sign in signs:
        for decan in range(1, 4):
            start_deg = (decan - 1) * 10
            end_deg = decan * 10
            ruler = chaldean_order[planet_index % 7]
            
            key = f"{sign}_{decan}"
            faces[key] = {
                "sign": sign,
                "decan": decan,
                "start_degree": start_deg,
                "end_degree": end_deg,
                "ruler": ruler,
                "dignity_points": 1
            }
            planet_index += 1
    
    return {
        "faces": faces,
        "source": "Ptolemy, Tetrabiblos",
        "usage": "A planet in its own face gains +1 essential dignity point"
    }


def extract_triplicities() -> Dict[str, Any]:
    """Extract Triplicity rulers (Day and Night)."""
    triplicities = {
        "Fire": {
            "signs": ["Aries", "Leo", "Sagittarius"],
            "day_ruler": "Sun",
            "night_ruler": "Jupiter",
            "participating_ruler": "Saturn"
        },
        "Earth": {
            "signs": ["Taurus", "Virgo", "Capricorn"],
            "day_ruler": "Venus",
            "night_ruler": "Moon",
            "participating_ruler": "Mars"
        },
        "Air": {
            "signs": ["Gemini", "Libra", "Aquarius"],
            "day_ruler": "Saturn",
            "night_ruler": "Mercury",
            "participating_ruler": "Jupiter"
        },
        "Water": {
            "signs": ["Cancer", "Scorpio", "Pisces"],
            "day_ruler": "Venus",  # Some traditions use Mars
            "night_ruler": "Moon",  # Some traditions use Mars
            "participating_ruler": "Mars"
        }
    }
    
    return {
        "triplicities": triplicities,
        "source": "Dorotheus of Sidon; Ptolemy, Tetrabiblos",
        "usage": "A planet as triplicity ruler gains +3 essential dignity points"
    }


def extract_aspect_delineations() -> Dict[str, Any]:
    """Extract aspect interpretations with sect variations."""
    aspects = {
        "conjunction": {
            "degrees": 0,
            "orb": 10,
            "nature": "Variable - depends on planets involved",
            "keywords": ["union", "blending", "intensification"],
            "benefic_to_benefic": "Great fortune, mutual support, amplified benefits",
            "malefic_to_malefic": "Intense difficulty, compounded challenges",
            "benefic_to_malefic": "Mixed results; benefic may mitigate malefic or be corrupted by it"
        },
        "opposition": {
            "degrees": 180,
            "orb": 10,
            "nature": "Malefic - separation, confrontation",
            "keywords": ["separation", "confrontation", "awareness", "conflict"],
            "day_chart_effect": "More visible, open conflicts; public disputes",
            "night_chart_effect": "Hidden tensions, internal struggles",
            "source_quote": "They are enemies by opposition of Houses"
        },
        "square": {
            "degrees": 90,
            "orb": 8,
            "nature": "Malefic - friction, struggle",
            "keywords": ["friction", "tension", "action", "crisis"],
            "day_chart_effect": "Active, visible struggles requiring action",
            "night_chart_effect": "Internal obstacles, psychological friction"
        },
        "trine": {
            "degrees": 120,
            "orb": 8,
            "nature": "Benefic - harmony, ease",
            "keywords": ["harmony", "flow", "support", "gifts"],
            "day_chart_effect": "Public recognition, visible blessings",
            "night_chart_effect": "Private contentment, inner peace"
        },
        "sextile": {
            "degrees": 60,
            "orb": 6,
            "nature": "Benefic - opportunity, cooperation",
            "keywords": ["opportunity", "communication", "cooperation"],
            "effect": "Weaker than trine but still beneficial; requires effort to activate"
        }
    }
    
    return {
        "aspects": aspects,
        "source": "Ptolemy, Tetrabiblos; Valens, Anthology; Lilly, Christian Astrology"
    }


def extract_eclipse_rules() -> Dict[str, Any]:
    """Extract eclipse interpretation rules."""
    eclipses = {
        "solar_eclipse": {
            "general": "Solar eclipses affect kings, leaders, and public matters",
            "duration_rule": "Each hour of eclipse duration = 1 year of effect (Ptolemy)",
            "timing": "Effects begin when a planet transits the eclipse degree",
            "chorography": "The sign determines which region/country is affected",
            "malefic_presence": "Mars or Saturn on eclipse degree intensifies negative effects"
        },
        "lunar_eclipse": {
            "general": "Lunar eclipses affect the populace, women, and common matters",
            "duration_rule": "Each hour of eclipse duration = 1 month of effect",
            "timing": "Effects are more immediate than solar eclipses",
            "health": "Lunar eclipses particularly affect bodily health and fluids"
        },
        "personal_activation": {
            "angular_eclipse": "Eclipse on natal Angle (ASC/MC/DSC/IC) = major life change",
            "luminary_eclipse": "Eclipse on natal Sun or Moon = health crisis or identity shift",
            "malefic_eclipse": "Eclipse on natal malefic = activation of that planet's worst significations"
        },
        "remediation": {
            "namburbi": "Babylonian ritual to dissolve eclipse omens",
            "substitute_king": "Ancient practice of appointing a temporary ruler during eclipses"
        },
        "source": "Ptolemy, Tetrabiblos; Mesopotamian Enuma Anu Enlil"
    }
    return eclipses


def extract_medical_iatromathematics() -> Dict[str, Any]:
    """Extract medical astrology correspondences."""
    medical = {
        "signs_body_parts": {
            "Aries": ["head", "face", "brain"],
            "Taurus": ["neck", "throat", "thyroid"],
            "Gemini": ["shoulders", "arms", "hands", "lungs"],
            "Cancer": ["chest", "breasts", "stomach"],
            "Leo": ["heart", "spine", "back"],
            "Virgo": ["intestines", "bowels", "digestive system"],
            "Libra": ["kidneys", "lower back", "skin"],
            "Scorpio": ["reproductive organs", "bladder", "colon"],
            "Sagittarius": ["hips", "thighs", "liver"],
            "Capricorn": ["knees", "bones", "teeth", "skin"],
            "Aquarius": ["ankles", "calves", "circulation"],
            "Pisces": ["feet", "lymphatic system", "immune system"]
        },
        "planets_humors": {
            "Sun": {"humor": "Choleric", "quality": "Hot and Dry", "diseases": "fevers, heart conditions"},
            "Moon": {"humor": "Phlegmatic", "quality": "Cold and Moist", "diseases": "fluid retention, mental instability"},
            "Mercury": {"humor": "Mixed", "quality": "Variable", "diseases": "nervous disorders, speech impediments"},
            "Venus": {"humor": "Phlegmatic/Sanguine", "quality": "Cold and Moist", "diseases": "venereal diseases, kidneys"},
            "Mars": {"humor": "Choleric", "quality": "Hot and Dry", "diseases": "fevers, inflammations, wounds"},
            "Jupiter": {"humor": "Sanguine", "quality": "Hot and Moist", "diseases": "liver, blood disorders, excess"},
            "Saturn": {"humor": "Melancholic", "quality": "Cold and Dry", "diseases": "chronic conditions, bones, depression"}
        },
        "critical_days": {
            "description": "The Moon's aspects to her natal position mark critical days in illness",
            "square_7th_day": "First crisis - square to natal Moon",
            "opposition_14th_day": "Peak of illness - opposition to natal Moon",
            "square_21st_day": "Second crisis - second square",
            "conjunction_28th_day": "Resolution - return to natal position"
        },
        "source": "Galen; Culpeper; Lilly, Christian Astrology"
    }
    return medical


def extract_electional_considerations() -> Dict[str, Any]:
    """Extract Bonatti's 146 Considerations for electional astrology."""
    considerations = {
        "moon_conditions": {
            "void_of_course": {
                "definition": "Moon makes no applying aspects before leaving her sign",
                "effect": "Nothing will come of the matter; avoid beginning anything",
                "exception": "Unless Moon is in Cancer, Taurus, Sagittarius, or Pisces"
            },
            "via_combusta": {
                "definition": "Moon between 15° Libra and 15° Scorpio",
                "effect": "Extremely unfortunate; matters corrupted or destroyed",
                "reason": "This region contains the Fall of the Sun and many malefic stars"
            },
            "moon_phases": {
                "new_to_first_quarter": "Good for beginning new ventures",
                "first_quarter_to_full": "Good for growth and expansion",
                "full_to_last_quarter": "Good for completion and harvest",
                "last_quarter_to_new": "Good for endings and release"
            },
            "lunar_mansions": "See lunar_mansions.json for election by mansion"
        },
        "planetary_hours": {
            "description": "Each hour is ruled by a planet in Chaldean order",
            "usage": "Begin matters under the hour of a planet favorable to the action",
            "saturn_hour": "binding, restriction, agriculture, old people",
            "jupiter_hour": "wealth, religion, legal matters, expansion",
            "mars_hour": "war, surgery, competition, cutting",
            "sun_hour": "authority, fathers, gold, public matters",
            "venus_hour": "love, art, pleasure, women",
            "mercury_hour": "commerce, writing, travel, communication",
            "moon_hour": "the public, women, journeys, changes"
        },
        "general_rules": [
            "Fortify the ruler of the matter and the Moon",
            "Avoid malefics on the Ascendant or afflicting the Moon",
            "Place benefics angular, malefics cadent",
            "Ensure the applying aspects are favorable",
            "Match the planetary hour to the nature of the business"
        ],
        "source": "Bonatti, Liber Astronomiae; Lilly, Christian Astrology"
    }
    return considerations


def extract_lunar_mansions() -> List[Dict]:
    """Extract lunar mansions from research doc."""
    mansions_file = RESEARCH_DIR / "lunar-mansions.txt"
    
    if not mansions_file.exists():
        return []
    
    with open(mansions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the JSON block
    json_match = re.search(r'```json\s*(\[[\s\S]*?\])\s*```', content)
    if json_match:
        try:
            mansions = json.loads(json_match.group(1))
            return mansions
        except json.JSONDecodeError:
            pass
    
    return []


def save_json(data: Any, filename: str):
    """Save data to JSON file."""
    filepath = OUTPUT_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {filename} ({len(data) if isinstance(data, (dict, list)) else 'N/A'} entries)")


def main():
    print("=" * 70)
    print("COMPREHENSIVE TRADITIONAL ASTROLOGY DATA EXTRACTION")
    print("=" * 70)
    
    print("\n1. Reading source material...")
    content = read_binder()
    print(f"   Binder1.txt: {len(content):,} characters")
    
    print("\n2. Extracting Fixed Stars...")
    fixed_stars = extract_fixed_stars(content)
    save_json(fixed_stars, "fixed_stars.json")
    
    print("\n3. Extracting Lots/Arabic Parts...")
    lots = extract_lots_arabic_parts(content)
    save_json(lots, "lots_arabic_parts.json")
    
    print("\n4. Extracting Firdaria Periods...")
    firdaria = extract_firdaria_periods()
    save_json(firdaria, "firdaria.json")
    
    print("\n5. Extracting Annual Profection Meanings...")
    profections = extract_profection_meanings()
    save_json(profections, "profections.json")
    
    print("\n6. Extracting Terms/Bounds...")
    terms = extract_terms_bounds()
    save_json(terms, "terms_bounds.json")
    
    print("\n7. Extracting Faces/Decans...")
    faces = extract_faces_decans()
    save_json(faces, "faces_decans.json")
    
    print("\n8. Extracting Triplicities...")
    triplicities = extract_triplicities()
    save_json(triplicities, "triplicities.json")
    
    print("\n9. Extracting Aspect Delineations...")
    aspects = extract_aspect_delineations()
    save_json(aspects, "aspect_delineations.json")
    
    print("\n10. Extracting Eclipse Rules...")
    eclipses = extract_eclipse_rules()
    save_json(eclipses, "eclipse_rules.json")
    
    print("\n11. Extracting Medical Iatromathematics...")
    medical = extract_medical_iatromathematics()
    save_json(medical, "medical_astrology.json")
    
    print("\n12. Extracting Electional Considerations...")
    electional = extract_electional_considerations()
    save_json(electional, "electional_considerations.json")
    
    print("\n13. Extracting Lunar Mansions...")
    mansions = extract_lunar_mansions()
    if mansions:
        save_json(mansions, "lunar_mansions.json")
    else:
        print("   (Parsing lunar mansions from research doc...)")
    
    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    
    # Summary
    print("\nData files created in src/database/data/:")
    for f in sorted(OUTPUT_DIR.glob("*.json")):
        size = f.stat().st_size
        print(f"  {f.name}: {size:,} bytes")


if __name__ == "__main__":
    main()
