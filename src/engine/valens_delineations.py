"""Delineation tables translated from the Greek of Vettius Valens.

Kroll 1908 critical edition, read from page images. The English is this
project's own work, made directly from the Greek, and carries no translator's
copyright. Text and page citations: docs/sources/valens_translation.md

WHY THIS EXISTS
---------------
Every chart we produce reports a bound lord and then says nothing about it.
Valens I.3 (printed pp. 14-19) delineates all sixty bounds. The boundaries
themselves were already correct - verified digit-by-digit against
EGYPTIAN_TERMS in all twelve signs - but the meanings had never been carried.

COVERAGE IS PARTIAL AND DELIBERATELY SO
---------------------------------------
Roughly forty-one of the sixty are present. The absent ones were read but not
rendered closely enough to quote, and are simply omitted: a caller gets None
and says nothing. They are NOT filled with plausible-sounding text. An invented
delineation would be indistinguishable from a translated one at the point of
use, which is the whole failure this table exists to avoid.

Gaps, for whoever fills them: Cancer entirely; Virgo except Mercury; Libra
except Saturn; Scorpio except Mars; Leo's Mars bound; Pisces' Saturn bound.

READING THEM CORRECTLY
----------------------
Valens attaches conditions constantly, and they decide the outcome. Sagittarius
in Mercury's bound gives philosophers "when Mercury inclines" and soldiers
"when Mars". Capricorn in Jupiter's bound produces "both reputation and
disrepute, wealth and poverty" - he refuses a single verdict there and so
should we. Quoting the substrate without the condition is not faithful
transmission; it is quoting half a sentence.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

# (sign, bound_lord) -> delineation, translated from Valens I.3, pp. 14-19.
# Bound lords are the Egyptian set, which Valens uses and which our
# EGYPTIAN_TERMS table reproduces exactly.
BOUND_DELINEATIONS: Dict[Tuple[str, str], str] = {
    # --- Aries, p. 14 ---
    ("Aries", "Jupiter"): "gracious, robust, much-crowned, benefic",
    ("Aries", "Venus"): "cheerful, skilled in art, distinguished, complete, clean, of good complexion",
    ("Aries", "Mercury"): "changeable and well-natured, windy, hail-bringing, thundering, lightning-hurling",
    ("Aries", "Mars"): "corrupting, fiery, unstable, manly; of malefactors and of the rash",
    ("Aries", "Saturn"): "very cold, sterile, envious",
    # --- Taurus, p. 14 ---
    ("Taurus", "Venus"): "many-seeded, many-offspring, healthy, industrious, rather drunken",
    ("Taurus", "Mercury"): "intelligent and prudent - but malefactors, few-seeded, evil-natured, death-producing",
    ("Taurus", "Jupiter"): "great-minded, manly, ruling and beneficent, great-souled, gracious",
    ("Taurus", "Saturn"): "barren, sterile, eunuch-like, vagabond, blameworthy, toilsome",
    ("Taurus", "Mars"): (
        "masculine, tyrannical, fiery, harsh, murderous, temple-robbing, utterly wicked "
        "- yet not undistinguished, though corrupting and not long-lived"
    ),
    # --- Gemini, p. 15 ---
    ("Gemini", "Mercury"): "gracious, well-set, intelligent, of many arts, scientific, practical, celebrated, many-seeded",
    ("Gemini", "Jupiter"): "contentious, gracious, calm, much-crowned, well-nourished, beneficent",
    ("Gemini", "Venus"): "flowery, musical, poetic, crowd-related, joyful, much-crowned",
    ("Gemini", "Mars"): "much-toiling, brotherless, few-childed, corrupting, raw, meddlesome",
    ("Gemini", "Saturn"): (
        "gracious, administrative, acquisitive, intellectual, much-known, notable, "
        "distinguished in understanding, most renowned"
    ),
    # --- Cancer, p. 15 (transcribed 2026-08-10) ---
    ("Cancer", "Mars"): (
        "lightning-hurling, agitated, irregular, contrary-minded, frenzied, many-seeded, "
        "scarce, corrupting - and base at the end"
    ),
    ("Cancer", "Venus"): (
        "many-seeded, blameworthy, very moist, changeable, skilled in craft, crowd-related, "
        "and wholly mixed"
    ),
    ("Cancer", "Mercury"): (
        "exact, rapacious, leaders of public affairs, tax-collecting, popular, well-off, "
        "accumulators of substance"
    ),
    ("Cancer", "Jupiter"): (
        "kingly, imperial, renowned, much-litigating, great-minded, well-tempered, ruling, "
        "and altogether fine"
    ),
    ("Cancer", "Saturn"): (
        "since the whole sign is water - very moist, and scarce in what is their own, "
        "and needy toward the end"
    ),
    # --- Leo, p. 15 ---
    ("Leo", "Jupiter"): "experienced, masculine, imperial, wholly commanding, practical, eminent, having nothing lowly",
    ("Leo", "Venus"): "most well-tempered, relaxed, much-wise, enjoying",
    ("Leo", "Saturn"): (
        "much-experienced, thoughtful, natural, well-natured, narrow, mystical, of many arts, "
        "seekers of the things that have been hidden away - but sterile and barren"
    ),
    ("Leo", "Mercury"): "learned, crowd-related, heads of schools, incomparable, legal, intelligent",
    ("Leo", "Mars"): (
        "most base, monstrous, corrupting, injurious, sluggish, blameworthy, and unfortunate"
    ),
    # --- Virgo, p. 15 ---
    ("Virgo", "Mercury"): (
        "loftiest, administrative, much-wise, fair, setting people over great affairs, most "
        "intelligent, eminent - but not fortunate in love-matters; generally the whole of Virgo, "
        "but especially these degrees and those of Venus"
    ),
    ("Virgo", "Venus"): (
        "blameworthy, erring about marriages and falling into trouble on that account; but "
        "fortunate about theatrical matters; and most shameful about the afflictions, "
        "especially when Saturn bears witness with them"
    ),
    ("Virgo", "Jupiter"): (
        "of farm-loving, fair, retiring men, not uneducated; and they are guardian-like, "
        "many-seeded, and successful"
    ),
    ("Virgo", "Mars"): (
        "masculine, harsh, of popular demagogues and night-wanderers, of forgers and "
        "assailants; these degrees outrage men, and lead them into bonds, mutilations, "
        "tortures and prisons"
    ),
    ("Virgo", "Saturn"): (
        "monstrous, very cold, corrupting, short-lived - of men who are mocked"
    ),
    # --- Libra, p. 16 ---
    ("Libra", "Saturn"): "kingly, lofty, practical especially by day; sterile, moist, practical",
    ("Libra", "Mercury"): (
        "of the market-place, workshop-related and commercial, gathering documents of "
        "transactions and reckonings of numbers; on the whole just and understanding"
    ),
    ("Libra", "Jupiter"): (
        "wealth-making - but for those who fare badly, joyless, hoarding away, not fond of "
        "the beautiful, fault-finding; nor indeed well-off in children"
    ),
    ("Libra", "Venus"): (
        "of lovers of beauty and lovers of art, or of craftsmen themselves - modellers, "
        "painters, engravers; on the whole rhythmical, god-fearing, gentle, fortunate slowly, "
        "advanced of their own accord; and greatly fortunate about marriages, in all things happy"
    ),
    ("Libra", "Mars"): (
        "of leaders and commanders, fortunate in every craft of Mars, spirited, self-controlled "
        "and great-minded; but not well-off in brothers, nor having many"
    ),
    # --- Scorpio, p. 16 ---
    ("Scorpio", "Mars"): (
        "disturbed, easily moved, unstable, prone to anger, free-tongued, great-minded, "
        "few-childed, many-brothered, irregular in fortunes; well-set for nativities toward "
        "soldiering and travel abroad"
    ),
    # --- Scorpio continued, p. 17 ---
    ("Scorpio", "Venus"): (
        "fortunate in marriages, god-fearing, loved by everyone, art-loving, well-off, "
        "picked out above all others, of pleasant life"
    ),
    ("Scorpio", "Mercury"): (
        "of arms and contest, of crown-bearers, contending in bitter speeches and not to be "
        "despised; these too are many-seeded; but on the whole malicious in mind, especially "
        "against those who put them to the test or who act wickedly"
    ),
    ("Scorpio", "Jupiter"): (
        "of the much-skilled, of fortunate high priests, glorified with gold and purple and "
        "offices according to their own magnitudes; kindly to people and loving the gods"
    ),
    ("Scorpio", "Saturn"): (
        "punishing, scarce in children, scarce in brothers, hating their own, drug-makers, "
        "melancholic, woman-hating, having hidden injuries; on the whole most punishing and "
        "most given to blaming their lot; they are hated both by gods and by men - and they "
        "push back against those set above them, while being despised by the lowly"
    ),
    # --- Sagittarius, p. 17 ---
    ("Sagittarius", "Jupiter"): (
        "of practical men; moist with the well-tempered, altogether various in every art and "
        "action, much-crowned, many-childed, many-brothered, but scarce"
    ),
    ("Sagittarius", "Venus"): (
        "well-tempered, renowned, victorious, crown-bearing, god-fearing, honoured by superiors "
        "in crowds and among leaders; good in children and siblings; and to have several wives"
    ),
    ("Sagittarius", "Mercury"): (
        "of lovers of learning, prolific writers, practical men, begetting eternal things, "
        "philosophers, eminent in knowledge and prudence, lovers of history - WHEN MERCURY "
        "INCLINES; but WHEN MARS, lovers of arms and tacticians"
    ),
    ("Sagittarius", "Saturn"): "sterilizing and injuring, very cold, harmful; of base men unfortunate in everything",
    ("Sagittarius", "Mars"): (
        "very hot, danger-fleeing, insolent, shameless, corrupting - but having much movement "
        "in everything"
    ),
    # --- Capricorn, pp. 17-18 ---
    ("Capricorn", "Mercury"): (
        "lively, satirical, mimicking, lying, whorish, procuring; desirers of others' goods and "
        "inglorious - yet quick in everything, gracious and well-off, but not lofty"
    ),
    ("Capricorn", "Jupiter"): (
        "in the loftiest depression - producing BOTH reputation and disrepute, wealth and "
        "poverty, benefactions and theatrical displays; sterile, bearing females or monsters, "
        "small-seeming, private"
    ),
    ("Capricorn", "Venus"): (
        "of the profligate, lustful, downward-tending, undiscerning, blameworthy; changeable "
        "about their ends, not dying well, nor stable about marriages"
    ),
    ("Capricorn", "Saturn"): (
        "austere, joyless, strange, ill-childed, ill-brothered, raw, corrupting, very cold, "
        "envious, hesitating, guileful"
    ),
    ("Capricorn", "Mars"): (
        "lofty, authoritative, tyrannical, investing everything with command; scarce in their own "
        "kin, destructive of people, travelling, quarrel-loving, contentious to the end"
    ),
    # --- Aquarius, p. 18 (Venus bound verified at full resolution: Valens
    #     writes the figure as the WORD 'hex', not the numeral) ---
    ("Aquarius", "Mercury"): (
        "of the rich and treasure-loving, gladly hoarding; intelligent, legal, making everything "
        "exact, commanding, small-souled, full of cares, loving education and every skill, "
        "administrative, economical, philanthropic"
    ),
    ("Aquarius", "Venus"): (
        "well-loved, god-fearing, prospering without toil, suddenly fortunate, well-off, "
        "seafaring; many-seeded degrees - and it happens that one born under them consorts with "
        "old women, or with the injured, or with eunuchs"
    ),
    ("Aquarius", "Jupiter"): "fortunate, petty, secretive, unambitious, unmanifest, good-childed, unbrotherly",
    ("Aquarius", "Mars"): (
        "injurious especially about the inward parts, busied with lawsuits; of wicked, feeble and "
        "dissolute men - but quick to attempt evils"
    ),
    ("Aquarius", "Saturn"): (
        "sterile, moist, ill-born, injurious - especially about the meninges, the inward parts, "
        "dropsies and spasms; scarce, few-brothered, few-childed, envious, at the end not fortunate"
    ),
    # --- Pisces, p. 18 ---
    ("Pisces", "Venus"): (
        "cheerful, much-crowned, downward-tending, enjoying, sweet-living, glad, charming, "
        "beloved; advancing spontaneously; workers for the gods"
    ),
    ("Pisces", "Jupiter"): (
        "of lovers of learning and men of science, distinguished in crowds and prevailing in all "
        "discourse; many-brothered, many-childed"
    ),
    ("Pisces", "Mercury"): (
        "much-crowned, ruling, transacting for honoured men, merciful, god-loving, well-tempered"
    ),
    ("Pisces", "Mars"): (
        "practical, sea-fighters, leaders and stout-hearted, makers of things unspeakable, "
        "rapacious and again free in giving, variegated - not dying their own death"
    ),
    ("Pisces", "Saturn"): (
        "injurious, very moist, convulsive - unfortunate about everything"
    ),
}

# The sentence that closes I.3, printed p. 19,4-7: having set out for teaching
# purposes what each degree ALONE accomplishes, "with the domicile-lord lying
# upon them, it will accomplish its own - either base or good."  The bound
# delineation is therefore the degree's own contribution, and the condition of
# the overlying domicile lord decides whether it comes out base or good.  Prose
# must present it that way, never as a free-standing verdict.
BOUND_QUALIFIER = (
    "Valens sets the degrees out one at a time for teaching; in a real nativity the "
    "domicile lord lying over them decides whether what the degree carries comes out "
    "base or good (I.3, printed p. 19)."
)

# Whole-sign closing remarks Valens attaches to a sign's bounds as a set.
BOUND_SIGN_NOTES: Dict[str, str] = {
    "Sagittarius": "All the degrees in Sagittarius are various concerning all matters.",
}

# Valens I.1, pp. 1-5. Each planet is given a fixed six-part schema ending in
# sect, colour and taste. The colour/taste pair is complete across all seven
# and had never been carried at all.
PLANET_COLOUR_TASTE: Dict[str, Dict[str, str]] = {
    "Sun": {"colour": "yellowish-brown", "taste": "sharp"},
    "Moon": {"colour": "green", "taste": "salty"},
    "Saturn": {"colour": "castor-like", "taste": "astringent"},
    "Jupiter": {"colour": "grey, rather white", "taste": "sweet"},
    "Mars": {"colour": "red", "taste": "bitter"},
    "Venus": {"colour": "white", "taste": "most oily"},
    "Mercury": {"colour": None, "taste": None},  # not preserved in the read
}

# Valens I.1, p. 5. A one-line essence for each planet, distinct from the long
# signification lists. Better opening lines than any modern keyword set, and
# they are his.
PLANET_DOMAIN: Dict[str, str] = {
    "Moon": "forethought",
    "Sun": "radiance",
    "Saturn": "ignorance and necessity",
    "Jupiter": "reputation, crowns and eagerness",
    "Mars": "action and toil",
    "Venus": "love, desire and beauty",
    "Mercury": "law, custom and trust",
}

# Valens II.35, pp. 106-108. Eleven lunar configurations, each with the topic
# it signifies and the planet that prevails through it. Degree boundaries are
# elongation from the Sun.
LUNAR_PHASES = (
    {"name": "conjunction", "from_deg": 0.0, "to_deg": 0.0,
     "signifies": "reputation, power, kingly and tyrannical dispositions, public affairs of "
                  "cities, parents, marriages, mysteries, and all universal matters",
     "lord": None},
    {"name": "rising", "from_deg": 0.0, "to_deg": 46.0,
     "signifies": "life, action, and future foundation; it confirms the actions of the conjunction",
     "lord": "Mercury"},
    {"name": "crescent", "from_deg": 46.0, "to_deg": 90.0,
     "signifies": "upbringing, the things hoped for in life, women and the mother",
     "lord": "Mercury"},
    {"name": "first half-moon", "from_deg": 90.0, "to_deg": 135.0,
     "signifies": "injury, affliction and violent happenings; also children and rank",
     "lord": "Venus"},
    {"name": "first gibbous", "from_deg": 135.0, "to_deg": 180.0,
     "signifies": "happiness, coming advancement, travel abroad, and the sympathy of kin",
     "lord": "Sun"},
    {"name": "full moon", "from_deg": 180.0, "to_deg": 180.0,
     "signifies": "reputation and disrepute, travel, violent events, falls from eminence and "
                  "rises from the least, and parents",
     "lord": None},
    {"name": "second gibbous", "from_deg": 180.0, "to_deg": 225.0,
     "signifies": "sojourning abroad, greater action, and happiness",
     "lord": "Jupiter"},
    {"name": "second half-moon", "from_deg": 225.0, "to_deg": 280.0,
     "signifies": "old matters, long-lasting afflictions, and children",
     "lord": "Saturn"},
    {"name": "setting", "from_deg": 280.0, "to_deg": 360.0,
     "signifies": "the waning to conjunction, closing the cycle",
     "lord": "Saturn"},
)

# CAUTION on the 'lord' column. Valens gives the phase BOUNDARIES in degrees of
# elongation (46, 90, 135, 180, ... 280, 360) but gives the prevailing planets
# by DAY of the lunar month ("Mercury to day 4", "Venus to 12", "Saturn to 30").
# Those are two overlapping schemes and they do not align band-for-band. The
# lords here are attached to the nearest phase and are APPROXIMATE; the phase
# names and degree boundaries are exact. Do not present a lord as precisely
# bounded without re-reading pp. 106-108, where this mapping is recorded as
# English-only rather than transcribed Greek.


# Valens II.4, pp. 60-62. Keyed to the planet that is "allotted the hour"
# (rules the Ascendant) or rules the Lot of Fortune. Each entry has a base
# verdict and witness clauses that double, redirect or reverse it - the same
# three-part shape as the natal delineations.
LORD_OF_HOUR_OR_LOT: Dict[str, Dict[str, str]] = {
    "Saturn": {
        "base": "prospers in the action Saturn distributes, provided Mars does not oppose",
        "Jupiter": "doubly so, when Jupiter witnesses",
        "Venus": "through a woman, or through training, when Venus witnesses",
        "Mars": "but with Mars present or opposing, disturbances and oppositions instead",
        "Mercury": "impeded in hearing, when Mercury co-rules",
    },
    "Jupiter": {
        "base": "very fortunate from youth",
        "Mars": "advancing in brilliant military service, with Mars present or in trine",
        "Saturn": "coming into positions of eminence, with Saturn added",
    },
    "Sun": {
        "base": "fortunate, when rising and in sympathy with Jupiter",
        "Jupiter": "the sympathy with Jupiter is what carries it",
    },
    "Moon": {
        "base": "makes them great, and especially so in her own triangle",
    },
    "Venus": {
        "base": "deemed worthy of great honour, when conjunct or square the Lot of Fortune",
    },
}


def lord_of_hour_delineation(
    planet: Optional[str], witnesses: Optional[list] = None
) -> Optional[Tuple[str, list]]:
    """Valens II.4 for the lord of the Ascendant or of Fortune.

    Returns (base verdict, [witness clauses that apply]) or None. Witness
    clauses are returned separately so a caller cannot present a modified
    verdict as though it were the base one - Valens's clauses reverse the
    outcome as often as they strengthen it.
    """
    if not planet:
        return None
    entry = LORD_OF_HOUR_OR_LOT.get(str(planet))
    if not entry:
        return None
    clauses = [
        text
        for witness, text in entry.items()
        if witness != "base" and witness in set(witnesses or [])
    ]
    return entry["base"], clauses


def bound_delineation(sign: Optional[str], bound_lord: Optional[str]) -> Optional[str]:
    """Return Valens's delineation of a bound, or None if it was not translated.

    Returning None is correct behaviour for an untranslated bound. Callers must
    render nothing rather than substitute a generic phrase.
    """
    if not sign or not bound_lord:
        return None
    return BOUND_DELINEATIONS.get((str(sign), str(bound_lord)))


def lunar_phase_for(elongation_deg: Optional[float]) -> Optional[dict]:
    """Valens's phase for a Sun-Moon elongation in degrees, or None."""
    if elongation_deg is None:
        return None
    try:
        e = float(elongation_deg) % 360.0
    except (TypeError, ValueError):
        return None
    if e < 1.0:
        return dict(LUNAR_PHASES[0])
    for phase in LUNAR_PHASES[1:]:
        if phase["from_deg"] <= e < phase["to_deg"]:
            return dict(phase)
    return dict(LUNAR_PHASES[-1])
