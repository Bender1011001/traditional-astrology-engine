from .models import PlanetName, Sign, Sect

# Planet Sects (Nature)
PLANET_SECTS = {
    PlanetName.SUN: Sect.DAY,
    PlanetName.JUPITER: Sect.DAY,
    PlanetName.SATURN: Sect.DAY,
    PlanetName.MOON: Sect.NIGHT,
    PlanetName.VENUS: Sect.NIGHT,
    PlanetName.MARS: Sect.NIGHT,
    PlanetName.MERCURY: None, # Adaptive / Neutral
}

# Domiciles (Rulerships)
DOMICILES = {
    Sign.ARIES: PlanetName.MARS,
    Sign.TAURUS: PlanetName.VENUS,
    Sign.GEMINI: PlanetName.MERCURY,
    Sign.CANCER: PlanetName.MOON,
    Sign.LEO: PlanetName.SUN,
    Sign.VIRGO: PlanetName.MERCURY,
    Sign.LIBRA: PlanetName.VENUS,
    Sign.SCORPIO: PlanetName.MARS,
    Sign.SAGITTARIUS: PlanetName.JUPITER,
    Sign.CAPRICORN: PlanetName.SATURN,
    Sign.AQUARIUS: PlanetName.SATURN,
    Sign.PISCES: PlanetName.JUPITER,
}

# Exaltations
EXALTATIONS = {
    Sign.ARIES: PlanetName.SUN,
    Sign.TAURUS: PlanetName.MOON,
    Sign.CANCER: PlanetName.JUPITER,
    Sign.VIRGO: PlanetName.MERCURY,
    Sign.LIBRA: PlanetName.SATURN,
    Sign.CAPRICORN: PlanetName.MARS,
    Sign.PISCES: PlanetName.VENUS,
}

# Falls (Opposite to Exaltation)
FALLS = {
    Sign.LIBRA: PlanetName.SUN,
    Sign.SCORPIO: PlanetName.MOON,
    Sign.CAPRICORN: PlanetName.JUPITER,
    Sign.PISCES: PlanetName.MERCURY,
    Sign.ARIES: PlanetName.SATURN,
    Sign.CANCER: PlanetName.MARS,
    Sign.VIRGO: PlanetName.VENUS,
}

# Detriments (Opposite to Domicile)
DETRIMENTS = {
    Sign.LIBRA: PlanetName.MARS,
    Sign.SCORPIO: PlanetName.VENUS,
    Sign.SAGITTARIUS: PlanetName.MERCURY,
    Sign.CAPRICORN: PlanetName.MOON,
    Sign.AQUARIUS: PlanetName.SUN,
    Sign.PISCES: PlanetName.MERCURY,
    Sign.ARIES: PlanetName.VENUS,
    Sign.TAURUS: PlanetName.MARS,
    Sign.GEMINI: PlanetName.JUPITER,
    Sign.CANCER: PlanetName.SATURN,
    Sign.LEO: PlanetName.SATURN,
    Sign.VIRGO: PlanetName.JUPITER,
}

# Dorothean Triplicity (Bonatti Mode)
# Format: {Element: (Day, Night, Participant)}
DOROTHEAN_TRIPLICITY = {
    "Fire": (PlanetName.SUN, PlanetName.JUPITER, PlanetName.SATURN),
    "Earth": (PlanetName.VENUS, PlanetName.MOON, PlanetName.MARS),
    "Air": (PlanetName.SATURN, PlanetName.MERCURY, PlanetName.JUPITER),
    "Water": (PlanetName.VENUS, PlanetName.MARS, PlanetName.MOON)
}

# Ptolemaic Triplicity (Lilly Mode)
# Format: {Element: (Day, Night)} - No participant usually used in this mode
PTOLEMAIC_TRIPLICITY = {
    "Fire": (PlanetName.SUN, PlanetName.JUPITER),
    "Earth": (PlanetName.VENUS, PlanetName.MOON),
    "Air": (PlanetName.SATURN, PlanetName.MERCURY),
    "Water": (PlanetName.MARS, PlanetName.MARS)
}

