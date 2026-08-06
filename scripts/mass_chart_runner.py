#!/usr/bin/env python3
"""
Mass Celebrity Chart Runner — Deterministic Engine Only
=========================================================
Runs the Auditor engine (deterministic, no LLM) on a large corpus of famous
individuals with known birth times. For each person, saves:
  1. Full technical_data JSON (complete forensic audit)
  2. Deterministic report markdown (ReportSynthesizer output)
  3. A structured claim extraction (binary, falsifiable claims)

This does NOT call the LLM. It runs only the deterministic traditional
astrology engine, which is fast and free.

Sources: Birth data from Astro-Databank (astro.com/astro-databank)
Rodden Ratings: AA = birth certificate, A = from memory, B = biography

Usage:
    cd E:\\code.projects\\astrology
    python scripts/mass_chart_runner.py
"""

import io
import json
import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

# Force UTF-8 on Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.forensic_engine import Auditor


# =============================================================================
# CELEBRITY CORPUS — All with documented birth times
# =============================================================================
# Format: name -> {date_str, time_str, city, state, latitude, longitude,
#                   rodden_rating, known_themes, source}
#
# Latitude/longitude provided for non-US cities so geocoding doesn't fail.
# known_themes: documented biographical facts for later scoring.
# =============================================================================

CELEBRITIES = {
    # --- ALREADY RUN (3 originals) ---
    "Steve Jobs": {
        "date_str": "1955-02-24",
        "time_str": "19:15",
        "city": "San Francisco",
        "state": "California",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Visionary technologist / industry disruptor",
            "Perfectionist with obsessive attention to design aesthetics",
            "Mercurial temperament — charismatic but harsh and exacting",
            "Adopted; complex, estranged relationship with biological father",
            "Pancreatic cancer diagnosis; died at 56",
            "Built one of the most valuable companies in human history",
            "Zen Buddhist, spiritual seeker, LSD experimentation in youth",
            "Reality distortion field — extraordinary persuasive power",
        ],
    },
    "Marilyn Monroe": {
        "date_str": "1926-06-01",
        "time_str": "09:30",
        "city": "Los Angeles",
        "state": "California",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Iconic global sex symbol and actress",
            "Profound insecurity beneath a luminous, magnetic surface",
            "Turbulent love life, three marriages, many affairs",
            "Orphaned and raised in foster care; father unknown/absent",
            "Barbiturate and alcohol dependency; severe mental health struggles",
            "Mysterious death at age 36 — probable overdose",
            "Extraordinary public magnetism; became a cultural archetype",
        ],
    },
    "Richard Nixon": {
        "date_str": "1913-01-09",
        "time_str": "21:35",
        "city": "Yorba Linda",
        "state": "California",
        "rodden_rating": "A",
        "source": "Astro-Databank: from memory",
        "known_themes": [
            "37th President of the United States",
            "Watergate scandal — first president to resign in disgrace",
            "Brilliant geopolitical strategist; opened China relations",
            "Paranoid, secretive personality; maintained enemies list",
            "Humble working-class Quaker upbringing",
            "Complex, tormented relationship with power and authority",
            "Extraordinary political comeback after crushing 1962 defeat",
        ],
    },
    # --- NEW BATCH: US-based celebrities (no lat/lon needed) ---
    "Abraham Lincoln": {
        "date_str": "1809-02-12",
        "time_str": "06:54",
        "city": "Hodgenville",
        "state": "Kentucky",
        "rodden_rating": "B",
        "source": "Astro-Databank: biography (various)",
        "known_themes": [
            "16th President of the United States",
            "Led the nation through the Civil War",
            "Abolished slavery via the Emancipation Proclamation",
            "Assassinated at Ford's Theatre",
            "Self-educated frontier lawyer, born in poverty",
            "Suffered severe depression throughout life",
            "Extraordinary public speaking and persuasion skills",
            "Lost multiple elections before winning the presidency",
        ],
    },
    "Elvis Presley": {
        "date_str": "1935-01-08",
        "time_str": "04:35",
        "city": "Tupelo",
        "state": "Mississippi",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "King of Rock and Roll — cultural revolution through music",
            "Extraordinary charisma and sexual magnetism on stage",
            "Deep attachment to his mother Gladys; devastated by her death",
            "Twin brother Jesse stillborn — survivor guilt",
            "Military service interrupted career peak",
            "Prescription drug addiction, dramatic physical decline",
            "Died at 42 at Graceland; heart failure / polypharmacy",
            "Deep Christian faith, gospel music devotion",
        ],
    },
    "Muhammad Ali": {
        "date_str": "1942-01-17",
        "time_str": "18:35",
        "city": "Louisville",
        "state": "Kentucky",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Greatest heavyweight boxer in history",
            "Extraordinary self-confidence and verbal showmanship",
            "Religious conversion to Islam; changed name from Cassius Clay",
            "Refused military draft on conscience — stripped of title",
            "Political activist, civil rights figure",
            "Parkinson's disease from age 42; long decline",
            "Three-time world heavyweight champion",
            "Beloved global humanitarian figure",
        ],
    },
    "Oprah Winfrey": {
        "date_str": "1954-01-29",
        "time_str": "04:30",
        "city": "Kosciusko",
        "state": "Mississippi",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Media mogul — most influential talk show host in history",
            "Overcame extreme childhood poverty and abuse",
            "First Black female billionaire",
            "Extraordinary empathy and emotional intelligence",
            "Weight struggles and public vulnerability",
            "Built a media empire (Harpo, OWN, O Magazine)",
            "Spiritual/self-help advocacy, New Thought influence",
            "Never married but long-term partnership with Stedman Graham",
        ],
    },
    "Donald Trump": {
        "date_str": "1946-06-14",
        "time_str": "10:54",
        "city": "Jamaica",
        "state": "New York",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "45th President of the United States, real estate mogul",
            "Extraordinary self-promotion and branding instinct",
            "Multiple bankruptcies yet projected wealth image",
            "Deeply polarizing public figure",
            "Three marriages, tabloid personal life",
            "Combative personality, public feuds, litigation-heavy",
            "Privileged upbringing, inherited family real estate empire",
            "TV celebrity (The Apprentice) before political career",
        ],
    },
    "Kurt Cobain": {
        "date_str": "1967-02-20",
        "time_str": "19:38",
        "city": "Aberdeen",
        "state": "Washington",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Lead singer of Nirvana, voice of Generation X",
            "Extraordinary raw musical talent and artistic authenticity",
            "Severe depression and chronic stomach pain",
            "Heroin addiction throughout adult life",
            "Parents' divorce at age 9 profoundly destabilized him",
            "Deeply uncomfortable with fame and celebrity",
            "Suicide at age 27",
            "Married Courtney Love — volatile, intense relationship",
        ],
    },
    "Michael Jackson": {
        "date_str": "1958-08-29",
        "time_str": "19:33",
        "city": "Gary",
        "state": "Indiana",
        "rodden_rating": "A",
        "source": "Astro-Databank: from mother's memory",
        "known_themes": [
            "King of Pop — best-selling music artist of all time",
            "Extraordinary dancing and performing ability from childhood",
            "Deeply troubled childhood, abusive father Joe Jackson",
            "Extreme plastic surgery, possible body dysmorphia",
            "Peter Pan complex — built Neverland Ranch",
            "Child abuse allegations and trials",
            "Prescription drug dependency; died at 50 from propofol",
            "Shy, reclusive private personality vs explosive stage presence",
        ],
    },
    "Beyoncé": {
        "date_str": "1981-09-04",
        "time_str": "10:00",
        "city": "Houston",
        "state": "Texas",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "One of the most successful recording artists in history",
            "Extraordinary work ethic and performance perfectionism",
            "Marriage to Jay-Z — power couple, survived infidelity",
            "Fierce public persona (Sasha Fierce) vs private personality",
            "Black identity and feminism as artistic pillars",
            "Started career in Destiny's Child, breakout as solo artist",
            "Multiple business ventures beyond music",
            "Controlled, strategic public image management",
        ],
    },
    "Bruce Lee": {
        "date_str": "1940-11-27",
        "time_str": "07:12",
        "city": "San Francisco",
        "state": "California",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Martial arts legend, created Jeet Kune Do",
            "Broke racial barriers in Hollywood as Asian leading man",
            "Extraordinary physical discipline and philosophical depth",
            "Died suddenly at 32 from cerebral edema",
            "Child actor in Hong Kong before US martial arts career",
            "Philosophy: 'Be like water' — adaptability as strength",
            "Intense training regimen, pushed body to absolute limits",
            "Cultural icon bridging East and West",
        ],
    },
    "Amelia Earhart": {
        "date_str": "1897-07-24",
        "time_str": "23:30",
        "city": "Atchison",
        "state": "Kansas",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "First woman to fly solo across the Atlantic Ocean",
            "Disappeared over the Pacific Ocean at age 39",
            "Pioneering feminist icon and adventurer",
            "Tomboy childhood, resisted gender conventions",
            "Father's alcoholism destabilized family",
            "Married publisher George Putnam — independent marriage",
            "Extraordinary courage and risk-taking",
            "Became a symbol of women's capability and independence",
        ],
    },
    "Martin Luther King Jr.": {
        "date_str": "1929-01-15",
        "time_str": "12:00",
        "city": "Atlanta",
        "state": "Georgia",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Civil rights leader, Nobel Peace Prize laureate",
            "Extraordinary oratory — 'I Have a Dream' speech",
            "Baptist minister, deep Christian theology",
            "Nonviolent resistance strategy inspired by Gandhi",
            "Assassinated at age 39 in Memphis",
            "FBI surveillance, personal life under intense scrutiny",
            "Emerged as moral conscience of a generation",
            "Born into middle-class Black Atlanta clergy family",
        ],
    },
    "Amy Winehouse": {
        "date_str": "1983-09-14",
        "time_str": "22:25",
        "city": "London",
        "state": "",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Extraordinary jazz/soul vocal talent",
            "Iconic retro image, beehive hairstyle",
            "Severe alcoholism and drug addiction",
            "Died at 27 from alcohol poisoning (27 Club)",
            "Tumultuous relationship with Blake Fielder-Civil",
            "Parents' divorce deeply affected her",
            "Album 'Back to Black' about heartbreak and self-destruction",
            "Raw, confessional songwriting style",
        ],
    },
    "John F. Kennedy": {
        "date_str": "1917-05-29",
        "time_str": "15:00",
        "city": "Brookline",
        "state": "Massachusetts",
        "rodden_rating": "A",
        "source": "Astro-Databank: from Rose Kennedy's diary",
        "known_themes": [
            "35th President of the United States",
            "Assassinated in Dallas at age 46",
            "Youngest elected president, Catholic",
            "Cuban Missile Crisis — brinkmanship diplomacy",
            "Chronic health problems (Addison's disease, back pain)",
            "Extramarital affairs, Marilyn Monroe connection",
            "Wealthy, privileged political dynasty family",
            "Extraordinary charisma and public appeal",
        ],
    },
    "Princess Diana": {
        "date_str": "1961-07-01",
        "time_str": "19:45",
        "city": "Sandringham",
        "state": "",
        "latitude": 52.8284,
        "longitude": 0.5151,
        "rodden_rating": "A",
        "source": "Astro-Databank: from mother's memory",
        "known_themes": [
            "Princess of Wales, married Prince Charles",
            "Died in Paris car crash at 36",
            "People's Princess — extraordinary public empathy",
            "Bulimia, self-harm, depression throughout marriage",
            "Parents' bitter divorce profoundly affected her",
            "Charitable work: landmines, AIDS, homelessness",
            "Media obsession and paparazzi pursuit",
            "Rejected by royal establishment, became antiestablishment icon",
        ],
    },
    "Albert Einstein": {
        "date_str": "1879-03-14",
        "time_str": "11:30",
        "city": "Ulm",
        "state": "",
        "latitude": 48.4011,
        "longitude": 9.9876,
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Revolutionary theoretical physicist — general relativity",
            "Nobel Prize in Physics (photoelectric effect)",
            "Late talker as child, struggled in rigid school systems",
            "Complex personal life — affair, divorce, remarriage to cousin",
            "Fled Nazi Germany, advocated for peace",
            "Deep philosophical and musical interests (violin)",
            "Eccentric, absent-minded professor archetype",
            "Pacifist who reluctantly urged atomic bomb development",
        ],
    },
    "Queen Elizabeth II": {
        "date_str": "1926-04-21",
        "time_str": "02:40",
        "city": "London",
        "state": "",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Longest-reigning British monarch (70 years)",
            "Extraordinary sense of duty and stoic composure",
            "Married Prince Philip for 73 years",
            "Navigated massive social change while preserving monarchy",
            "Emotionally reserved in public, warm in private",
            "Scandal-ridden family (Charles/Diana, Andrew, Harry/Meghan)",
            "Deep Christian faith, Christmas broadcasts",
            "Horses, corgis, and country life as personal passions",
        ],
    },
    "Napoleon Bonaparte": {
        "date_str": "1769-08-15",
        "time_str": "09:50",
        "city": "Ajaccio",
        "state": "",
        "latitude": 41.9267,
        "longitude": 8.7369,
        "rodden_rating": "B",
        "source": "Astro-Databank: church baptism record",
        "known_themes": [
            "Emperor of France, military genius",
            "Rose from minor Corsican nobility to rule Europe",
            "Extraordinary tactical brilliance and ambition",
            "Exiled twice (Elba, St. Helena)",
            "Deep love for Josephine despite infidelity",
            "Napoleonic Code — reformed legal systems across Europe",
            "Ultimately defeated by coalition at Waterloo",
            "Short stature mythology, compensatory drive",
        ],
    },
    "Winston Churchill": {
        "date_str": "1874-11-30",
        "time_str": "01:30",
        "city": "Woodstock",
        "state": "",
        "latitude": 51.8486,
        "longitude": -1.3544,
        "rodden_rating": "AA",
        "source": "Astro-Databank: biography with recorded time",
        "known_themes": [
            "Prime Minister of the UK during WWII",
            "Extraordinary wartime oratory and leadership",
            "Aristocratic background (Duke of Marlborough family)",
            "Suffered from 'Black Dog' depression",
            "Nobel Prize in Literature for historical writing",
            "Painter, bricklayer, and prolific writer",
            "Heavy drinker, cigar smoker — lived to 90",
            "Multiple political failures before WWII vindication",
        ],
    },
    "Nikola Tesla": {
        "date_str": "1856-07-10",
        "time_str": "00:00",
        "city": "Smiljan",
        "state": "",
        "latitude": 44.5667,
        "longitude": 15.3167,
        "rodden_rating": "C",
        "source": "Astro-Databank: midnight assumed (stroke of midnight per legend)",
        "known_themes": [
            "Pioneering electrical engineer — AC power system",
            "Extraordinary inventive genius, hundreds of patents",
            "Reclusive, eccentric, never married",
            "Obsessive-compulsive behaviors (multiples of 3)",
            "Died alone and impoverished in hotel room",
            "Rivalry with Edison, exploited by businessmen",
            "Visionary ideas ahead of his time (wireless energy)",
            "Photographic/eidetic memory, could visualize machines fully",
        ],
    },
    "Mahatma Gandhi": {
        "date_str": "1869-10-02",
        "time_str": "07:11",
        "city": "Porbandar",
        "state": "",
        "latitude": 21.6417,
        "longitude": 69.6293,
        "rodden_rating": "A",
        "source": "Astro-Databank: autobiography",
        "known_themes": [
            "Father of Indian independence, nonviolent resistance pioneer",
            "Lived ascetically, voluntary poverty, celibacy vow",
            "Lawyer trained in London, transformed by South Africa racism",
            "Assassinated by Hindu nationalist at 78",
            "Deep Hindu spiritual practice, Bhagavad Gita devotee",
            "Complex family life — criticized by own sons",
            "Salt March, Quit India movement — mass mobilization genius",
            "Global influence on civil rights and peace movements",
        ],
    },
    "Frida Kahlo": {
        "date_str": "1907-07-06",
        "time_str": "08:30",
        "city": "Mexico City",
        "state": "",
        "latitude": 19.4326,
        "longitude": -99.1332,
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Iconic Mexican painter, surrealist self-portraits",
            "Devastating bus accident at 18 caused lifelong pain",
            "Tumultuous marriage to Diego Rivera — affairs, divorce, remarriage",
            "Communist political activist",
            "Multiple miscarriages, unable to carry pregnancy",
            "Used art to process physical and emotional suffering",
            "Bisexual, defied gender conventions of her era",
            "Became a feminist icon posthumously",
        ],
    },
    "John Lennon": {
        "date_str": "1940-10-09",
        "time_str": "18:30",
        "city": "Liverpool",
        "state": "",
        "latitude": 53.4084,
        "longitude": -2.9916,
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Co-founder of the Beatles, greatest band in history",
            "Extraordinary songwriting genius with Paul McCartney",
            "Abandoned by father, raised by aunt Mimi after mother's death",
            "Assassinated at 40 by Mark David Chapman",
            "Peace activist — 'Imagine', bed-ins for peace",
            "Volatile temper, aggressive in early life",
            "Relationship with Yoko Ono was defining partnership",
            "Witty, acerbic, intellectually provocative",
        ],
    },
    "Audrey Hepburn": {
        "date_str": "1929-05-04",
        "time_str": "03:00",
        "city": "Brussels",
        "state": "",
        "latitude": 50.8503,
        "longitude": 4.3517,
        "rodden_rating": "A",
        "source": "Astro-Databank: from family",
        "known_themes": [
            "Iconic actress — Breakfast at Tiffany's, Roman Holiday",
            "Extraordinary grace, elegance, and style icon",
            "Father abandoned family when she was young",
            "Survived Nazi occupation of Netherlands as a child",
            "UNICEF Goodwill Ambassador, devoted humanitarian work",
            "Two marriages ended in divorce, longed for stable family",
            "Trained ballet dancer before film career",
            "Deeply private, retreated from Hollywood to raise children",
        ],
    },
    "Marie Curie": {
        "date_str": "1867-11-07",
        "time_str": "12:00",
        "city": "Warsaw",
        "state": "",
        "latitude": 52.2297,
        "longitude": 21.0122,
        "rodden_rating": "B",
        "source": "Astro-Databank: noon chart (unverified time)",
        "known_themes": [
            "First woman to win a Nobel Prize, won two in different sciences",
            "Discovered radium and polonium",
            "Extreme dedication to research, worked in a shed laboratory",
            "Husband Pierre killed in horse cart accident",
            "Affair with married physicist Paul Langevin — public scandal",
            "Died of aplastic anemia from radiation exposure",
            "Faced intense sexism in French academic establishment",
            "Polish patriot, named polonium after her homeland",
        ],
    },
    "Jimi Hendrix": {
        "date_str": "1942-11-27",
        "time_str": "10:15",
        "city": "Seattle",
        "state": "Washington",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Greatest electric guitarist in history",
            "Revolutionary approach to sound and feedback",
            "Difficult childhood — parents divorced, mother died young",
            "Military service (Army paratrooper) before music career",
            "Drug and alcohol use throughout career",
            "Died at 27 from asphyxiation after barbiturate overdose",
            "Left-handed, played right-handed guitar upside down",
            "Three years of fame changed music forever",
        ],
    },
    "Freddie Mercury": {
        "date_str": "1946-09-05",
        "time_str": "05:00",
        "city": "Stone Town",
        "state": "",
        "latitude": -6.1622,
        "longitude": 39.1921,
        "rodden_rating": "C",
        "source": "Astro-Databank: approximate, from interview",
        "known_themes": [
            "Lead singer of Queen, extraordinary vocal range",
            "Flamboyant, charismatic live performer",
            "Born Farrokh Bulsara in Zanzibar to Parsi Indian family",
            "Died of AIDS-related bronchopneumonia at 45",
            "Private about personal life despite public flamboyance",
            "Bisexual, longtime partner Jim Hutton",
            "Dental feature (extra teeth) he refused to fix for vocal reasons",
            "Bohemian Rhapsody — revolutionary operatic rock",
        ],
    },
    "Theodore Roosevelt": {
        "date_str": "1858-10-27",
        "time_str": "19:45",
        "city": "New York City",
        "state": "New York",
        "rodden_rating": "AA",
        "source": "Astro-Databank: family bible",
        "known_themes": [
            "26th President — youngest to assume office at 42",
            "Extraordinarily vigorous, athletic, adventurous lifestyle",
            "Led Rough Riders in Spanish-American War",
            "Trust-buster, progressive reformer, conservation champion",
            "Wife and mother died on the same day (Valentine's Day 1884)",
            "Nobel Peace Prize for mediating Russo-Japanese War",
            "Nearly blind in one eye from boxing in the White House",
            "Shot during speech, finished the speech before going to hospital",
        ],
    },
    "Cleopatra VII": {
        "date_str": "-0068-01-01",
        "time_str": "12:00",
        "city": "Alexandria",
        "state": "",
        "latitude": 31.2001,
        "longitude": 29.9187,
        "rodden_rating": "X",
        "source": "Speculative: year approximate, time unknown",
        "known_themes": [
            "Last active ruler of Ptolemaic Egypt",
            "Extraordinary political intelligence and diplomatic skill",
            "Relationships with Julius Caesar and Mark Antony",
            "Died by suicide (asp bite legend)",
            "Polyglot — spoke 9+ languages",
            "Controlled vast wealth and resources",
        ],
        "skip": True,  # Birth data too speculative
    },
    "Elon Musk": {
        "date_str": "1971-06-28",
        "time_str": "06:00",
        "city": "Pretoria",
        "state": "",
        "latitude": -25.7461,
        "longitude": 28.1881,
        "rodden_rating": "C",
        "source": "Astro-Databank: rectified, disputed",
        "known_themes": [
            "Tech billionaire — Tesla, SpaceX, X/Twitter",
            "Extraordinary ambition: Mars colonization, neural interfaces",
            "Volatile public persona, provocative social media",
            "Multiple marriages and many children",
            "Difficult relationship with father Errol Musk",
            "Workaholic, sleeps at factories during production crises",
            "South African upbringing, bullied severely as child",
            "Polarizing figure — genius vs reckless depending on view",
        ],
    },
    "Che Guevara": {
        "date_str": "1928-06-14",
        "time_str": "03:05",
        "city": "Rosario",
        "state": "",
        "latitude": -32.9442,
        "longitude": -60.6505,
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Marxist revolutionary, Cuban Revolution leader",
            "Trained physician who chose guerrilla warfare",
            "Iconic image became global symbol of rebellion",
            "Executed in Bolivia at 39",
            "Severe asthma throughout life, refused to let it limit him",
            "Idealistic, ruthless, intellectually rigorous",
            "Motorcycle journey across South America radicalized him",
            "Wrote extensively — diaries, political theory",
        ],
    },
    "Billie Holiday": {
        "date_str": "1915-04-07",
        "time_str": "02:30",
        "city": "Philadelphia",
        "state": "Pennsylvania",
        "rodden_rating": "A",
        "source": "Astro-Databank: from mother",
        "known_themes": [
            "Greatest jazz vocalist of the 20th century",
            "Traumatic childhood — sexual abuse, mother in prison",
            "Heroin and alcohol addiction throughout adult life",
            "Died at 44 from cirrhosis; arrested on deathbed for heroin",
            "'Strange Fruit' — first great protest song",
            "Abusive relationships with men throughout life",
            "Voice deteriorated but gained emotional depth with age",
            "Posthumous icon of Black artistry and resilience",
        ],
    },
    "Carl Jung": {
        "date_str": "1875-07-26",
        "time_str": "19:32",
        "city": "Kesswil",
        "state": "",
        "latitude": 47.5991,
        "longitude": 9.3194,
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Founder of analytical psychology — archetypes, collective unconscious",
            "Break with Freud was defining professional trauma",
            "Deep interest in alchemy, mythology, astrology, mysticism",
            "Experienced visions and near-psychotic episodes (Red Book period)",
            "Introverted personality who explored the inner world",
            "Long marriage to Emma Jung plus affair with Toni Wolff",
            "Tower at Bollingen — retreated to build stone tower by hand",
            "Influenced 20th-century culture: personality types, shadow work",
        ],
    },
    "Walt Disney": {
        "date_str": "1901-12-05",
        "time_str": "00:35",
        "city": "Chicago",
        "state": "Illinois",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Created Mickey Mouse, founded Disney entertainment empire",
            "Extraordinary imagination and storytelling vision",
            "Demanding perfectionist, drove employees hard",
            "Multiple early business failures before breakthrough",
            "Difficult childhood, abusive father, frequent family moves",
            "Anti-union, conservative political views",
            "Died of lung cancer at 65; heavy smoker",
            "Transformed animation, theme parks, and family entertainment",
        ],
    },
    "Janis Joplin": {
        "date_str": "1943-01-19",
        "time_str": "09:45",
        "city": "Port Arthur",
        "state": "Texas",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Iconic blues/rock vocalist — raw, powerful voice",
            "Bullied and ostracized in high school for being different",
            "Alcoholism and heroin addiction throughout career",
            "Died at 27 from heroin overdose (27 Club)",
            "Desperately wanted love and acceptance",
            "Bisexual, defied gender norms in conservative Texas",
            "Counterculture icon, Woodstock performer",
            "Southern Pearl — combined vulnerability with ferocity",
        ],
    },
    "Leonardo DiCaprio": {
        "date_str": "1974-11-11",
        "time_str": "02:47",
        "city": "Los Angeles",
        "state": "California",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Academy Award-winning actor (The Revenant)",
            "Child actor who became one of Hollywood's biggest stars",
            "Environmental activist — climate change advocacy",
            "Pattern of dating much younger women",
            "Raised by single mother, close relationship with her",
            "Selective about roles, works with top directors",
            "Private personal life despite massive fame",
            "Titanic made him a global teenage heartthrob",
        ],
    },
    "Lady Gaga": {
        "date_str": "1986-03-28",
        "time_str": "09:53",
        "city": "New York City",
        "state": "New York",
        "rodden_rating": "AA",
        "source": "Astro-Databank: birth certificate",
        "known_themes": [
            "Pop superstar and Oscar-winning actress",
            "Extraordinary reinvention and visual artistry",
            "Bullied in school, felt like an outsider",
            "Fibromyalgia and chronic pain conditions",
            "LGBTQ+ icon and advocate",
            "Italian-American family, close to parents",
            "Sexual assault survivor, PTSD",
            "Classically trained musician who chose pop provocation",
        ],
    },
}


