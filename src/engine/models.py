from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class Sect(Enum):
    DAY = "Day"
    NIGHT = "Night"


class PlanetName(Enum):
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"
    URANUS = "Uranus"
    NEPTUNE = "Neptune"
    PLUTO = "Pluto"
    NORTH_NODE = "North_Node"
    SOUTH_NODE = "South_Node"


class PlanetaryPhase(Enum):
    UNDER_BEAMS = "Under the Beams"
    COMBUST = "Combust"
    CAZIMI = "Cazimi"
    HELIACAL_RISING = "Heliacal Rising"
    HELIACAL_SETTING = "Heliacal Setting"
    MORNING_FIRST = "Morning First"  # Same as heliacal rising for superiors
    EVENING_FIRST = "Evening First"
    EVENING_LAST = "Evening Last"  # Same as heliacal setting for superiors
    MORNING_LAST = "Morning Last"
    STATION_RETROGRADE = "Station Retrograde"
    STATION_DIRECT = "Station Direct"
    OPPOSITION = "Opposition"  # Acronychal Rising
    FREE = "Free"


class SolarProximity(Enum):
    CAZIMI = "Cazimi"
    COMBUST = "Combust"
    UNDER_BEAMS = "Under the Beams"
    FREE = "Free"


class Sign(Enum):
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"


@dataclass
class Planet:
    name: PlanetName
    longitude: float  # 0-360 degrees
    latitude: float = 0.0
    speed: float = 0.0
    altitude: float = 0.0

    # Phasis Data
    phase: Optional[PlanetaryPhase] = None
    solar_proximity: Optional[SolarProximity] = None
    is_oriental: bool = False
    in_chariot: bool = False
    is_visible: bool = True

    @property
    def sign(self) -> Sign:
        index = int(self.longitude / 30) % 12
        return list(Sign)[index]

    @property
    def degree_in_sign(self) -> float:
        return self.longitude % 30

    @property
    def is_retrograde(self) -> bool:
        return self.speed < 0


@dataclass
class Chart:
    sun_altitude: float  # Degrees above/below horizon
    planets: List[Planet]
    ascendant: float  # 0-360
    mc: float = 0.0
    north_node: float = 0.0
    south_node: float = 0.0
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    jd: Optional[float] = None
    houses: Optional[Dict[int, float]] = None
    house_system: Optional[str] = None


class LotName(Enum):
    FORTUNE = "Fortune"
    SPIRIT = "Spirit"
    EROS = "Eros"
    NECESSITY = "Necessity"
    COURAGE = "Courage"
    VICTORY = "Victory"
    NEMESIS = "Nemesis"
    DEBT = "Debt"
    THEFT = "Theft"
    ACCUSATION = "Accusation"
    FATHER = "Father"
    MOTHER = "Mother"
    MARRIAGE_MEN = "Marriage_Men"
    MARRIAGE_WOMEN = "Marriage_Women"
    CHILDREN = "Children"
    SIBLINGS = "Siblings"
    FRIENDS = "Friends"
    ENEMIES = "Enemies"
    SICKNESS = "Sickness"
    ASSETS = "Assets"
    DEATH = "Death"
    JOURNEYS = "Journeys"
    COMMERCE = "Commerce"
    BOLDNESS = "Boldness"
    SUCCESS = "Success"
    MISFORTUNE = "Misfortune"
    LIFE = "Life"
    WISDOM = "Wisdom"
    ART = "Art"
    BATTLES = "Battles"
    FOUNDATION = "Foundation"
    BASIS = "Basis"
    EXALTATION = "Exaltation"
    WHEAT = "Wheat"
    BARLEY = "Barley"
    RICE = "Rice"
    LENTILS = "Lentils"
    POVERTY = "Poverty"
    CAUSATIVE_PLACE = "Causative_Place"
