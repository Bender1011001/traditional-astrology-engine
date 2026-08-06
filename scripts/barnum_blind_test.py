#!/usr/bin/env python3
"""
Barnum blind-control test.

Generates plain-language statement lists for 1 real chart + 3 decoy charts
(same birthplace, different dates/times), using ONE fixed rule table applied
identically to every chart. Lists are shuffled into labels A-D; the mapping
is written to a separate answer-key file.

Grade every statement in every list T / F / ? without looking at the key.
If astrology carries signal, the real chart's list should outscore the decoys.
"""

import json
import os
import random
import sys
from datetime import date

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.prediction import FIRDARIA_DAY, FIRDARIA_NIGHT
from src.scripts.generate_premium_report import generate_chart_data_object

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
CARDINAL, FIXED, MUTABLE = {0, 3, 6, 9}, {1, 4, 7, 10}, {2, 5, 8, 11}
AIR = {2, 6, 10}
SEVEN = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
HARD = {"Conjunction", "Square", "Opposition"}

MELOTHESIA = {
    "Aries": "head (headaches/migraines, sinus, eyes)",
    "Taurus": "throat and neck",
    "Gemini": "lungs, shoulders, arms and hands",
    "Cancer": "stomach and chest",
    "Leo": "heart, upper back and spine",
    "Virgo": "gut and digestion (food sensitivities, stomach trouble under stress)",
    "Libra": "kidneys and lower back",
    "Scorpio": "reproductive organs and bladder",
    "Sagittarius": "hips, thighs and liver",
    "Capricorn": "knees, joints, bones, teeth and skin",
    "Aquarius": "ankles, calves and circulation",
    "Pisces": "feet, lymph and immune system",
}

# Fixed calendar windows judged per-chart by its own time-lords (same windows
# for every list so year-quality claims are directly comparable).
WINDOWS = [
    ("2019-01", "2021-12", date(2020, 6, 15)),
    ("2022-01", "2024-06", date(2023, 3, 15)),
    ("2024-07", "2025-06", date(2025, 1, 1)),
    ("2025-07", "now", date(2026, 3, 1)),
]