# Legacy Export for backward compatibility (defaults to Dorothean in original code? No, original had dict with Sect keys)
# The original code had: "Fire": {Sect.DAY: PlanetName.SUN, Sect.NIGHT: PlanetName.JUPITER}, which looked like Ptolemaic actually, but with limited keys.
# Actually previously it was referenced as TRIPLICITY_RULERS in dignities.py as tuple (Day, Night, Part).
# Let's keep a generic TRIPLICITY_RULERS pointing to Dorothean as default if needed, but Receptions will pick specific.
TRIPLICITY_RULERS = DOROTHEAN_TRIPLICITY

SIGN_ELEMENTS = {
    Sign.ARIES: "Fire", Sign.LEO: "Fire", Sign.SAGITTARIUS: "Fire",
    Sign.TAURUS: "Earth", Sign.VIRGO: "Earth", Sign.CAPRICORN: "Earth",
    Sign.GEMINI: "Air", Sign.LIBRA: "Air", Sign.AQUARIUS: "Air",
    Sign.CANCER: "Water", Sign.SCORPIO: "Water", Sign.PISCES: "Water",
}

# Egyptian Terms (Bounds)
EGYPTIAN_TERMS = {
    Sign.ARIES: [(PlanetName.JUPITER, 6), (PlanetName.VENUS, 12), (PlanetName.MERCURY, 20), (PlanetName.MARS, 25), (PlanetName.SATURN, 30)],
    Sign.TAURUS: [(PlanetName.VENUS, 8), (PlanetName.MERCURY, 14), (PlanetName.JUPITER, 22), (PlanetName.SATURN, 27), (PlanetName.MARS, 30)],
    Sign.GEMINI: [(PlanetName.MERCURY, 6), (PlanetName.JUPITER, 12), (PlanetName.VENUS, 17), (PlanetName.MARS, 24), (PlanetName.SATURN, 30)],
    Sign.CANCER: [(PlanetName.MARS, 7), (PlanetName.VENUS, 13), (PlanetName.MERCURY, 19), (PlanetName.JUPITER, 26), (PlanetName.SATURN, 30)],
    Sign.LEO: [(PlanetName.JUPITER, 6), (PlanetName.VENUS, 11), (PlanetName.SATURN, 18), (PlanetName.MERCURY, 24), (PlanetName.MARS, 30)],
    Sign.VIRGO: [(PlanetName.MERCURY, 7), (PlanetName.VENUS, 17), (PlanetName.JUPITER, 21), (PlanetName.MARS, 28), (PlanetName.SATURN, 30)],
    Sign.LIBRA: [(PlanetName.SATURN, 6), (PlanetName.MERCURY, 14), (PlanetName.JUPITER, 21), (PlanetName.VENUS, 28), (PlanetName.MARS, 30)],
    Sign.SCORPIO: [(PlanetName.MARS, 7), (PlanetName.VENUS, 11), (PlanetName.MERCURY, 19), (PlanetName.JUPITER, 24), (PlanetName.SATURN, 30)],
    Sign.SAGITTARIUS: [(PlanetName.JUPITER, 12), (PlanetName.VENUS, 17), (PlanetName.MERCURY, 21), (PlanetName.SATURN, 26), (PlanetName.MARS, 30)],
    Sign.CAPRICORN: [(PlanetName.MERCURY, 7), (PlanetName.JUPITER, 14), (PlanetName.VENUS, 22), (PlanetName.SATURN, 26), (PlanetName.MARS, 30)],
    Sign.AQUARIUS: [(PlanetName.MERCURY, 7), (PlanetName.VENUS, 13), (PlanetName.JUPITER, 20), (PlanetName.MARS, 25), (PlanetName.SATURN, 30)],
    Sign.PISCES: [(PlanetName.VENUS, 12), (PlanetName.JUPITER, 16), (PlanetName.MERCURY, 19), (PlanetName.MARS, 28), (PlanetName.SATURN, 30)],
}

