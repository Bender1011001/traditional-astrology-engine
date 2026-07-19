"""
Doctrinal-disagreement layer.

Traditional astrology is not a single consistent system — its authorities disagree
on real points (triplicity rulers, bounds, the house of the mother, degree tables,
length-of-life method, fixed-star natures, ...). Faithfulness to the texts means
NOT silently picking one. This module exposes those disagreements so the reading
can state, for each contested judgment, *that* the sources disagree, *which*
sources, and *both* positions.

Two parts:
  * DOCTRINAL_FORKS — a curated, sourced registry of the standing disagreements,
    each with the competing authorities and their positions, plus how this engine
    handles it (default + alternates).
  * DoctrineEngine.chart_dignity_forks() — per-chart, computed disagreements: for
    THIS nativity's planets, where do the triplicity schemes (Dorothean vs
    Ptolemaic) or the bound systems (Egyptian vs Ptolemaic) actually give a
    different verdict? These are derived from the engine's own variant calculator,
    so they are exact for the chart in hand.
"""

from typing import Any, Dict, List

from .dignities import DignityCalculator, TermSystem, TriplicityScheme
from .models import PlanetName, Sect

_SEPTENER = [
    PlanetName.SUN, PlanetName.MOON, PlanetName.MERCURY, PlanetName.VENUS,
    PlanetName.MARS, PlanetName.JUPITER, PlanetName.SATURN,
]

