"""
Planetary remediation engine (deterministic correspondences + electional timing).

Turns the ad-hoc remediation prose into a sourced, structured layer the narrative
must cite. Built on the two-layer model requested in the source-map review:

  * a HISTORICAL layer that records the traditional correspondence faithfully
    (including items that are toxic or unsafe by modern standards), and
  * a SAFE / production layer that exposes only non-toxic, behavioural, or
    charitable substitutes for actual recommendations.

Correspondences are the stable Renaissance planetary set (Agrippa, Three Books of
Occult Philosophy, Bk I; standard alchemical metal/day assignments), cross-checked
against consolidated modern references. Planetary days and metals are canonical;
stones, colours, and incenses are the widely-attested traditional set.

ELECTIONAL TIMING: the engine specifies *when* to perform a remedy — the planet's
day and its planetary hour — and, if a lunar-mansion intent is supplied, ties the
act to the Moon's transit through that mansion. Computing the next concrete
date/time is left to the planetary-hours / electional layers; this engine emits
the rule + ingredients.

SAFETY: never recommend toxic metals (lead, quicksilver) or hazardous suffumigation
materials. `metal_historical` is provenance-only; `metal_safe` is what may be
suggested. All output is historical/symbolic and explicitly non-medical.
"""

from typing import Any, Dict, List, Optional

from .models import PlanetName, Sect

# Toxic / unsafe items recorded for provenance but never recommended.
_UNSAFE = {"lead", "quicksilver", "mercury (metal)"}

PLANETARY_CORRESPONDENCES: Dict[str, Dict[str, Any]] = {
    "Saturn": {
        "day": "Saturday",
        "hour_ruler": "Saturn",
        "qualities": "cold & dry; greater malefic",
        "metal_historical": "lead",  # toxic — provenance only
        "metal_safe": "pewter or dark iron substitute (do NOT use lead)",
        "stones": ["onyx", "jet", "obsidian", "hematite", "smoky quartz"],
        "colors": ["black", "dark grey", "indigo", "dark brown"],
        "incense": ["myrrh", "cypress", "patchouli"],
        "body": "bones, teeth, spleen, skin, the retentive faculty",
        "charitable_acts": [
            "service to the elderly, the poor, and the bereaved",
            "almsgiving and settling old debts or obligations",
            "voluntary simplicity, decluttering, and patient discipline (non-medical)",
        ],
        "direction": None,  # source-dependent (Picatrix varies); left null
    },
    "Jupiter": {
        "day": "Thursday",
        "hour_ruler": "Jupiter",
        "qualities": "hot & moist; greater benefic",
        "metal_historical": "tin",
        "metal_safe": "tin",
        "stones": ["sapphire", "lapis lazuli", "amethyst", "turquoise"],
        "colors": ["royal blue", "purple", "deep blue"],
        "incense": ["nutmeg", "clove", "cedar", "pine"],
        "body": "liver, blood, thighs, the nutritive growth",
        "charitable_acts": [
            "generosity, charity, and patronage of education or religion",
            "mentoring, teaching, and giving counsel",
            "acts of mercy, forgiveness, and reconciliation",
        ],
        "direction": None,
    },
    "Mars": {
        "day": "Tuesday",
        "hour_ruler": "Mars",
        "qualities": "hot & dry; lesser malefic",
        "metal_historical": "iron",
        "metal_safe": "iron or steel",
        "stones": ["garnet", "bloodstone", "red jasper", "carnelian"],
        "colors": ["red", "scarlet"],
        "incense": ["dragon's blood", "ginger", "pine"],
        "body": "muscles, gall, the left ear, the attractive faculty",
        "charitable_acts": [
            "vigorous exertion or exercise directed at a worthy goal (non-medical)",
            "protecting the vulnerable and acting with disciplined courage",
            "channeling anger into constructive, decisive work",
        ],
        "direction": None,
    },
    "Sun": {
        "day": "Sunday",
        "hour_ruler": "Sun",
        "qualities": "hot & dry; luminary of the day",
        "metal_historical": "gold",
        "metal_safe": "gold",
        "stones": ["amber", "ruby", "citrine", "sunstone", "tiger's eye"],
        "colors": ["gold", "yellow", "orange"],
        "incense": ["frankincense", "cinnamon", "bay laurel"],
        "body": "heart, vital spirit, the right eye",
        "charitable_acts": [
            "magnanimous leadership and honoring those in authority or one's father",
            "gratitude practices and generous public acts",
            "creative, heart-led work performed with integrity",
        ],
        "direction": None,
    },
    "Venus": {
        "day": "Friday",
        "hour_ruler": "Venus",
        "qualities": "warm & moist; lesser benefic",
        "metal_historical": "copper",
        "metal_safe": "copper",
        "stones": ["emerald", "rose quartz", "jade", "malachite"],
        "colors": ["green", "rose pink", "copper"],
        "incense": ["rose", "sandalwood", "vanilla"],
        "body": "kidneys, throat, the generative faculty",
        "charitable_acts": [
            "making peace, reconciliation, and acts of kindness",
            "creating or supporting art, music, and beauty",
            "cultivating and repairing relationships",
        ],
        "direction": None,
    },
    "Mercury": {
        "day": "Wednesday",
        "hour_ruler": "Mercury",
        "qualities": "convertible; takes the nature of its associations",
        "metal_historical": "quicksilver",  # toxic — provenance only
        "metal_safe": "an alloy or simply none (do NOT handle mercury)",
        "stones": ["agate", "aventurine", "fluorite", "opal"],
        "colors": ["orange", "mixed/iridescent", "light blue"],
        "incense": ["lavender", "mastic", "storax"],
        "body": "brain, tongue, hands, the rational faculty",
        "charitable_acts": [
            "study, writing, teaching, and honest clear communication",
            "helping others with letters, contracts, or learning",
            "mending misunderstandings through careful speech",
        ],
        "direction": None,
    },
    "Moon": {
        "day": "Monday",
        "hour_ruler": "Moon",
        "qualities": "cold & moist; luminary of the night",
        "metal_historical": "silver",
        "metal_safe": "silver",
        "stones": ["moonstone", "selenite", "pearl", "clear quartz"],
        "colors": ["silver", "white", "pale blue"],
        "incense": ["jasmine", "sandalwood", "white lotus"],
        "body": "stomach, breasts, womb, bodily fluids, the digestive faculty",
        "charitable_acts": [
            "care and nurture — tending home, family, mothers, and children",
            "providing food, shelter, or comfort to those in need",
            "rest, emotional attunement, and acts of quiet service",
        ],
        "direction": None,
    },
}

