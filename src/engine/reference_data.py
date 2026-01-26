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

# Triplicity Lords (Dorothean/Lilly - using Lilly's simplified commonly used ones or Dorothean? 
# Only 1 ruler needed to score +3? Or does it need to be the primary ruler of the sect?
# Lilly usually gives +3 if the planet is a triplicity ruler of the sign in the correct sect.
# Let's assume generic Triplicity Rulers list.
# Fire: Sun (Day), Jupiter (Night), Saturn (Participating)
# Earth: Venus (Day), Moon (Night), Mars (Participating)
# Air: Saturn (Day), Mercury (Night), Jupiter (Participating)
# Water: Venus (Day), Mars (Night), Moon (Participating)
# NOTE: User says "Implement the Weighted Scoring System (Ibn Ezra/Lilly)".
TRIPLICITY_RULERS = {
    "Fire": {Sect.DAY: PlanetName.SUN, Sect.NIGHT: PlanetName.JUPITER},
    "Earth": {Sect.DAY: PlanetName.VENUS, Sect.NIGHT: PlanetName.MOON},
    "Air": {Sect.DAY: PlanetName.SATURN, Sect.NIGHT: PlanetName.MERCURY},
    "Water": {Sect.DAY: PlanetName.VENUS, Sect.NIGHT: PlanetName.MARS},
}

SIGN_ELEMENTS = {
    Sign.ARIES: "Fire", Sign.LEO: "Fire", Sign.SAGITTARIUS: "Fire",
    Sign.TAURUS: "Earth", Sign.VIRGO: "Earth", Sign.CAPRICORN: "Earth",
    Sign.GEMINI: "Air", Sign.LIBRA: "Air", Sign.AQUARIUS: "Air",
    Sign.CANCER: "Water", Sign.SCORPIO: "Water", Sign.PISCES: "Water",
}

# Egyptian Terms (Bounds) - Upper bound degree per sign
# Format: Sign -> List of (Planet, UpperDegree)
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

# Faces (Chaldean Order) - 10 degrees each
# Signs in standard order: Aries to Pisces
# Rulers cycle: Mars, Sun, Venus, Mercury, Moon, Saturn, Jupiter...
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

# Alcocoden Planetary Years (Lesser, Mean, Greater)
# Source: Binder1_part_018.txt
PLANETARY_YEARS = {
    PlanetName.SATURN: {"lesser": 30, "mean": 43.5, "greater": 57},
    PlanetName.JUPITER: {"lesser": 12, "mean": 45.5, "greater": 79},
    PlanetName.MARS: {"lesser": 15, "mean": 40.5, "greater": 66},
    PlanetName.SUN: {"lesser": 19, "mean": 69.5, "greater": 120},
    PlanetName.VENUS: {"lesser": 8, "mean": 45, "greater": 82},
    PlanetName.MERCURY: {"lesser": 20, "mean": 48, "greater": 76},
    PlanetName.MOON: {"lesser": 25, "mean": 66.5, "greater": 108},
}