# --- Curated registry of standing disagreements ----------------------------
DOCTRINAL_FORKS: List[Dict[str, Any]] = [
    {
        "topic": "Triplicity rulers",
        "summary": "How many rulers a triplicity has, and who they are.",
        "positions": [
            {"authority": "Dorothean (Dorotheus, Carmen Astrologicum; Bonatti; Māshāʾallāh; most Persian/medieval)",
             "position": "Three rulers per triplicity — a day lord, a night lord, and a participating lord (+3 / +3 / +1)."},
            {"authority": "Ptolemaic (Ptolemy, Tetrabiblos I.18; William Lilly)",
             "position": "Two rulers per triplicity — day and night only, no participating lord. The Water day-ruler is Mars (vs Venus in the Dorothean scheme)."},
        ],
        "engine_handling": "Default = Dorothean; Ptolemaic (sect-gated) is computable. See chart_specific for where they actually differ in this chart.",
    },
    {
        "topic": "Terms / bounds",
        "summary": "Which table of bounds (sub-rulers of degree-ranges) is authoritative.",
        "positions": [
            {"authority": "Egyptian (Vettius Valens and most Hellenistic authors)",
             "position": "The oldest, most widely used bound table."},
            {"authority": "Ptolemaic (Ptolemy, Tetrabiblos I.20-21)",
             "position": "Ptolemy's reconstructed 'ancient' table, differing from the Egyptian in many degrees."},
            {"authority": "Chaldean",
             "position": "A third, less common system."},
        ],
        "engine_handling": "Default = Egyptian; Ptolemaic and Chaldean are computable. See chart_specific for per-planet differences.",
    },
    {
        "topic": "House of the mother",
        "summary": "Which place signifies the mother.",
        "positions": [
            {"authority": "Valens (Anthology)", "position": "The mother is taken from the 10th place."},
            {"authority": "Later Hellenistic / medieval (and Lilly)", "position": "Parents are taken from the 4th; the 4th can signify the mother (or the father), with sect and significators deciding."},
        ],
        "engine_handling": "Topical layer reports the 10th as the mother's place AND the 4th for parents; natural significators (Moon/Venus) are given alongside.",
    },
    {
        "topic": "Significator of the parents",
        "summary": "Which planets signify father and mother.",
        "positions": [
            {"authority": "Ptolemy (Tetrabiblos III.4)", "position": "Sun signifies the father by day, Saturn by night; Venus signifies the mother by day, the Moon by night."},
            {"authority": "Common medieval usage", "position": "Sun = father and Moon = mother generally, with Saturn as a co-significator of the father."},
        ],
        "engine_handling": "Topical natural-significators use Ptolemy's sect-based assignment, listing the co-significator.",
    },
    {
        "topic": "Degree qualities (masculine/feminine, light/dark/pitted/azimene, etc.)",
        "summary": "The per-degree quality tables differ between authorities.",
        "positions": [
            {"authority": "Lilly (Christian Astrology, 1647, p.116)", "position": "The engine's default table — e.g. the 8th degree of Aries is masculine."},
            {"authority": "al-Bīrūnī (Book of Instruction)", "position": "Differs on specific degrees — e.g. the 8th degree of Aries is feminine; Aquarius and Pisces differ materially (per Skyscript's comparison)."},
        ],
        "engine_handling": "Default = Lilly 1647 (analysis.degree_qualities, tradition='lilly_1647'). The al-Bīrūnī table is a separate authority, not yet transcribed; never auto-merged.",
    },
    {
        "topic": "Length of life — Alcocoden years",
        "summary": "How to compute the years the Giver of Years grants.",
        "positions": [
            {"authority": "Configured strict bound-lord branch (legacy valens_term key)", "position": "The inspected sources do not justify attributing this implementation to Valens."},
            {"authority": "Bonatti / Lilly (points method)", "position": "Greater / mean / lesser planetary years selected by the Alcocoden's condition."},
        ],
        "engine_handling": "analysis.vitality computes both the legacy valens_term key (configured strict bound-lord branch) and bonatti_points, then publishes the conflict rather than falsely harmonizing it.",
    },
    {
        "topic": "Lot of Marriage",
        "summary": "Significator and lot for marriage differ by author and by the native's sex.",
        "positions": [
            {"authority": "Dorotheus (Carmen II)", "position": "Venus signifies the wife for a male native; Mars (and/or Jupiter) the husband for a female native; the 7th and its lord co-signify."},
            {"authority": "Hermes / Paulus (lot formulas)", "position": "Distinct lot-of-marriage formulas (and separate male/female versions) that do not always agree."},
        ],
        "engine_handling": "Topical layer gives sex-specific significators; the lots catalog provides the formula lots.",
    },
    {
        "topic": "Fixed-star nature & signification",
        "summary": "A star's planetary nature and meaning are reported differently across authorities.",
        "positions": [
            {"authority": "Ptolemy (Tetrabiblos I.9)", "position": "Gives planetary natures, often for parts of constellations rather than single stars."},
            {"authority": "Robson (Fixed Stars and Constellations)", "position": "Consolidated star-by-star significations for natal use."},
            {"authority": "Brady (Brady's Book of Fixed Stars)", "position": "Paran-based, with modern precessed positions."},
        ],
        "engine_handling": "stars.py stores a Ptolemaic nature plus a delineative meaning; where authorities differ, provenance should be preserved rather than merged.",
    },
    {
        "topic": "Almuten Figuris (Lord of the Nativity)",
        "summary": "Which points and weightings determine the chart's Almuten.",
        "positions": [
            {"authority": "Ibn Ezra (5 hylegiacal points)", "position": "Sun, Moon, Ascendant, Lot of Fortune, prenatal Syzygy, scored by essential + accidental dignity."},
            {"authority": "al-Qabīsī / others", "position": "Differ in the points counted and the weighting of accidental factors."},
        ],
        "engine_handling": "Default = Ibn Ezra 5-point method (analysis.dignity.almuten).",
    },
    {
        "topic": "Combustion / Cazimi / Under-the-Beams orbs",
        "summary": "The degree boundaries of solar-proximity conditions vary by author.",
        "positions": [
            {"authority": "Common (Lilly and others)", "position": "Cazimi within 17'; combust to ~8°30'; under the beams to ~17°."},
            {"authority": "Variant usage", "position": "Some take cazimi at 16', combustion to 8°, under-beams to 12° or 15°."},
        ],
        "engine_handling": "Engine uses cazimi 17', combust 8°, under-beams 15°. This is one defensible boundary set among several.",
    },
    {
        "topic": "Remediation: 'charitable act' and 'psalm' columns",
        "summary": "Whether these are sourced from the core magical corpus.",
        "positions": [
            {"authority": "Agrippa (Bk I) + Picatrix", "position": "Supply correspondences, images, suffumigations, and invocations — but NOT a clean per-planet 'charitable act' or 'psalm' table."},
            {"authority": "Later Christianized devotional layer", "position": "Adds psalm-per-planet and charitable-act assignments not present in the earlier magical sources."},
        ],
        "engine_handling": "analysis.remediation.charitable_acts are an interpretive extension derived from each planet's significations, NOT a single sourced table — flagged as such.",
    },
]


