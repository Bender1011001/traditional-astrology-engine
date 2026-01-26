from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

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
    
    @property
    def sign(self) -> Sign:
        index = int(self.longitude / 30) % 12
        return list(Sign)[index]
    
    @property
    def degree_in_sign(self) -> float:
        return self.longitude % 30

@dataclass
class Chart:
    sun_altitude: float # Degrees above/below horizon
    planets: List[Planet]
    ascendant: float # 0-360
    mc: float = 0.0
    north_node: float = 0.0 
    south_node: float = 0.0

class LotName(Enum):
    FORTUNE = "Fortune"
    SPIRIT = "Spirit"
    EROS = "Eros"
    NECESSITY = "Necessity"
    VICTORY = "Victory"
    FATHER = "Father"
    MOTHER = "Mother"
    COURAGE = "Courage"
    NEMESIS = "Nemesis"
