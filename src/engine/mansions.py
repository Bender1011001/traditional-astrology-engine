from typing import Dict


class LunarMansionEngine:
    """
    Implements the configured equal tropical 28-mansion calculation.

    Picatrix Book I, Chapter 4 supplies electional/talismanic operations, not
    natal delineations.  Callers must not turn ``intents_good`` or
    ``intents_bad`` into character statements or birth-chart predictions.

    PROVENANCE WARNING, from reading Ritter's Arabic on 2026-08-11
    ---------------------------------------------------------------
    The BOUNDARIES below are exactly right.  Ritter prints each mansion's span
    to the arc-second and they are equal 1/28 divisions of 12d51'26"; mansions
    1-12 and 26-28 were checked and agree to the second.  ``MANSION_WIDTH`` is
    correct.  Chapter 4 is also the correct citation - the Arabic heading is
    ``fasl (4)``.

    The INTENTS are a different matter and should not be treated as Picatrix
    until rewritten.  Comparing 12 mansions against Ritter showed a systematic,
    directional divergence: the political and coercive operations are missing
    (besieging cities, vengeance against kings, corrupting crops, severing
    partners, binding and RELEASING prisoners - the last is Ritter's first
    listed use for mansion 11 and absent here), while benign domestic material
    with no counterpart in the Arabic has been added (healing illness, ease of
    childbirth, washing the body, putting on new garments).  Mansion 8 is
    inverted in sense: Ritter makes friendship *between those who hate each
    other*, this table says *between allies*.  Each entry cites
    ``source_refs`` of ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"]; the
    divergent content is most likely the second, cited as though co-equal.

    TWO CONDITIONS FROM THE SOURCE THAT THIS ENGINE DOES NOT IMPLEMENT
    -----------------------------------------------------------------
    1. The Moon gate.  Picatrix states it at both ends of the chapter.  At the
       opening: "do not perform any of the works until the MOON IS IN THE
       DEGREE AGREEING WITH THAT WORK".  At the close, as ``al-'umda``, the
       cardinal rule: in works of GOOD the Moon must be "pure of the malefics
       and of combustion, applying to the benefics", and at the beginnings of
       works "separating from a benefic and applying to a benefic" - and in
       works of EVIL, the reverse.  A mansion therefore does not simply "mean"
       its uses; the operation is gated on lunar condition.  Nothing here
       evaluates that.
    2. The attribution.  Picatrix credits the whole 28-mansion system to India
       - "what the PEOPLE OF INDIA rely upon in their operations and their
       elections" - at both the opening (``al-Hindiyyun``) and the close.  He
       is reporting a foreign system, not asserting his own.

    See docs/sources/picatrix_notes.md for the passages and the per-mansion
    comparison.
    """

    MANSION_WIDTH = 12.8571428571  # 360 / 28

    MANSIONS = [
        {
            "mansion_id": 1,
            "name": "Al-Sharatain",
            "start_lon_deg": 0.0,
            "end_lon_deg": 12.857143,
            "intents_good": [
                "beginning journeys",
                "taking medicine",
                "purchasing livestock",
                "creating discord between individuals",
                "imprisonment of captives",
            ],
            "intents_bad": [
                "marriage",
                "meaningful partnerships",
                "foundations of alliances",
                "activities requiring cooperation",
            ],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 2,
            "name": "Al-Batin",
            "start_lon_deg": 12.857143,
            "end_lon_deg": 25.714286,
            "intents_good": [
                "polluting rivers and waters",
                "finding hidden treasure",
                "producing wheat",
                "destroying houses before completion",
                "creating anger between people",
                "strengthening prisons for captives",
            ],
            "intents_bad": ["completing construction projects", "peaceful endeavors"],
            "source_refs": ["Picatrix Bk I, Ch 4"],
        },
        {
            "mansion_id": 3,
            "name": "Al-Thurayya",
            "start_lon_deg": 25.714286,
            "end_lon_deg": 38.571429,
            "intents_good": [
                "acquisition of all good things",
                "sailing safely on the sea",
                "returning safely from journeys",
                "firmly incarcerating captives",
                "love and relationships",
            ],
            "intents_bad": [
                "marriage",
                "partnerships between unequals",
                "planting crops",
            ],
            "source_refs": ["Picatrix Bk I, Ch 4", "Picatrix Bk IV, Ch 9"],
        },
        {
            "mansion_id": 4,
            "name": "Aldebaran",
            "start_lon_deg": 38.571429,
            "end_lon_deg": 51.428572,
            "intents_good": [
                "employing others",
                "building and construction",
                "investing capital",
                "obtaining offices and positions",
            ],
            "intents_bad": ["marriage", "travel (especially dangerous journeys)"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 5,
            "name": "Al-Haqa",
            "start_lon_deg": 51.428572,
            "end_lon_deg": 64.285715,
            "intents_good": [
                "marriage",
                "education and learning",
                "making medicine",
                "travel",
                "employment",
                "favor from kings and officials",
                "divinatory dreams",
            ],
            "intents_bad": ["business partnerships"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Picatrix Bk IV, Ch 9"],
        },
        {
            "mansion_id": 6,
            "name": "Al-Hanah",
            "start_lon_deg": 64.285715,
            "end_lon_deg": 77.142858,
            "intents_good": [
                "actions of war and seeking justice",
                "pursuing enemies and evildoers",
                "travel",
                "forming partnerships",
                "excellent hunting",
                "besieging cities and castles",
                "exact revenge on enemies",
            ],
            "intents_bad": [
                "planting and agricultural work",
                "borrowing money",
                "depositing items for safekeeping",
                "taking medicines and treating injuries",
            ],
            "source_refs": ["Picatrix Bk I, Ch 4"],
        },
        {
            "mansion_id": 7,
            "name": "Al-Dhira",
            "start_lon_deg": 77.142858,
            "end_lon_deg": 90.0,
            "intents_good": [
                "agricultural pursuits",
                "washing or purifying the body",
                "reconciliation with enemies",
                "gaining advantage over adversaries",
            ],
            "intents_bad": ["buying property", "healing the sick"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 8,
            "name": "Al-Nathrah",
            "start_lon_deg": 90.0,
            "end_lon_deg": 102.857143,
            "intents_good": [
                "love and friendship",
                "safe travel and journeys",
                "creation of friendship between allies",
                "strengthening imprisonment of captives",
                "victory in combat",
                "driving out pests",
            ],
            "intents_bad": ["destruction and prostration of captives"],
            "source_refs": ["Picatrix Bk I, Ch 4"],
        },
        {
            "mansion_id": 9,
            "name": "Al-Tarf",
            "start_lon_deg": 102.857143,
            "end_lon_deg": 115.714286,
            "intents_good": [
                "capturing individuals for captivity",
                "fortifying gates and defenses",
            ],
            "intents_bad": [
                "constructive activities",
                "agricultural activities",
                "making trustworthy partnerships",
                "safe journeys",
                "inflicting controlled evil",
            ],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 10,
            "name": "Al-Jabha",
            "start_lon_deg": 115.714286,
            "end_lon_deg": 128.571429,
            "intents_good": [
                "healing of illness",
                "ease of childbirth in women",
                "marriage and partnerships",
                "building and construction",
            ],
            "intents_bad": ["travel (especially by sea)", "lending money"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Picatrix Bk IV, Ch 9"],
        },
        {
            "mansion_id": 11,
            "name": "Al-Zubrah",
            "start_lon_deg": 128.571429,
            "end_lon_deg": 141.428572,
            "intents_good": [
                "building and construction",
                "renting lands",
                "agriculture",
                "marriage",
                "putting on new garments",
                "voyages and maritime trade",
                "gaining by merchandise",
                "redemption of captives",
            ],
            "intents_bad": ["travel", "employment"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 12,
            "name": "Al-Sarfah",
            "start_lon_deg": 141.428572,
            "end_lon_deg": 154.285715,
            "intents_good": [
                "causing marital love",
                "curing the sick",
                "helping sailors",
                "planting crops",
            ],
            "intents_bad": ["marriage", "land journeys"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 13,
            "name": "Al-Awwa",
            "start_lon_deg": 154.285715,
            "end_lon_deg": 167.142858,
            "intents_good": [
                "increasing trade and money",
                "increase of harvests",
                "completion of buildings",
                "liberation of captives",
                "erotic love and pleasure",
            ],
            "intents_bad": ["long-term relationships"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Picatrix Bk IV, Ch 9"],
        },
        {
            "mansion_id": 14,
            "name": "Al-Simak",
            "start_lon_deg": 167.142858,
            "end_lon_deg": 180.0,
            "intents_good": [
                "causing marital love",
                "curing the sick",
                "helping sailors",
            ],
            "intents_bad": ["marriage", "land journeys"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 15,
            "name": "Al-Ghafr",
            "start_lon_deg": 180.0,
            "end_lon_deg": 192.857143,
            "intents_good": [
                "digging wells and canals",
                "healing illnesses caused by windiness",
                "employment",
                "moving house",
                "buying and selling",
            ],
            "intents_bad": ["journeys", "partnerships", "marriage"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 16,
            "name": "Azebene",
            "start_lon_deg": 192.857143,
            "end_lon_deg": 205.714286,
            "intents_good": [
                "making money through buying and selling",
                "prosperity",
                "favor from authorities",
            ],
            "intents_bad": [
                "travel",
                "healing",
                "making deals",
                "planting crops",
                "marriage",
                "partnerships",
            ],
            "source_refs": ["Picatrix Bk I, Ch 4", "Renaissance Astrology"],
        },
        {
            "mansion_id": 17,
            "name": "Alichil",
            "start_lon_deg": 205.714286,
            "end_lon_deg": 218.571429,
            "intents_good": [
                "placement of armies",
                "making buildings strong and stable",
                "safety of sailors",
                "ordinary durability loves",
            ],
            "intents_bad": ["exposing enemies", "family relationships"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 18,
            "name": "Al-Kalb",
            "start_lon_deg": 218.571429,
            "end_lon_deg": 231.428572,
            "intents_good": [
                "building",
                "renting and purchasing land",
                "getting promoted",
                "eastward journeys",
                "planting",
                "taking medication",
            ],
            "intents_bad": ["partnerships", "employment"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 19,
            "name": "Al-Ibrah",
            "start_lon_deg": 231.428572,
            "end_lon_deg": 244.285715,
            "intents_good": [
                "sieges",
                "litigation",
                "land journeys",
                "planting trees",
                "hurrying the menses of women",
            ],
            "intents_bad": ["partnerships", "employment", "sea travel"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Picatrix Bk IV, Ch 9"],
        },
        {
            "mansion_id": 20,
            "name": "Al-Naym",
            "start_lon_deg": 244.285715,
            "end_lon_deg": 257.142858,
            "intents_good": ["hunting on land"],
            "intents_bad": ["marriage", "money loans"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Picatrix Bk IV, Ch 9"],
        },
        {
            "mansion_id": 21,
            "name": "Al-Balda",
            "start_lon_deg": 257.142858,
            "end_lon_deg": 270.0,
            "intents_good": [
                "strengthening buildings",
                "planting",
                "making big purchases or investments",
            ],
            "intents_bad": ["employment"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 22,
            "name": "Sa'd al-Dhabih",
            "start_lon_deg": 270.0,
            "end_lon_deg": 282.857143,
            "intents_good": [
                "healing",
                "journeys",
                "partnerships",
                "quick escape for those caught",
            ],
            "intents_bad": ["marriage", "employment"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 23,
            "name": "Sa'd Bula",
            "start_lon_deg": 282.857143,
            "end_lon_deg": 295.714286,
            "intents_good": [
                "putting on new clothes",
                "forming partnerships",
                "taking medicine",
                "ensuring quick escape for captives",
            ],
            "intents_bad": [
                "marriage (implies abuse)",
                "journeys",
                "depositing items for safekeeping",
            ],
            "source_refs": ["Picatrix Bk I, Ch 4", "Picatrix Bk IV, Ch 9"],
        },
        {
            "mansion_id": 24,
            "name": "Sa'd al-Su'ud",
            "start_lon_deg": 295.714286,
            "end_lon_deg": 308.571429,
            "intents_good": ["sieges", "seeking fights", "taking revenge on enemies"],
            "intents_bad": [
                "marriage",
                "planting",
                "partnerships",
                "purchasing animals",
                "employment",
            ],
            "source_refs": ["Picatrix Bk I, Ch 4"],
        },
        {
            "mansion_id": 25,
            "name": "Sa'd al-Akhbiyah",
            "start_lon_deg": 308.571429,
            "end_lon_deg": 321.428572,
            "intents_good": [
                "sieges",
                "seeking fights",
                "taking revenge on enemies",
                "safety in travel (though causes delays)",
                "fortifying buildings",
            ],
            "intents_bad": [
                "marriage",
                "planting",
                "partnerships",
                "purchasing animals",
                "employment",
            ],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
        {
            "mansion_id": 26,
            "name": "Al-Fargh al-Muqaddam",
            "start_lon_deg": 321.428572,
            "end_lon_deg": 334.285715,
            "intents_good": ["planting", "business", "marriage", "creation of love"],
            "intents_bad": ["travel", "employment", "giving or taking loans"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Picatrix Bk IV, Ch 9"],
        },
        {
            "mansion_id": 27,
            "name": "Al-Fargh al-Thani",
            "start_lon_deg": 334.285715,
            "end_lon_deg": 347.142858,
            "intents_good": [
                "increasing harvests",
                "revenues",
                "gains",
                "healing infirmities",
            ],
            "intents_bad": ["building", "upholding prisons", "sea travel"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Constellations of Words"],
        },
        {
            "mansion_id": 28,
            "name": "Batn al-Hut",
            "start_lon_deg": 347.142858,
            "end_lon_deg": 360.0,
            "intents_good": ["trade", "planting", "healing", "marriage"],
            "intents_bad": ["loaning or taking loans"],
            "source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"],
        },
    ]

    @staticmethod
    def get_lunar_mansion(longitude_deg: float, include_boundary: bool = True) -> Dict:
        """
        Maps an ecliptic longitude to the corresponding tropical lunar mansion.
        Returns the full mansion dictionary.
        """
        norm_lon = longitude_deg % 360.0

        if include_boundary:
            mansion_index = int(norm_lon // LunarMansionEngine.MANSION_WIDTH)
        else:
            mansion_index = int(
                (norm_lon + 0.000000001) // LunarMansionEngine.MANSION_WIDTH
            )

        # Handle edge case at 360/0
        if mansion_index == 28:
            mansion_index = (
                0  # Wrap to start if it hit exactly 360, but wait.. 360 is 0.
            )
            # Actually the index goes 0..27.
            # If norm_lon is 359.999, index is 27.
            # If norm_lon is 0.0, index is 0.

        # Safety clamp
        if mansion_index > 27:
            mansion_index = 0
        if mansion_index < 0:
            mansion_index = 0

        # Adjust for 1-based indexing in MANSIONS list if needed, or just access by index
        # MANSIONS list is 0-indexed but has mansion_id 1..28
        result = dict(LunarMansionEngine.MANSIONS[mansion_index])
        result.update(
            {
                "calculation_method": "configured_equal_tropical_28_from_aries",
                "mansion_width_deg": LunarMansionEngine.MANSION_WIDTH,
                "source_rule_id": "picatrix_lunar_mansions_electional_scope",
                "usage_scope": "electional_talismanic_only",
                "natal_delineation_supported": False,
                "publication_limit": (
                    "Publish the calculated mansion and the source's electional scope. "
                    "Do not convert image-making or electional operations into natal character or destiny claims."
                ),
            }
        )
        if result["mansion_id"] == 11:
            result["inspected_source_name_variant"] = "Azobra"
            result["assignment_robust_to_inspected_boundary_variants"] = True
        return result