PROVENANCE = (
    "Renaissance planetary correspondences (Agrippa, Three Books of Occult "
    "Philosophy Bk I; standard alchemical day/metal assignments). Historical and "
    "symbolic only — not medical, dietary, or safety advice."
)


class RemediationEngine:
    @staticmethod
    def malefic_contrary_to_sect(sect: Sect) -> str:
        """The primary remediation target: the out-of-sect malefic (Mars by day,
        Saturn by night)."""
        return "Mars" if sect == Sect.DAY else "Saturn"

    @staticmethod
    def prescribe(
        planet: str,
        moon_mansion: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """A safe, sourced remediation prescription for one planet, with the
        electional-timing rule (day + planetary hour, optionally Moon's mansion)."""
        c = PLANETARY_CORRESPONDENCES.get(planet)
        if not c:
            return {"planet": planet, "error": "no correspondence table for this body"}

        timing = (
            f"Perform on {c['day']}, in the planetary hour of {c['hour_ruler']} "
            f"(compute via the planetary-hours layer for the native's location)."
        )
        mansion_note = None
        if moon_mansion:
            m_name = moon_mansion.get("name") or moon_mansion.get("mansion")
            intents = moon_mansion.get("intents") or moon_mansion.get("good_for")
            if m_name:
                mansion_note = (
                    f"For lunar timing, prefer when the waxing Moon transits its natal "
                    f"mansion ({m_name})"
                    + (f", whose intents include: {intents}." if intents else ".")
                )

        return {
            "planet": planet,
            "reason": reason,
            "qualities": c["qualities"],
            "election": {
                "day": c["day"],
                "planetary_hour": c["hour_ruler"],
                "rule": timing,
                "lunar_mansion": mansion_note,
            },
            "safe_remedies": {
                "stones": c["stones"],
                "colors": c["colors"],
                "incense": c["incense"],
                "metal": c["metal_safe"],
                "charitable_acts": c["charitable_acts"],
            },
            "historical_only": {
                "metal": c["metal_historical"],
                "unsafe": c["metal_historical"] in _UNSAFE,
                "note": "Recorded for provenance; not a recommendation."
                if c["metal_historical"] in _UNSAFE
                else None,
            },
            "body_correspondence": c["body"],
            "direction": c["direction"],
            "provenance": PROVENANCE,
        }

    @staticmethod
    def prescribe_for_chart(
        sect: Sect,
        afflicted_planets: Optional[List[str]] = None,
        moon_mansion: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Assemble prescriptions for the out-of-sect malefic plus any explicitly
        afflicted septener bodies (deduped, capped)."""
        septener = {"Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"}
        primary = RemediationEngine.malefic_contrary_to_sect(sect)
        targets: List[str] = [primary]
        for p in afflicted_planets or []:
            if p in septener and p not in targets:
                targets.append(p)
        targets = targets[:3]

        out = {
            "primary_target": primary,
            "primary_reason": "the malefic contrary to the sect (its disruptive testimony is strongest)",
            "prescriptions": [],
            "provenance": PROVENANCE,
        }
        for p in targets:
            reason = (
                out["primary_reason"]
                if p == primary
                else "afflicted/maltreated significator"
            )
            out["prescriptions"].append(
                RemediationEngine.prescribe(p, moon_mansion=moon_mansion, reason=reason)
            )
        return out