def run_chart(name: str, data: dict) -> dict:
    """Run Auditor.generate_full_nativity for a celebrity."""
    kwargs = {
        "date_str": data["date_str"],
        "time_str": data["time_str"],
        "city": data["city"],
        "state": data.get("state", ""),
        "name": "Subject",  # Anonymized
    }
    if "latitude" in data:
        kwargs["latitude"] = data["latitude"]
    if "longitude" in data:
        kwargs["longitude"] = data["longitude"]

    result = Auditor.generate_full_nativity(**kwargs)
    if "error" in result:
        raise RuntimeError(f"Chart calculation failed for {name}: {result['error']}")
    return result


def extract_key_claims(result: dict) -> List[Dict[str, str]]:
    """
    Extract structured, falsifiable claims from the deterministic engine output.
    These are the claims that can be scored against known biography.
    """
    claims = []
    td = result.get("technical_data", {})
    analysis = td.get("analysis", {})

    # 1. Sect
    sect = analysis.get("sect", {})
    sect_type = sect.get("type", "UNKNOWN")
    claims.append({
        "id": "SECT_01",
        "category": "constitution",
        "claim": f"This is a {sect_type.lower()} chart (born {'during daylight' if sect_type == 'DAY' else 'at night'})",
        "source": "Sect determination by Sun altitude",
    })

    # 2. Temperament
    temp = analysis.get("temperament", {})
    if isinstance(temp, dict):
        dominant = temp.get("dominant_humor") or temp.get("dominant_temperament", "")
        qualities = temp.get("primary_qualities", [])
        if dominant:
            claims.append({
                "id": "TEMP_01",
                "category": "constitution",
                "claim": f"Dominant temperament: {dominant}",
                "source": "TemperamentEngine calculation",
            })
        if qualities:
            claims.append({
                "id": "TEMP_02",
                "category": "constitution",
                "claim": f"Primary qualities: {', '.join(str(q) for q in qualities) if isinstance(qualities, list) else str(qualities)}",
                "source": "TemperamentEngine calculation",
            })

    # 3. Almuten Figuris
    dignity = analysis.get("dignity", {})
    almuten = dignity.get("almuten", {})
    if isinstance(almuten, dict):
        almuten_planet = almuten.get("planet") or almuten.get("name", "")
        if almuten_planet:
            claims.append({
                "id": "ALM_01",
                "category": "identity",
                "claim": f"Soul Guardian (Almuten Figuris): {almuten_planet}",
                "source": "AlmutenEngine calculation",
            })

    # 4. Teams (constructive vs destructive)
    teams = analysis.get("teams", {})
    if isinstance(teams, dict):
        constructive = teams.get("constructive_team", [])
        destructive = teams.get("destructive_team", [])
        if constructive:
            team_names = [p.get("name", str(p)) if isinstance(p, dict) else str(p)
                          for p in constructive]
            claims.append({
                "id": "TEAM_01",
                "category": "identity",
                "claim": f"Constructive (supporting) planets: {', '.join(team_names)}",
                "source": "Sect-based team assignment",
            })
        if destructive:
            team_names = [p.get("name", str(p)) if isinstance(p, dict) else str(p)
                          for p in destructive]
            claims.append({
                "id": "TEAM_02",
                "category": "identity",
                "claim": f"Destructive (challenging) planets: {', '.join(team_names)}",
                "source": "Sect-based team assignment",
            })

    # 5. Vitality
    vitality = analysis.get("vitality", {})
    if isinstance(vitality, dict):
        hyleg = vitality.get("hyleg", {})
        if isinstance(hyleg, dict) and hyleg.get("name"):
            claims.append({
                "id": "VIT_01",
                "category": "vitality",
                "claim": f"Hyleg (Source of Life): {hyleg['name']}",
                "source": "HylegAlcocodenEngine",
            })
        rating = vitality.get("vitality_rating", "")
        if rating:
            claims.append({
                "id": "VIT_02",
                "category": "vitality",
                "claim": f"Vitality rating: {rating}",
                "source": "HylegAlcocodenEngine",
            })

    # 6. Per-planet dignity scores (top planet)
    pf = td.get("planets_forensic", [])
    if pf:
        scored = []
        for p in pf:
            if isinstance(p, dict):
                name_val = p.get("name", "")
                dig = p.get("dignities", {})
                if isinstance(dig, dict):
                    total = dig.get("total_score")
                    if total is not None:
                        scored.append((name_val, int(total)))
        if scored:
            scored.sort(key=lambda x: x[1], reverse=True)
            best = scored[0]
            worst = scored[-1]
            claims.append({
                "id": "DIG_01",
                "category": "identity",
                "claim": f"Strongest planet by dignity: {best[0]} (score {best[1]})",
                "source": "DignityCalculator essential + accidental",
            })
            claims.append({
                "id": "DIG_02",
                "category": "identity",
                "claim": f"Weakest planet by dignity: {worst[0]} (score {worst[1]})",
                "source": "DignityCalculator essential + accidental",
            })

    # 7. Topical conditions (house ruler conditions)
    topical = analysis.get("topical", {})
    if isinstance(topical, dict):
        topoi = topical.get("topoi", [])
        if isinstance(topoi, list):
            for topos in topoi:
                if not isinstance(topos, dict):
                    continue
                house_num = topos.get("house")
                condition_tag = topos.get("condition_tag", "")
                ruler = topos.get("ruler", "")
                sign = topos.get("sign", "")
                if house_num and condition_tag:
                    claims.append({
                        "id": f"TOP_{house_num:02d}",
                        "category": "topical",
                        "claim": f"House {house_num} ({sign}): ruler {ruler}, condition: {condition_tag}",
                        "source": "TopicalEngine",
                    })

    return claims


