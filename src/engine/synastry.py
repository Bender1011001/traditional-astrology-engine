from typing import Any, Dict

from .lots import calculate_lot_position
from .models import Chart, LotName, PlanetName, Sect


class SynastryEngine:
    ORB_SUCCESS = 3.0  # Tight orb for "Structural Fit"

    @staticmethod
    def get_sect(chart: Chart) -> Sect:
        # Simple sect check: Sun above/below horizon
        return Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

    @staticmethod
    def check_conjunction(pos1: float, pos2: float, orb: float = 3.5) -> bool:
        diff = abs(pos1 - pos2)
        if diff > 180:
            diff = 360 - diff
        return diff <= orb

    def analyze_structural_fit(
        self, person_a: Chart, person_b: Chart
    ) -> Dict[str, Any]:
        sect_a = self.get_sect(person_a)
        sect_b = self.get_sect(person_b)

        # Calculate key lots
        fortune_a = calculate_lot_position(person_a, LotName.FORTUNE, sect_a)
        spirit_a = calculate_lot_position(person_a, LotName.SPIRIT, sect_a)

        fortune_b = calculate_lot_position(person_b, LotName.FORTUNE, sect_b)
        spirit_b = calculate_lot_position(person_b, LotName.SPIRIT, sect_b)

        # 1. Dependency Audits (Planets on Lots)
        dependencies = []

        # Check Person A's planets on Person B's Lot of Fortune
        for planet in person_a.planets:
            if self.check_conjunction(planet.longitude, fortune_b):
                delineation = self._get_planet_on_fortune_delineation(
                    "Person A", planet.name, "Person B"
                )
                dependencies.append(
                    {
                        "type": "Planet on Fortune",
                        "subject": "Person A",
                        "planet": planet.name.value,
                        "target": "Person B",
                        "delineation": delineation,
                    }
                )

        # Check Person B's planets on Person A's Lot of Fortune
        for planet in person_b.planets:
            if self.check_conjunction(planet.longitude, fortune_a):
                delineation = self._get_planet_on_fortune_delineation(
                    "Person B", planet.name, "Person A"
                )
                dependencies.append(
                    {
                        "type": "Planet on Fortune",
                        "subject": "Person B",
                        "planet": planet.name.value,
                        "target": "Person A",
                        "delineation": delineation,
                    }
                )

        # 2. Shared Fate (Spirit Handshake)
        shared_fate = []
        if self.check_conjunction(spirit_a, spirit_b):
            shared_fate.append(
                {
                    "type": "Spirit Handshake",
                    "description": "Your Lots of Spirit (Career/Will) are aligned. This indicates a shared destiny or complementary life paths.",
                    "delineation": "The 'Handshake' between charts: You are moving in the same direction, with shared intentionality.",
                }
            )

        # Check if Spirit of one is on Fortune of another (Materializing the Will)
        if self.check_conjunction(spirit_a, fortune_b):
            shared_fate.append(
                {
                    "type": "Will to Matter",
                    "description": "Person A's Spirit is on Person B's Fortune.",
                    "delineation": "Person A's actions and will directly impact Person B's material well-being and health.",
                }
            )
        if self.check_conjunction(spirit_b, fortune_a):
            shared_fate.append(
                {
                    "type": "Will to Matter",
                    "description": "Person B's Spirit is on Person A's Fortune.",
                    "delineation": "Person B's actions and will directly impact Person A's material well-being and health.",
                }
            )

        return {
            "dependency_audits": dependencies,
            "shared_fate": shared_fate,
            "overall_assessment": (
                "Structural Fit"
                if (len(dependencies) > 0 or len(shared_fate) > 0)
                else "Individual Journeys"
            ),
        }

    def _get_planet_on_fortune_delineation(
        self, subj: str, planet: PlanetName, target: str
    ) -> str:
        delineations = {
            PlanetName.SUN: f"{subj}'s Sun clarifies and illuminates {target}'s Lot of Fortune, bringing vital energy to their health and resources.",
            PlanetName.MOON: f"{subj}'s Moon provides emotional support and fluctuation to {target}'s Lot of Fortune.",
            PlanetName.MERCURY: f"{subj}'s Mercury brings intelligence and active communication to {target}'s financial and physical state.",
            PlanetName.VENUS: f"{subj}'s Venus brings ease, beauty, and benefit to {target}'s resources.",
            PlanetName.MARS: f"{subj}'s Mars may bring conflict, heat, or intensive effort to {target}'s Lot of Fortune—potential for 'feverish' costs.",
            PlanetName.JUPITER: f"{subj}'s Jupiter is a major stabilizer and wealth-bringer to {target}'s physical life.",
            PlanetName.SATURN: f"{subj}'s Saturn is on {target}'s Lot of Fortune—this person will stabilize your finances but may feel like a 'heavy' influence on your health.",
        }
        return delineations.get(
            planet, f"{subj}'s {planet.value} impacts {target}'s Lot of Fortune."
        )