def sidx(lon):
    return int(lon // 30) % 12


def whole_sign_house(p_lon, asc_idx):
    return (sidx(p_lon) - asc_idx) % 12 + 1


def cond_class(cond):
    """Uniform 3-way classification of a topos ruler_condition dict."""
    if not cond or not cond.get("available", False):
        return "mixed"
    score = cond.get("essential_dignity_score", 0) or 0
    malt = cond.get("maltreatment_count", 0) or 0
    retro = bool(cond.get("retrograde", False))
    if score < 0 or malt >= 2 or (score <= 0 and retro):
        return "afflicted"
    if score >= 4 and malt == 0:
        return "strong"
    return "mixed"


def firdaria_at(birth, target, is_day):
    """(major, sub) firdaria lords active on target date."""
    table = FIRDARIA_DAY if is_day else FIRDARIA_NIGHT
    seq = [(p.value if hasattr(p, "value") else str(p), y) for p, y in table]
    age = (target - birth).days / 365.2425
    total = sum(y for _, y in seq)
    age %= total
    cum = 0.0
    for i, (name, years) in enumerate(seq):
        if cum + years > age:
            into = age - cum
            piece = years / 7.0
            k = int(into // piece)
            sub = seq[(i + k) % len(seq)][0] if k < 7 else name
            return name, sub
        cum += years
    return seq[-1][0], seq[-1][0]


def extract(chart):
    """Pull the uniform feature set the rule table needs."""
    a = chart["analysis"]
    planets = chart["astronomy"]["planets"]
    asc = a["angles"]["Ascendant"]
    asc_idx = SIGNS.index(asc["sign"])
    feats = {
        "asc_sign": asc["sign"],
        "is_day": a["sect"]["type"] == "DAY",
        "temp": a["temperament"]["net_balance"],
        "waning": bool(a["syzygy"]["natal_phase"].get("is_waning")),
        "geniture": {k: v["total"] for k, v in
                     a["dignity"]["lord_of_geniture"]["scores"].items()},
        "aspects": a["aspects"],
        "topoi": {t["house"]: t for t in a["topical"]["twelve_topoi"]},
        "houses": {}, "signs": {}, "retro": {}, "oriental": {},
    }
    for name in SEVEN:
        p = planets[name]
        feats["houses"][name] = whole_sign_house(p["longitude"], asc_idx)
        feats["signs"][name] = sidx(p["longitude"])
        feats["retro"][name] = bool(p.get("is_retrograde"))
        ph = (p.get("classical") or {}).get("phasis") or {}
        feats["oriental"][name] = bool(ph.get("is_oriental"))
    return feats


def hard_hits(feats, malefic):
    n = 0
    for asp in feats["aspects"]:
        pa, pb = asp.get("planet_a"), asp.get("planet_b")
        if asp.get("type") in HARD and malefic in (pa, pb):
            other = pb if pa == malefic else pa
            if other in ("Sun", "Moon", "Mercury"):
                n += 1
    return n


def aspect_between(feats, x, y):
    for asp in feats["aspects"]:
        if {asp.get("planet_a"), asp.get("planet_b")} == {x, y}:
            return asp.get("type")
    return None


def statements(feats, birth):
    """THE RULE TABLE. Applied identically to every chart."""
    s = []
    add = s.append
    hot = feats["temp"].get("Hot_vs_Cold", 0)
    moist = feats["temp"].get("Moist_vs_Dry", 0)
    gen = feats["geniture"]
    houses, signs_of = feats["houses"], feats["signs"]
    topoi = feats["topoi"]

    # 1-3 body
    add("Your build runs lean/wiry rather than heavyset." if hot <= 0 else
        "Your build runs sturdy/muscular or fleshy rather than skinny.")
    add("You run cold - cold hands and feet, you layer up when others are fine."
        if hot <= 0 else
        "You run hot - you're the one opening windows and wearing shorts early.")
    add("Your skin and hair run dry." if moist <= 0 else
        "Your skin runs oily/moist rather than dry.")
    # 4 weak point
    add("Your body's weak point is your %s." % MELOTHESIA[feats["asc_sign"]])
    # 5 emotional axis
    sat, mar = hard_hits(feats, "Saturn"), hard_hits(feats, "Mars")
    if sat >= mar:
        add("Your mental-health axis is chronic worry and rumination, not temper.")
    else:
        add("Your mental-health axis is temper and impulsivity, not chronic worry.")
    # 6 conflict style
    lights_cadent = houses["Sun"] in (6, 12, 3, 9) or houses["Moon"] in (6, 12, 3, 9)
    add("Under pressure you go silent and remove yourself; being seen angry or "
        "emotional embarrasses you afterwards." if (lights_cadent or feats["waning"])
        else "Under pressure you confront on the spot; people know when you're angry.")
    # 7 health habits
    add("You research your own health and have taken supplements you researched "
        "yourself." if gen.get("Mercury", 0) >= 5 else
        "You avoid health research and doctors until something forces the issue.")
    # 8 father (day: Sun; night: Saturn)
    fsig = "Sun" if feats["is_day"] else "Saturn"
    fh, fg = houses[fsig], gen.get(fsig, 0)
    if fh in (6, 8, 12) or fg < 0:
        add("Your father was absent, diminished or unreliable - he did not provide "
            "the launch (money, status, guidance) a father is expected to.")
    elif fh in (1, 4, 7, 10) and fg >= 5:
        add("Your father was a strong, present figure who actively set you up in life.")
    else:
        add("Your father was present but conventional/distant - neither a launcher "
            "nor an absence.")
    # 9 mother (day: Moon; night: Venus)
    msig = "Moon" if feats["is_day"] else "Venus"
    mh, mg = houses[msig], gen.get(msig, 0)
    if mh in (6, 8, 12) or mg < 0:
        add("Your mother's care was impaired - by illness, hardship, her own "
            "limitations, or circumstances; there is quiet grief on that side.")
    elif mh in (1, 4, 7, 10) and mg >= 5:
        add("Your mother was a robust, reliable anchor whose support you never "
            "had to question.")
    else:
        add("Your mother was caring but constrained - support was real yet came "
            "with gaps or conditions.")
    # 10 siblings
    c3 = cond_class(topoi.get(3, {}).get("ruler_condition"))
    add({"afflicted": "You have no siblings, or no sibling you are close to as an adult.",
         "strong": "You have at least one sibling who is a genuine ally - among "
                   "your closest people.",
         "mixed": "Sibling relations are ordinary - neither allies nor estranged."}[c3])
    # 11 childhood home
    c4 = cond_class(topoi.get(4, {}).get("ruler_condition"))
    add({"afflicted": "Your childhood home was unstable or burdened - money trouble, "
                      "disruption, or conditions you didn't invite friends into.",
         "strong": "Your childhood home was a stable launching pad.",
         "mixed": "Your childhood home was ordinary - imperfect but functional."}[c4])
    # 12 childhood recognition
    c5 = cond_class(topoi.get(5, {}).get("ruler_condition"))
    add({"afflicted": "As a child your creative output was conditionally received - "
                      "praised when convenient, ignored otherwise - and you concluded "
                      "your real work wouldn't be recognized.",
         "strong": "As a child your talents were noticed and actively encouraged.",
         "mixed": "Your childhood talents got average encouragement."}[c5])
    # 13 inheritance / other people's money
    t8 = topoi.get(8, {})
    c8 = cond_class(t8.get("ruler_condition"))
    mal_in_8 = any(houses[m] == 8 for m in ("Mars", "Saturn"))
    ben_in_8 = any(houses[b] == 8 for b in ("Venus", "Jupiter"))
    if mal_in_8 or c8 == "afflicted":
        add("Inheritance and shared money are tangled for you: anything that comes "
            "through family or others arrives encumbered, disputed, or demanding "
            "your own labor/money to extract - or evaporates.")
    elif ben_in_8 and c8 == "strong":
        add("Inheritance/windfalls through others come to you cleanly.")
    else:
        add("Inheritance and shared money are a non-story for you either way.")
    # 14 writing vs speaking
    add("You communicate better in writing than live - in person you over-explain, "
        "rush, or stop mid-thought when you sense disinterest."
        if not feats["oriental"]["Mercury"] else
        "You're better live than in writing - quick on your feet, words come "
        "easiest out loud.")
    # 15 argue to think
    mm = aspect_between(feats, "Mercury", "Mars")
    ms = aspect_between(feats, "Mercury", "Saturn")
    if mm:
        add("You think BY arguing - debate sharpens your ideas, and friendly "
            "arguing has been a formative practice in your life.")
    elif ms:
        add("You think slowly and alone - debate flusters you; you need silence "
            "to reach conclusions.")
    else:
        add("Discussion neither helps nor hurts your thinking - you work things "
            "out internally either way.")
    # 16 authority
    sat_g = gen.get("Saturn", 0)
    sat_asp_sun = aspect_between(feats, "Saturn", "Sun")
    if sat_g < 0 or sat_asp_sun in ("Square", "Opposition"):
        add("You clash with or withdraw from authority; no mentor/protege "
            "relationship has ever worked out for you, and hypocrisy in "
            "institutions genuinely disgusts you.")
    elif sat_g >= 4:
        add("You work well under senior figures; at least one mentor materially "
            "advanced your life.")
    else:
        add("Authority is a non-issue - you neither seek nor fight it.")
    # 17 finishing
    modes = [signs_of[p] for p in SEVEN]
    n_card = sum(1 for m in modes if m in CARDINAL)
    n_fix = sum(1 for m in modes if m in FIXED)
    n_mut = sum(1 for m in modes if m in MUTABLE)
    if n_card >= max(n_fix, n_mut):
        add("You start far more than you finish - you have a literal graveyard of "
            "half-done projects (vehicles, builds, ideas) around you.")
    elif n_fix >= max(n_card, n_mut):
        add("You finish what you start - abandoned projects are rare for you.")
    else:
        add("Your projects don't get abandoned so much as endlessly mutated into "
            "different projects.")
    # 18 planning
    n_air = sum(1 for p in SEVEN if signs_of[p] in AIR)
    add("You don't plan long-range - you iterate, and you've paid for it in "
        "trial-and-error losses; five-year plans die on contact."
        if n_air <= 1 else
        "You're a natural long-range planner - you map before you move.")
    # 19 solitude
    add("You need hours of solitude per day, not minutes, and a private room of "
        "your own is non-negotiable." if lights_cadent else
        "You recharge around people - too much alone time visibly degrades you.")
    # 20-21 friends
    c11 = cond_class(topoi.get(11, {}).get("ruler_condition"))
    mal_in_11 = any(houses[m] == 11 for m in ("Mars", "Saturn"))
    ben_in_11 = any(houses[b] == 11 for b in ("Venus", "Jupiter"))
    if c11 == "afflicted" or mal_in_11:
        add("You have been genuinely blindsided by friends - a group or close "
            "friend turned on you without warning at least once.")
        add("Friend groups have been a net source of loss in your life - betrayal, "
            "obligation, or slow abandonment outweigh what they gave.")
    elif c11 == "strong" and ben_in_11:
        add("Friends are your luck - doors in your life open through your circle, "
            "and your groups have held for decades.")
        add("You read rooms well; social blindsides basically don't happen to you.")
    else:
        add("Your friendships are ordinary - some drift, no dramatic betrayals.")
        add("Groups neither bless nor burn you; you're a take-it-or-leave-it member.")
    # 22 money source
    t2 = topoi.get(2, {})
    r2 = t2.get("ruler_condition") or {}
    r2h = r2.get("house")
    src = {1: "your own solo skill, self-directed",
           2: "steady accumulation in one lane",
           3: "trade, driving, dealing, constant local motion",
           4: "family, land, property",
           5: "speculation, creative output, or entertainment",
           6: "day-labor, service work, or employment under others",
           7: "a partner or one-to-one clients",
           8: "other people's money - debt, settlements, managing others' assets",
           9: "distance - travel, teaching, publishing, or foreign connections",
           10: "an institution, a boss, a public position",
           11: "your network - friends, kin, patrons, alliances",
           12: "behind-the-scenes work, institutions, or isolated labor"}
    add("Your income has come through %s." % src.get(r2h, "mixed channels"))
    # 23 money retention
    c2 = cond_class(r2)
    add({"strong": "You keep what you earn: disciplined saver, debt-averse, good "
                   "credit - money quietly accumulates.",
         "afflicted": "Money leaks: feast-famine cycles, debt, and losses through "
                      "other people keep resetting you.",
         "mixed": "You hold money adequately - neither a hoarder nor a leak."}[c2])
    # 24 relationships
    c7 = cond_class(topoi.get(7, {}).get("ruler_condition"))
    ven_g = gen.get("Venus", 0)
    ven_hard = sum(1 for a2 in feats["aspects"]
                   if a2.get("type") in HARD and "Venus" in
                   (a2.get("planet_a"), a2.get("planet_b")) and
                   {a2.get("planet_a"), a2.get("planet_b")} & {"Mars", "Saturn"})
    if c7 == "afflicted" and (ven_hard >= 1 or ven_g < 4):
        add("Partnership is late or absent for you: by 30 you had little or no "
            "real relationship history, despite genuinely wanting it.")
    elif c7 == "strong" and ven_g >= 6:
        add("Partnership came early and continuously - you've rarely been single "
            "since your teens.")
    else:
        add("Your relationship history is ordinary - some relationships, "
            "average timing, nothing remarkable either way.")
    # 25 domestic desire
    ven_sign = SIGNS[signs_of["Venus"]]
    add("You specifically crave the full domestic package - home, partner, kids, "
        "animals, a settled place - it is not ambivalent."
        if ven_sign in ("Cancer", "Taurus") or houses["Venus"] in (4, 5)
        else "Freedom beats domesticity for you - the settled package has never "
             "been the actual dream.")
    # 26-29 dated windows
    for label_start, label_end, mid in WINDOWS:
        maj, sub = firdaria_at(birth, mid, feats["is_day"])
        q = gen.get(maj, 0) + gen.get(sub, 0)
        if q < 0:
            desc = "one of the HARSHER stretches of your adult life - grind, " \
                   "obstruction, bad luck, things breaking"
        elif q > 8:
            desc = "one of the LIGHTER stretches - support, expansion, things " \
                   "clicking with less resistance"
        else:
            desc = "a MIXED stretch - neither your worst nor your best"
        add("The period %s to %s was %s." % (label_start, label_end, desc))
    # 30 education
    c9 = cond_class(topoi.get(9, {}).get("ruler_condition"))
    jup_g = gen.get("Jupiter", 0)
    if jup_g < 0 or c9 == "afflicted":
        add("Your formal education was truncated or gapped - you did not take the "
            "credentialed path, and it cost you early.")
    elif jup_g >= 6 and c9 == "strong":
        add("Formal education carried you - degrees/credentials are load-bearing "
            "in your life.")
    else:
        add("Your education was conventional - finished, unremarkable, neither "
            "wound nor weapon.")
    return s


CHARTS = [
    ("REAL", "1996-08-13", "07:18"),
    ("DECOY-1", "1995-03-22", "14:45"),
    ("DECOY-2", "1997-11-08", "03:30"),
    ("DECOY-3", "1994-06-30", "20:15"),
]


def main():
    out_rows = []
    for tag, bdate, btime in CHARTS:
        print("computing %s (%s %s)..." % (tag, bdate, btime))
        d = generate_chart_data_object("Native", bdate, btime, "Fairfield", "CA",
                                       latitude=38.2494, longitude=-122.0397)
        feats = extract(d)
        y, m, dd = (int(x) for x in bdate.split("-"))
        stmts = statements(feats, date(y, m, dd))
        out_rows.append((tag, bdate, btime, stmts))

    rng = random.Random(4242)
    order = list(range(len(out_rows)))
    rng.shuffle(order)
    labels = ["A", "B", "C", "D"]

    lines = ["# Blind Statement Test",
             "",
             "Four statement lists. One is derived from a real birth chart; three are",
             "from decoy charts (same birthplace, different dates/times). All four were",
             "generated by the same fixed rule table - no hand-tuning.",
             "",
             "**Grade every statement in every list**: T (true of me), F (false), "
             "? (can't judge).",
             "Don't skip lists even if one 'feels' like you - the decoy scores ARE "
             "the experiment.",
             ""]
    key = {}
    for lab, idx in zip(labels, order):
        tag, bdate, btime, stmts = out_rows[idx]
        key[lab] = {"identity": tag, "birth": "%s %s" % (bdate, btime)}
        lines.append("## List %s" % lab)
        lines.append("")
        for i, st in enumerate(stmts, 1):
            lines.append("%s%d. [ ] %s" % (lab, i, st))
        lines.append("")

    test_path = os.path.join(os.getcwd(), "BARNUM_BLIND_TEST.md")
    key_path = os.path.join(os.getcwd(), "BARNUM_BLIND_TEST_KEY_DO_NOT_OPEN.json")
    with open(test_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(key_path, "w", encoding="utf-8") as f:
        json.dump(key, f, indent=2)
    print("wrote %s" % test_path)
    print("wrote %s (do not open until graded)" % key_path)


if __name__ == "__main__":
    main()
