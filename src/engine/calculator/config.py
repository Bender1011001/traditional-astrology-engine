import swisseph as swe

ZODIAC_SYSTEM_LABELS = {
    "tropical": "Tropical",
    "sidereal": "Sidereal"
}

AYANAMSA_OPTIONS = {
    "fagan_bradley": (swe.SIDM_FAGAN_BRADLEY, "Fagan-Bradley"),
    "lahiri": (swe.SIDM_LAHIRI, "Lahiri"),
    "krishnamurti": (swe.SIDM_KRISHNAMURTI, "Krishnamurti"),
    "raman": (swe.SIDM_RAMAN, "Raman"),
    "hipparchos": (swe.SIDM_HIPPARCHOS, "Hipparchos"),
    "true_citra": (swe.SIDM_TRUE_CITRA, "True Citra"),
    "true_revati": (swe.SIDM_TRUE_REVATI, "True Revati"),
    "suryasiddhanta": (swe.SIDM_SURYASIDDHANTA, "Surya Siddhanta")
}

AYANAMSA_ALIASES = {
    "faganbradley": "fagan_bradley",
    "fagan": "fagan_bradley",
    "lahiri": "lahiri",
    "krishnamurti": "krishnamurti",
    "kp": "krishnamurti",
    "raman": "raman",
    "hipparchos": "hipparchos",
    "hipparchus": "hipparchos",
    "truecitra": "true_citra",
    "truerevati": "true_revati",
    "suryasiddhanta": "suryasiddhanta"
}

HOUSE_SYSTEM_LABELS = {
    "P": "Placidus",
    "W": "Whole Sign",
    "R": "Regiomontanus",
    "B": "Alcabitius",
    "C": "Campanus",
    "O": "Porphyry",
    "E": "Equal",
    "K": "Koch",
    "T": "Topocentric"
}

HOUSE_SYSTEM_ALIASES = {
    "placidus": "P",
    "pl": "P",
    "wholesign": "W",
    "whole": "W",
    "ws": "W",
    "regiomontanus": "R",
    "regio": "R",
    "alcabitius": "B",
    "campanus": "C",
    "porphyry": "O",
    "equal": "E",
    "koch": "K",
    "topocentric": "T",
    "topo": "T"
}

COMPARE_SYSTEMS = ["W", "P", "R", "B", "O", "C"]

def normalize_zodiac_system(value: str | None) -> tuple[str, str]:
    if not value:
        return "tropical", ZODIAC_SYSTEM_LABELS["tropical"]
    raw = value.strip().lower()
    if raw in ("sidereal", "s", "sid"):
        return "sidereal", ZODIAC_SYSTEM_LABELS["sidereal"]
    return "tropical", ZODIAC_SYSTEM_LABELS["tropical"]

def normalize_ayanamsa(value: str | None) -> tuple[int, str, str]:
    if not value:
        mode, label = AYANAMSA_OPTIONS["lahiri"]
        return mode, label, "lahiri"
    key = value.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    norm = AYANAMSA_ALIASES.get(key, "lahiri")
    mode, label = AYANAMSA_OPTIONS.get(norm, AYANAMSA_OPTIONS["lahiri"])
    return mode, label, norm

def normalize_house_system(value: str | None) -> tuple[str, str]:
    if not value:
        return "P", HOUSE_SYSTEM_LABELS["P"]
    raw = value.strip()
    if not raw:
        return "P", HOUSE_SYSTEM_LABELS["P"]
    if len(raw) == 1 and raw.upper() in HOUSE_SYSTEM_LABELS:
        code = raw.upper()
        return code, HOUSE_SYSTEM_LABELS[code]
    key = raw.lower().replace(" ", "").replace("-", "").replace("_", "")
    code = HOUSE_SYSTEM_ALIASES.get(key, "P")
    return code, HOUSE_SYSTEM_LABELS.get(code, "Placidus")