# Ptolemaic Terms (Lilly Mode)
PTOLEMAIC_TERMS = {
    Sign.ARIES: [(PlanetName.JUPITER, 6), (PlanetName.VENUS, 14), (PlanetName.MERCURY, 21), (PlanetName.MARS, 26), (PlanetName.SATURN, 30)],
    Sign.TAURUS: [(PlanetName.VENUS, 8), (PlanetName.MERCURY, 15), (PlanetName.JUPITER, 22), (PlanetName.SATURN, 26), (PlanetName.MARS, 30)],
    Sign.GEMINI: [(PlanetName.MERCURY, 7), (PlanetName.JUPITER, 14), (PlanetName.VENUS, 21), (PlanetName.SATURN, 25), (PlanetName.MARS, 30)],
    Sign.CANCER: [(PlanetName.MARS, 6), (PlanetName.JUPITER, 13), (PlanetName.MERCURY, 20), (PlanetName.VENUS, 27), (PlanetName.SATURN, 30)],
    Sign.LEO: [(PlanetName.JUPITER, 6), (PlanetName.VENUS, 13), (PlanetName.SATURN, 19), (PlanetName.MERCURY, 25), (PlanetName.MARS, 30)],
    Sign.VIRGO: [(PlanetName.MERCURY, 7), (PlanetName.VENUS, 13), (PlanetName.JUPITER, 18), (PlanetName.SATURN, 24), (PlanetName.MARS, 30)],
    Sign.LIBRA: [(PlanetName.SATURN, 6), (PlanetName.VENUS, 11), (PlanetName.JUPITER, 19), (PlanetName.MERCURY, 24), (PlanetName.MARS, 30)],
    Sign.SCORPIO: [(PlanetName.MARS, 6), (PlanetName.VENUS, 14), (PlanetName.JUPITER, 21), (PlanetName.MERCURY, 27), (PlanetName.SATURN, 30)],
    Sign.SAGITTARIUS: [(PlanetName.JUPITER, 8), (PlanetName.VENUS, 14), (PlanetName.MERCURY, 19), (PlanetName.SATURN, 25), (PlanetName.MARS, 30)],
    Sign.CAPRICORN: [(PlanetName.VENUS, 6), (PlanetName.MERCURY, 12), (PlanetName.JUPITER, 19), (PlanetName.MARS, 25), (PlanetName.SATURN, 30)],
    Sign.AQUARIUS: [(PlanetName.SATURN, 6), (PlanetName.MERCURY, 12), (PlanetName.VENUS, 20), (PlanetName.JUPITER, 25), (PlanetName.MARS, 30)],
    Sign.PISCES: [(PlanetName.VENUS, 8), (PlanetName.JUPITER, 14), (PlanetName.MERCURY, 20), (PlanetName.MARS, 26), (PlanetName.SATURN, 30)],
}

