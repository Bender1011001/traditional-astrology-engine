from datetime import datetime
from .models import Chart, PlanetName, Sign, Planet
from .dignities import DignityCalculator
from .reference_data import DOMICILES
import swisseph as swe

class Temperame