def main():
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "chart_outputs",
        "mass_test",
    )
    os.makedirs(output_dir, exist_ok=True)

    # Track results
    results_summary = []
    success_count = 0
    fail_count = 0
    skip_count = 0

    def is_precise_time(data_dict):
        if data_dict.get("skip"):
            return False
        time_str = data_dict.get("time_str", "")
        if time_str:
            try:
                hh, mm = map(int, time_str.split(":"))
                if mm in (0, 30):
                    return False
            except ValueError:
                pass
        return True

    total = sum(1 for v in CELEBRITIES.values() if is_precise_time(v))
    print("=" * 70)
    print(f"  MASS CELEBRITY CHART RUNNER — {total} subjects")
    print("  Engine: Auditor (deterministic, no LLM)")
    print(f"  Output: {output_dir}")
    print("=" * 70)
    print()

    for name, data in CELEBRITIES.items():
        if data.get("skip"):
            print(f"  SKIP: {name} (birth data too speculative)")
            skip_count += 1
            continue

        time_str = data.get("time_str", "")
        if time_str:
            try:
                hh, mm = map(int, time_str.split(":"))
                if mm in (0, 30):
                    print(f"  SKIP: {name} (birth time lands on hour/half hour: {time_str})")
                    skip_count += 1
                    continue
            except ValueError:
                pass

        slug = name.lower().replace(" ", "_").replace(".", "")
        print(f"  [{success_count + fail_count + 1}/{total}] {name}... ", end="", flush=True)

        try:
            result = run_chart(name, data)
            td = result.get("technical_data", {})
            ht = result.get("human_translation", {})

            # Save full technical data
            td_path = os.path.join(output_dir, f"{slug}_technical.json")
            with open(td_path, "w", encoding="utf-8") as f:
                json.dump(td, f, indent=2, default=str)

            # Save deterministic report
            report_md = ht.get("report_markdown", "")
            report_path = os.path.join(output_dir, f"{slug}_report.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# Deterministic Report: {name}\n")
                f.write(f"**Rodden Rating:** {data.get('rodden_rating', 'N/A')}\n")
                f.write(f"**Source:** {data.get('source', 'N/A')}\n\n")
                f.write("---\n\n")
                f.write(report_md)

            # Extract structured claims
            claims = extract_key_claims(result)
            claims_path = os.path.join(output_dir, f"{slug}_claims.json")
            with open(claims_path, "w", encoding="utf-8") as f:
                json.dump({
                    "subject": name,
                    "rodden_rating": data.get("rodden_rating", ""),
                    "known_themes": data.get("known_themes", []),
                    "engine_claims": claims,
                }, f, indent=2, default=str)

            # Summarize
            meta = td.get("meta", {})
            sect = td.get("analysis", {}).get("sect", {}).get("type", "?")
            n_claims = len(claims)

            results_summary.append({
                "name": name,
                "status": "OK",
                "sect": sect,
                "claims_extracted": n_claims,
                "report_length": len(report_md),
                "rodden_rating": data.get("rodden_rating", ""),
            })

            success_count += 1
            print(f"OK ({n_claims} claims, {len(report_md)} chars)")

        except Exception as e:
            fail_count += 1
            error_msg = str(e)
            print(f"FAILED: {error_msg[:80]}")
            results_summary.append({
                "name": name,
                "status": "FAILED",
                "error": error_msg,
                "rodden_rating": data.get("rodden_rating", ""),
            })
            traceback.print_exc()

    # Save master summary
    summary_path = os.path.join(output_dir, "run_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "run_timestamp": datetime.now().isoformat(),
            "total_attempted": total,
            "success": success_count,
            "failed": fail_count,
            "skipped": skip_count,
            "results": results_summary,
        }, f, indent=2, default=str)

    # Save known themes (answer key)
    answer_key_path = os.path.join(output_dir, "answer_key.json")
    answer_key = {}
    for name, data in CELEBRITIES.items():
        if not data.get("skip"):
            answer_key[name] = {
                "known_themes": data.get("known_themes", []),
                "rodden_rating": data.get("rodden_rating", ""),
                "source": data.get("source", ""),
            }
    with open(answer_key_path, "w", encoding="utf-8") as f:
        json.dump(answer_key, f, indent=2, default=str)

    print()
    print("=" * 70)
    print(f"  COMPLETE: {success_count} OK / {fail_count} FAILED / {skip_count} SKIPPED")
    print(f"  Output directory: {output_dir}")
    print(f"  Summary: {summary_path}")
    print(f"  Answer key: {answer_key_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