# Chaldean Terms (Babylonian Order) - 8, 7, 6, 5, 4 degrees
# Sequence: Jup, Ven, Sat, Mer, Mar (The standard planetary week order/descent)
CHALDEAN_TERMS = {
    Sign.ARIES: [(PlanetName.JUPITER, 8), (PlanetName.VENUS, 15), (PlanetName.SATURN, 21), (PlanetName.MERCURY, 26), (PlanetName.MARS, 30)],
    Sign.TAURUS: [(PlanetName.VENUS, 8), (PlanetName.SATURN, 15), (PlanetName.MERCURY, 21), (PlanetName.MARS, 26), (PlanetName.JUPITER, 30)],
    Sign.GEMINI: [(PlanetName.SATURN, 8), (PlanetName.MERCURY, 15), (PlanetName.MARS, 21), (PlanetName.JUPITER, 26), (PlanetName.VENUS, 30)],
    Sign.CANCER: [(PlanetName.MERCURY, 8), (PlanetName.MARS, 15), (PlanetName.JUPITER, 21), (PlanetName.VENUS, 26), (PlanetName.SATURN, 30)],
    Sign.LEO: [(PlanetName.MARS, 8), (PlanetName.JUPITER, 15), (PlanetName.VENUS, 21), (PlanetName.SATURN, 26), (PlanetName.MERCURY, 30)],
    Sign.VIRGO: [(PlanetName.JUPITER, 8), (PlanetName.VENUS, 15), (PlanetName.SATURN, 21), (PlanetName.MERCURY, 26), (PlanetName.MARS, 30)],
    Sign.LIBRA: [(PlanetName.VENUS, 8), (PlanetName.SATURN, 15), (PlanetName.MERCURY, 21), (PlanetName.MARS, 26), (PlanetName.JUPITER, 30)],
    Sign.SCORPIO: [(PlanetName.SATURN, 8), (PlanetName.MERCURY, 15), (PlanetName.MARS, 21), (PlanetName.JUPITER, 26), (PlanetName.VENUS, 30)],
    Sign.SAGITTARIUS: [(PlanetName.MERCURY, 8), (PlanetName.MARS, 15), (PlanetName.JUPITER, 21), (PlanetName.VENUS, 26), (PlanetName.SATURN, 30)],
    Sign.CAPRICORN: [(PlanetName.MARS, 8), (PlanetName.JUPITER, 15), (PlanetName.VENUS, 21), (PlanetName.SATURN, 26), (PlanetName.MERCURY, 30)],
    Sign.AQUARIUS: [(PlanetName.JUPITER, 8), (PlanetName.VENUS, 15), (PlanetName.SATURN, 21), (PlanetName.MERCURY, 26), (PlanetName.MARS, 30)],
    Sign.PISCES: [(PlanetName.VENUS, 8), (PlanetName.SATURN, 15), (PlanetName.MERCURY, 21), (PlanetName.MARS, 26), (PlanetName.JUPITER, 30)],
}

# Faces (Chaldean Order) - 10 degrees each
FACES_ORDER = [
    PlanetName.MARS, PlanetName.SUN, PlanetName.VENUS, # Aries
    PlanetName.MERCURY, PlanetName.MOON, PlanetName.SATURN, # Taurus
    PlanetName.JUPITER, PlanetName.MARS, PlanetName.SUN, # Gemini
    PlanetName.VENUS, PlanetName.MERCURY, PlanetName.MOON, # Cancer
    PlanetName.SATURN, PlanetName.JUPITER, PlanetName.MARS, # Leo
    PlanetName.SUN, PlanetName.VENUS, PlanetName.MERCURY, # Virgo
    PlanetName.MOON, PlanetName.SATURN, PlanetName.JUPITER, # Libra
    PlanetName.MARS, PlanetName.SUN, PlanetName.VENUS, # Scorpio
    PlanetName.MERCURY, PlanetName.MOON, PlanetName.SATURN, # Sagittarius
    PlanetName.JUPITER, PlanetName.MARS, PlanetName.SUN, # Capricorn
    PlanetName.VENUS, PlanetName.MERCURY, PlanetName.MOON, # Aquarius
    PlanetName.SATURN, PlanetName.JUPITER, PlanetName.MARS, # Pisces
]

PLANETARY_YEARS = {
    PlanetName.SATURN: {"lesser": 30, "mean": 43.5, "greater": 57},
    PlanetName.JUPITER: {"lesser": 12, "mean": 45.5, "greater": 79},
    PlanetName.MARS: {"lesser": 15, "mean": 40.5, "greater": 66},
    PlanetName.SUN: {"lesser": 19, "mean": 69.5, "greater": 120},
    PlanetName.VENUS: {"lesser": 8, "mean": 45, "greater": 82},
    PlanetName.MERCURY: {"lesser": 20, "mean": 48, "greater": 76},
    PlanetName.MOON: {"lesser": 25, "mean": 66.5, "greater": 108},
}

