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
