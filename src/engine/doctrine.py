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
        "topic": "Masculine and feminine degrees",
        "summary": "Whether the degrees alternate by a rule or follow an irregular table.",
        "positions": [
            {"authority": "Valens, Anthologiae I.12 (printed pp. 27-28), c. 165",
             "position": "A GENERATIVE RULE: in masculine signs the first 2.5 degrees are masculine, the next 2.5 feminine, alternating; in feminine signs the first 2.5 are feminine, then alternating. Twelve equal blocks per sign, phase set by the sign's own gender."},
            {"authority": "Lilly, Christian Astrology p. 117, 1647",
             "position": "An IRREGULAR TABLE with no evident generating rule - Aries breaks at 8/9/15/22/30, Taurus at 5/11/17/21/24/30, and so on."},
        ],
        "engine_handling": "The engine ships Lilly's table (degrees.py _MF), correctly attributed to him. These are two different systems roughly 1,480 years apart, and neither is a corruption of the other. Valens's rule is not implemented; it is recorded here so the Lilly table is not mistaken for the tradition's single answer.",
    },
    {
        "topic": "Bounds - a fourth system",
        "summary": "Valens rejects the received bounds and derives his own.",
        "positions": [
            {"authority": "Egyptian / Ptolemaic / Chaldean (the three transmitted systems)",
             "position": "Five bounds per sign among the five non-luminaries; the lights receive none. Ptolemy attacks the Egyptian set at I.21 for preserving 'consistency neither of order nor of quantity'."},
            {"authority": "Valens, Anthologiae III.9 (printed pp. 144-145), his own",
             "position": "'It did not seem right to me, as some do, to impose the bounds according to the seven-zone, but according to the HOUSES and the EXALTATIONS and the TRIANGLES.' Each planet's degree-allotment in EVERY sign equals its count of dignities: Sun 3, Moon 4, Saturn 4, Jupiter 5, Mars 5, Venus 5, Mercury 4 - summing exactly to 30. It INCLUDES THE LIGHTS, which no transmitted system does, and the order is SECT-DEPENDENT, which no transmitted system is."},
        ],
        "engine_handling": "Not implemented. TermSystem carries the three transmitted systems, which is the right default. Recorded because Valens flags it in the first person and derives it from a stated principle, so it is an authored alternative rather than a variant reading.",
    },
    {
        "topic": "Topical assignment of the places",
        "summary": "Which house governs which subject - and Valens alone carries three incompatible answers.",
        "positions": [
            {"authority": "Paulus Alexandrinus ch. 24 (the engine's default)",
             "position": "The familiar twelve-place topical list. This is what the reading cites."},
            {"authority": "Valens II.5-II.14 (printed pp. 62-68)",
             "position": "The places delineated by CONDITIONAL OUTCOME rather than topic - what results when benefics or malefics land there, and above all where the lords of the Ascendant, Fortune and Spirit fall."},
            {"authority": "Valens II.15 (p. 69) - the nine names",
             "position": "god=father (9th), goddess=mother (3rd), Good Daimon=children (11th), Good Fortune=MARRIAGE (5th), Bad Daimon=sufferings (12th), Bad Fortune=injuries (6th), Fortune+Ascendant=life, Daimon=practical wisdom, Midheaven=action, Eros=desire, Necessity=enemies."},
            {"authority": "Valens IV.12 (p. 179)",
             "position": "A third full list: the 2nd holds 'involvement with a woman' and the place of the will; the 3rd holds kingship and authority; the 8th is 'an IDLE place'; the 9th includes astrology itself and appearances of the gods; the 10th holds the WIFE."},
        ],
        "engine_handling": "The engine cites Paulus and will continue to. Recorded because marriage sits in the 7th (Valens II.37), the 5th (II.15) and the 2nd/10th (IV.12) depending on the chapter, all within one author - so a topical assignment is a defensible choice among several, not a settled fact.",
    },
    {
        "topic": "Lord of the Year - two different techniques, one name",
        "summary": "A naming hazard rather than a doctrinal disagreement.",
        "positions": [
            {"authority": "Valens I.11 (printed p. 27) - CALENDRICAL",
             "position": "Years since Augustus plus intercalary days plus days from Thoth to the birthday; subtract sevens; count the remainder from the Sun. Valens then rejects its universal form: 'that those born in the same year should have obtained one and the same rulership does not seem to have reason', preferring an epoch from the heliacal rising of Sirius."},
            {"authority": "Valens IV.11 (printed p. 174) - ANNUAL PROFECTION",
             "position": "Divide the age by twelve; the remainder counts the sign from the Ascendant. This is what the engine implements and cites to Paulus ch. 31."},
        ],
        "engine_handling": "The engine implements the profection only. Recorded so that nobody reading I.11 wires up the calendrical technique under the same label and silently changes what 'Lord of the Year' means.",
    },
    {
        "topic": "Triplicity rulers",
        "summary": "How many rulers a triplicity has, and who they are.",
        "positions": [
            {"authority": "Dorothean (Dorotheus, Carmen Astrologicum; Bonatti; Māshāʾallāh; most Persian/medieval)",
             "position": "Three rulers per triplicity — a day lord, a night lord, and a participating lord (+3 / +3 / +1)."},
            {"authority": "Ptolemaic (Ptolemy, Apotelesmatika I.19, read in the Boll-Boer Greek)",
             "position": "Two rulers per triplicity for fire, earth and air. WATER IS HIS ONLY THREE-RULER TRIANGLE: 'it was left to Mars, he being the sole one remaining and having a relation to it through the house of Scorpio; and co-ruling it WITH HIM - on account of both the sect and the femininity of the signs - by night the Moon, and by day Venus.' Mars therefore holds water in BOTH sects while Venus and the Moon split it by sect. Valens II.1 (54,4) independently gives Venus by day for water, so two 2nd-century Greek sources agree against Lilly."},
            {"authority": "Lilly (Christian Astrology I) — a Latin-European table, NOT Ptolemy's",
             "position": "Two rulers per triplicity, but the watery trigon is Mars by day AND by night. This is where the commonly-quoted 'Mars is the water day-ruler' comes from; it is Lilly's, not Ptolemy's, and the two are kept as separate authorities here rather than merged under one 'Ptolemaic' label."},
        ],
        "engine_handling": "Default = Dorothean; Ptolemaic (sect-gated) is computable. Ptolemy and Lilly were previously blended into one table whose water row (Mars by day, Moon by night) matched neither of them; they are now separate. See chart_specific for where they actually differ in this chart.",
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