# Planetary Moieties (Half-Orbs) - Lilly CA p. 57
MOIETIES = {
    PlanetName.SATURN: 5.0,  # Orb 10 -> Moiety 5
    PlanetName.JUPITER: 4.5, # Orb 9 -> Moiety 4.5
    PlanetName.MARS: 3.5,    # Orb 7 (sometimes 7.30) -> Moiety 3.5
    PlanetName.SUN: 7.5,     # Orb 15 -> Moiety 7.5
    PlanetName.VENUS: 3.5,   # Orb 7 -> Moiety 3.5
    PlanetName.MERCURY: 3.5, # Orb 7 -> Moiety 3.5
    PlanetName.MOON: 6.0,    # Orb 12 -> Moiety 6
    PlanetName.URANUS: 2.5,  # Modern: 5 deg orb
    PlanetName.NEPTUNE: 2.5,
    PlanetName.PLUTO: 2.5,
    PlanetName.NORTH_NODE: 0.0,
    PlanetName.SOUTH_NODE: 0.0,
}

PLANET_ESSENCES = {
    PlanetName.SUN: "Sovereignty and Identity",
    PlanetName.MOON: "Emotional Synthesis and Adaptation",
    PlanetName.MERCURY: "Analytical Mastery and Communication",
    PlanetName.VENUS: "Harmony and Value Creation",
    PlanetName.MARS: "Strategic Action and Drive",
    PlanetName.JUPITER: "Expansion and Wisdom",
    PlanetName.SATURN: "Structural Integrity and Responsibility"
}

TERM_METHODS = {
    PlanetName.SUN: "Radiance and Authority",
    PlanetName.MOON: "Receptivity and Fluency",
    PlanetName.MERCURY: "Precision and Communication",
    PlanetName.VENUS: "Grace and Relatability",
    PlanetName.MARS: "Strategy and Fortitude",
    PlanetName.JUPITER: "Growth and Principles",
    PlanetName.SATURN: "Structure and Restraint"
}

RULE_SOURCE_MAP = {
    "Bonatti Consideration 5": ["Bonatti, Liber Astronomiae, Consideration 5 (Void of Course)"],
    "Bonatti Consideration 30": ["Bonatti, Liber Astronomiae, Consideration 30 (Planet at 29°)"],
    "Bonatti Consideration 141": ["Bonatti, Liber Astronomiae, Consideration 141 (Significator in Ascendant)"],
    "Via Combusta": ["Traditional doctrine (Lilly, Christian Astrology, p. 115)"],
    "Combustion": ["Traditional doctrine (Ptolemy, Tetrabiblos I.24; Lilly, CA, p. 113)"],
    "Besiegement": ["Traditional doctrine (Lilly, Christian Astrology, p. 114)"],
    "Antiscia": ["Firmicus Maternus, Mathesis II.30", "Lilly, CA, p. 90"],
    "Melothesia": ["Manilius, Astronomica IV", "Culpeper, English Physician"],
    "Sect/Hayz/Halb": ["Ptolemy, Tetrabiblos III.3", "Dorotheus, Carmen Astrologicum I.1"],
    "Universal Overdrive": ["Ptolemy, Tetrabiblos II.1"],
    "Universal Causation": ["Ptolemy, Tetrabiblos II.8"],
    "Mundane Rank 4 > Natal Particulars": ["Traditional mundane hierarchy (Ptolemy, Tetrabiblos II.3)"],
    "Aries Ingress": ["Traditional mundane ingress doctrine (Bonatti, Liber Astronomiae, VIII)"]
}
