

from .dignities import DignityCalculator
from .models import Chart, PlanetName, Sign
from .reference_data import DOMICILES


class TemperamentEngine:
    """
    Implements William Lilly's method for calculating Temperament (Christian Astrology, 1647).
    Analyzes the balance of Hot, Cold, Moist, and Dry qualities in a nativity.
    """

    QUALITIES = {
        "FIRE": {"Hot": 1, "Dry": 1, "Cold": 0, "Moist": 0},
        "EARTH": {"Hot": 0, "Dry": 1, "Cold": 1, "Moist": 0},
        "AIR": {"Hot": 1, "Dry": 0, "Cold": 0, "Moist": 1},
        "WATER": {"Hot": 0, "Dry": 0, "Cold": 1, "Moist": 1},
    }

    SEASONS = {
        "Spring": {"Hot": 1, "Moist": 1, "Cold": 0, "Dry": 0},  # Sun in Ari, Tau, Gem
        "Summer": {"Hot": 1, "Dry": 1, "Cold": 0, "Moist": 0},  # Sun in Can, Leo, Vir
        "Autumn": {"Cold": 1, "Dry": 1, "Hot": 0, "Moist": 0},  # Sun in Lib, Sco, Sag
        "Winter": {"Cold": 1, "Moist": 1, "Hot": 0, "Dry": 0},  # Sun in Cap, Aqu, Pis
    }

    MOON_PHASES = {
        "New to First Quarter": {"Hot": 1, "Moist": 1, "Cold": 0, "Dry": 0},
        "First Quarter to Full": {"Hot": 1, "Dry": 1, "Cold": 0, "Moist": 0},
        "Full to Last Quarter": {"Cold": 1, "Dry": 1, "Hot": 0, "Moist": 0},
        "Last Quarter to New": {"Cold": 1, "Moist": 1, "Hot": 0, "Dry": 0},
    }

    # Inherent planetary natures per Lilly, Christian Astrology (1647), pp. 57-83.
    # Each planet contributes its own temperamental nature to the tally.
    PLANET_NATURES = {
        PlanetName.SATURN: {"Hot": 0, "Cold": 1, "Moist": 0, "Dry": 1},
        PlanetName.JUPITER: {"Hot": 1, "Cold": 0, "Moist": 1, "Dry": 0},
        PlanetName.MARS: {"Hot": 1, "Cold": 0, "Moist": 0, "Dry": 1},
        PlanetName.SUN: {"Hot": 1, "Cold": 0, "Moist": 0, "Dry": 1},
        PlanetName.VENUS: {"Hot": 0, "Cold": 1, "Moist": 1, "Dry": 0},
        PlanetName.MERCURY: {
            "Hot": 0,
            "Cold": 0,
            "Moist": 0,
            "Dry": 0,
        },  # Variable; takes sign nature
        PlanetName.MOON: {"Hot": 0, "Cold": 1, "Moist": 1, "Dry": 0},
    }

    @staticmethod
    def get_element_qualities(sign: Sign):
        element = DignityCalculator.ZODIAC_ELEMENTS[sign]
        return TemperamentEngine.QUALITIES[element]

    @staticmethod
    def calculate_temperament(chart: Chart) -> dict:
        tally = {"Hot": 0, "Cold": 0, "Moist": 0, "Dry": 0}
        details = []

        # 1. Ascendant Sign
        asc_sign_idx = int(chart.ascendant / 30) % 12
        asc_sign = list(Sign)[asc_sign_idx]
        asc_qual = TemperamentEngine.get_element_qualities(asc_sign)
        TemperamentEngine._add_qualities(tally, asc_qual)
        details.append(f"Ascendant in {asc_sign.value}: +{asc_qual}")

        # 2. Ascendant Ruler
        asc_ruler_name = DOMICILES[asc_sign]  # Correct lookup: Sign -> PlanetName
        asc_ruler = next((p for p in chart.planets if p.name == asc_ruler_name), None)
        if asc_ruler:
            ruler_qual = TemperamentEngine.get_element_qualities(asc_ruler.sign)
            TemperamentEngine._add_qualities(tally, ruler_qual)
            details.append(
                f"Asc Ruler ({asc_ruler_name.value}) in {asc_ruler.sign.value}: +{ruler_qual}"
            )

        # 3. Moon Sign
        moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
        moon_qual = TemperamentEngine.get_element_qualities(moon.sign)
        TemperamentEngine._add_qualities(tally, moon_qual)
        details.append(f"Moon in {moon.sign.value}: +{moon_qual}")

        # 4. Moon Phase
        sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
        phase_angle = (moon.longitude - sun.longitude) % 360
        phase_name, phase_qual = TemperamentEngine._get_moon_phase_qualities(
            phase_angle
        )
        TemperamentEngine._add_qualities(tally, phase_qual)
        details.append(f"Moon Phase ({phase_name}): +{phase_qual}")

        # 5. Season (Sun Sign)
        season_name, season_qual = TemperamentEngine._get_season_qualities(sun.sign)
        TemperamentEngine._add_qualities(tally, season_qual)
        details.append(f"Season ({season_name}): +{season_qual}")

        # Keep track of which planets have a stake in the temperament
        significant_planets = set()
        if asc_ruler:
            significant_planets.add(asc_ruler.name)
        significant_planets.add(PlanetName.MOON)

        # 6. Planets aspecting Moon or Ascendant (sign element contribution)
        # Lilly adds planets aspecting Moon/Asc as temperament modifiers.
        for p in chart.planets:
            if p.name in [
                PlanetName.NORTH_NODE,
                PlanetName.SOUTH_NODE,
                PlanetName.URANUS,
                PlanetName.NEPTUNE,
                PlanetName.PLUTO,
            ]:
                continue

            # Aspect to Moon
            if p.name not in [
                PlanetName.MOON,
                PlanetName.SUN,
            ]:  # Sun handled softly via Moon Phase and Season
                diff = abs(p.longitude - moon.longitude) % 360
                dist = diff if diff <= 180 else 360 - diff
                if (
                    dist <= 10
                    or abs(dist - 60) <= 8
                    or abs(dist - 90) <= 8
                    or abs(dist - 120) <= 8
                    or abs(dist - 180) <= 10
                ):
                    p_qual = TemperamentEngine.get_element_qualities(p.sign)
                    TemperamentEngine._add_qualities(tally, p_qual)
                    details.append(f"Planet {p.name.value} aspecting Moon: +{p_qual}")
                    significant_planets.add(p.name)

            # Aspect to Ascendant
            diff_asc = abs(p.longitude - chart.ascendant) % 360
            dist_asc = diff_asc if diff_asc <= 180 else 360 - diff_asc
            if (
                dist_asc <= 10
                or abs(dist_asc - 60) <= 8
                or abs(dist_asc - 90) <= 8
                or abs(dist_asc - 120) <= 8
                or abs(dist_asc - 180) <= 10
            ):
                if p.name != PlanetName.SUN:  # Sun sign handled in Season step
                    p_qual_asc = TemperamentEngine.get_element_qualities(p.sign)
                    TemperamentEngine._add_qualities(tally, p_qual_asc)
                    details.append(
                        f"Planet {p.name.value} aspecting Ascendant: +{p_qual_asc}"
                    )
                significant_planets.add(p.name)

        # 7. Inherent Planetary Natures (Lilly, CA pp. 57-83)
        # Significant = Ascendant ruler, Moon, and planets aspecting Moon/Asc.
        for pname in significant_planets:
            p_nature = TemperamentEngine.PLANET_NATURES.get(pname)
            if p_nature and any(v > 0 for v in p_nature.values()):
                TemperamentEngine._add_qualities(tally, p_nature)
                details.append(f"Planet {pname.value} inherent nature: +{p_nature}")

        # Lilly's Calculation: Net Balance
        net_hot = tally["Hot"] - tally["Cold"]
        net_moist = tally["Moist"] - tally["Dry"]

        # Determine Temperament
        primary = "Balanced"
        if net_hot > 0 and net_moist > 0:
            primary = "Sanguine (Hot/Moist)"
        elif net_hot > 0 and net_moist < 0:
            primary = "Choleric (Hot/Dry)"
        elif net_hot < 0 and net_moist < 0:
            primary = "Melancholic (Cold/Dry)"
        elif net_hot < 0 and net_moist > 0:
            primary = "Phlegmatic (Cold/Moist)"

        # Handle "Compound" cases roughly
        # If one value is near 0, it's a mix.

        return {
            "primary_temperament": primary,
            "scores": tally,
            "net_balance": {"Hot_vs_Cold": net_hot, "Moist_vs_Dry": net_moist},
            "breakdown": details,
        }

    @staticmethod
    def _add_qualities(tally, current):
        for k in tally:
            tally[k] += current.get(k, 0)

    @staticmethod
    def _get_moon_phase_qualities(angle):
        if 0 <= angle < 90:
            return "New-1stQ", TemperamentEngine.MOON_PHASES["New to First Quarter"]
        elif 90 <= angle < 180:
            return "1stQ-Full", TemperamentEngine.MOON_PHASES["First Quarter to Full"]
        elif 180 <= angle < 270:
            return "Full-LastQ", TemperamentEngine.MOON_PHASES["Full to Last Quarter"]
        else:
            return "LastQ-New", TemperamentEngine.MOON_PHASES["Last Quarter to New"]

    @staticmethod
    def _get_season_qualities(sun_sign: Sign):
        # Seasons by Tropical Zodiac
        if sun_sign in [Sign.ARIES, Sign.TAURUS, Sign.GEMINI]:
            return "Spring", TemperamentEngine.SEASONS["Spring"]
        if sun_sign in [Sign.CANCER, Sign.LEO, Sign.VIRGO]:
            return "Summer", TemperamentEngine.SEASONS["Summer"]
        if sun_sign in [Sign.LIBRA, Sign.SCORPIO, Sign.SAGITTARIUS]:
            return "Autumn", TemperamentEngine.SEASONS["Autumn"]
        return "Winter", TemperamentEngine.SEASONS["Winter"]