class DoctrineEngine:
    @staticmethod
    def _trip_points(name: PlanetName, lon: float, sect: Sect, scheme: TriplicityScheme) -> int:
        bd = DignityCalculator.calculate_planet_dignity_variant(
            name, lon, sect, term_system=TermSystem.EGYPTIAN,
            triplicity_scheme=scheme, include_monomoiria=False,
        )["score_breakdown"]
        return int(bd.get("triplicity", 0) or 0)

    @staticmethod
    def _term_points(name: PlanetName, lon: float, sect: Sect, ts: TermSystem) -> int:
        bd = DignityCalculator.calculate_planet_dignity_variant(
            name, lon, sect, term_system=ts,
            triplicity_scheme=TriplicityScheme.DOROTHEAN, include_monomoiria=False,
        )["score_breakdown"]
        return int(bd.get("term", 0) or 0)

    @staticmethod
    def chart_dignity_forks(chart: Any, sect: Sect) -> List[Dict[str, Any]]:
        """Exact, per-chart disagreements between the dignity schemes for this
        nativity's septener planets."""
        forks: List[Dict[str, Any]] = []
        for p in getattr(chart, "planets", []):
            if p.name not in _SEPTENER:
                continue
            lon = float(p.longitude)
            name = p.name.value

            dor = DoctrineEngine._trip_points(p.name, lon, sect, TriplicityScheme.DOROTHEAN)
            pto = DoctrineEngine._trip_points(p.name, lon, sect, TriplicityScheme.PTOLEMAIC_SECT_GATED)
            if dor != pto:
                forks.append({
                    "planet": name,
                    "factor": "triplicity dignity",
                    "positions": [
                        {"authority": "Dorothean (Dorotheus, Bonatti)", "value": f"+{dor}" if dor else "none"},
                        {"authority": "Ptolemaic (Ptolemy, Lilly)", "value": f"+{pto}" if pto else "none"},
                    ],
                    "note": f"The triplicity schemes disagree on {name}'s triplicity dignity here; state both rather than picking one.",
                })

            egy = DoctrineEngine._term_points(p.name, lon, sect, TermSystem.EGYPTIAN)
            pty = DoctrineEngine._term_points(p.name, lon, sect, TermSystem.PTOLEMAIC)
            if egy != pty:
                forks.append({
                    "planet": name,
                    "factor": "term (bound) dignity",
                    "positions": [
                        {"authority": "Egyptian bounds (Valens)", "value": f"+{egy}" if egy else "none"},
                        {"authority": "Ptolemaic bounds (Ptolemy)", "value": f"+{pty}" if pty else "none"},
                    ],
                    "note": f"The bound systems disagree on whether {name} holds its own term here; state both.",
                })
        return forks

    @staticmethod
    def build(chart: Any, sect: Sect) -> Dict[str, Any]:
        try:
            chart_specific = DoctrineEngine.chart_dignity_forks(chart, sect)
        except Exception as exc:  # never break the audit
            chart_specific = [{"error": f"chart-specific fork computation degraded: {exc!r}"}]
        return {
            "_doc": "Where traditional authorities disagree, the reading MUST state the disagreement, name the sources, and give both positions — never silently pick one.",
            "known_forks": DOCTRINAL_FORKS,
            "chart_specific": chart_specific,
        }
