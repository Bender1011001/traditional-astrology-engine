# Doctrine Source Manifest

## Publication rule

A named traditional authority is not sufficient provenance. A customer-facing
claim may be called text-verified only when the repository records a specific
edition, a stable source, a precise book/chapter or page location, and the hash
of the inspected source text. OCR is an index; page images control when glyphs
or wording are unclear.

The machine-readable registry is
`src/database/data/doctrine_sources.json`.

## Verified in this pass

### William Lilly, *Christian Astrology* (1647)

- Internet Archive identifier:
  `bim_early-english-books-1641-1700_christian-astrology-_lilly-william_1647`
- Inspected OCR SHA-256:
  `f661a0a140950cc53be09a8400ba87578f35b74b8724818b9f356cf6dd155e4d`
- Reception was located at p. 112. Lilly distinguishes reception by house,
  triplicity, term, face, and other essential dignity.
- The planetary chapters and tables contain the dignity and sect-dependent
  material used by the project. Long-s OCR and astrological glyph loss require
  visual page confirmation before exact quotation.
- The facsimile page for the *Two necessary Tables of the Signes* (printed
  p. 116) and Lilly's explanation (printed pp. 117-118) were visually
  inspected. The engine's one-based pitted and azimene lists match the printed
  table for the chart-relevant signs. Lilly does not apply every flag to every
  planet: light/dark/smoky/void chiefly concern the Ascendant and Moon; pitted
  degrees concern the Ascendant, Moon, or Ascendant ruler; and azimene degrees
  are offered as retrospective corroboration through those significators or
  the principal lord when a bodily defect is already known. They are not a
  standalone license to predict disability. Increasing-fortune degrees are
  relevant to the second cusp or ruler, Jupiter, and Fortune.
- A second public-domain Wellcome Library copy was inspected through Internet
  Archive item `b30338724`; its OCR SHA-256 is
  `7c08b55359c41049c5d43901b8da869a326f8eb852e4a30603a4b698533626aa`.
  Book III, Chapter CIV, printed pp. 527-531, gives Lilly's Hyleg and
  Alcocoden procedure. He rejects the eighth and twelfth as hylegical places
  for the luminaries, preserves the Arabic giver-of-years doctrine, and says
  an angular, strong, fortunate Alcocoden may give its greater years. The
  planetary table on printed p. 80 gives Mercury 76 greater years, 48 mean
  years, and 20 least years.
- The limitation is part of the source, not a modern deletion: Lilly says the
  native might live the allotted years if no obstructive direction, sudden
  casualty, or general calamity intervenes, then explicitly says he is not
  satisfied that the Hyleg, Anareta, or Alcocoden can yet be selected with
  certainty. The customer report therefore prints the exact 76-year Mercury
  branch, the failed rival Venus branch, and the model's anaretic candidate,
  while identifying the configured whole-sign aspect fallback used by the
  Mercury branch.

### Ptolemy, *Tetrabiblos*, Ashmand translation (1822)

- Internet Archive identifier: `ptolemystetrabi01procgoog`
- Inspected OCR SHA-256:
  `152221d620bf34a3c942eaf62818bfb4e995fbd0ba48aab837d2c8a84d7382c6`
- Book I, Chapter VII assigns Saturn to day and Mars to night as a moderating
  mixture. This supports "more moderated in sect," not "ally" or "benefic."
- Book I, Chapter XXI supplies Ptolemy's triplicity arrangement.
- Book I, Chapters XXIII-XXIV distinguish and tabulate term systems.
- Book I, Chapter XVI defines opposition, trine, quartile, and sextile by
  degree distance. This verifies the geometry only; project orb allowances,
  application/separation, and conjunction handling remain configured details.
- Book I, Chapter X assigns Perseus generally the nature of Jupiter and Saturn
  and separately assigns Mars-Mercury to the nebula in the sword hilt. Algol is
  in the Gorgon's head, not the sword hilt. Book III, Chapter IX makes the harsh
  Gorgon judgment conditional on Mars being near it inside a larger anaretic
  configuration. An Algol-Midheaven contact alone does not satisfy that rule.
  The premium report therefore uses a disclosed one-degree ecliptic orb,
  Ptolemy's Jupiter-Saturn nature, and no automatic violent-death inference.
- This is a public-domain English translation through Proclus' paraphrase, not
  a critical Greek edition. That limitation must remain explicit.

Book IV, Chapter X was inspected for prorogations and distributors. Ptolemy
assigns different prorogators to different event classes, measures Ascendant
distances by the ascensional times of the latitude, allows a planet's bodily or
aspectual ray to govern after reaching the prorogation, and includes the ruler
of the occupied term as a participant. The engine had mislabeled its
latitude-free zodiacal oblique-ascension directions as “Placidus” and selected
the partner by whichever planet happened to be found first inside a sampled
three-degree orb. The method is now honestly labeled configured zodiacal OA,
and the partner is the last directed ray to have reached the Ascendant. Only
the current Ascendant bound distributor is admitted to the customer report;
the other primary-direction outputs remain held pending a fuller formula audit.

### Dorotheus of Sidon, *Carmen Astrologicum*, Book I

- David Pingree's 1976 English translation, in Deborah Houlding's searchable
  2013 reproduction, was inspected and hashed as
  `33bf2b057257de999142861ad222056b1f092397760662b611132c2e5e284c82`.
- Book I.1 gives the sect-ordered triplicity rulers; I.5 gives Dorotheus's
  hierarchy of good, intermediate, and worst places; I.22-I.24 applies the
  rulers of the Sun by day or Moon by night to fortune, property, and elevation.
- The first and second rulers are contrasted for the beginning and later
  outcome of the native's condition. The third ruler participates in the whole
  testimony. The inspected text does **not** divide life into equal early,
  middle, and late thirds or assign the participating ruler a fixed final third.
- The customer report therefore publishes a first/second/participant judgment,
  with the actual natal places and conditions, and no invented age boundaries.
  The reproduction is a copyrighted modern translation for internal study; it
  does not substitute for independent checking of the Arabic, Greek, or Latin.

### Abraham Ibn Ezra, *Book of Revolution* (Sela critical edition, 2014)

- Shlomo Sela's parallel Hebrew-English critical edition was inspected; the
  PDF SHA-256 is
  `58152334a828879e52a02e195589ee03189d681ea637572e08548dfd05403738`.
- Section 1 defines the annual revolution as the moment the Sun returns to its
  natal degree and minute and requires casting the return Ascendant. Section 4
  compares the sect-light triplicity ruler's condition at birth and return.
  Section 15 makes the ruler of the return Ascendant a witness and compares the
  return with the natal Ascendant and annual terminal/profected sign. Section
  21 makes annual testimony shorter-lived and subordinate to natal promises.
- The old report mixed this Western annual-revolution framework with a
  Tajika-style Muntha ruler, arbitrary point weights, and an unsupported
  “Morin handover.” Those hybrid claims were removed. The report now publishes
  the exact return Ascendant, its ruler and condition, all seven return planets'
  whole-sign overlays, and the required natal/return triplicity comparison.
  Because residence-at-return is not collected, it explicitly discloses that
  natal coordinates are being used as a location proxy.
- Section 4 also preserves a real later doctrine that the three sect-light
  triplicity rulers govern first, middle, and last relative portions of life.
  This is not Dorotheus I.22's wording. The report now shows both methods as a
  historical fork: Dorotheus's first/second fortune-course judgment and Ibn
  Ezra's later three-phase scheme. Exact phase boundaries are not invented;
  the separate Lilly-scoped longevity chapter publishes the numerical branches
  actually produced by the engine.

## Not yet text-verified

The existing code and research notes name Dorotheus outside the inspected Book
I passages, Valens outside inspected timing passages, Bonatti, Abu Ma'shar,
Ibn Ezra outside the inspected critical-edition passages, Paulus outside inspected chapters, al-Biruni outside inspected sections,
Picatrix outside the selected chapter, and Agrippa. Those names are not enough.
Until an edition and exact location are entered in the registry, the new report
must call the relevant rule a configured project method rather than claim that
it perfectly reproduces the original authority.

## Binder1 inspection added in the second pass

`docs/research/Binder1.txt` is the canonical Binder. The root `Binder1.txt` is
an exact prefix that omits 675,597 bytes of later material. The canonical Binder
contains 35,105 lines, 28 detected reference boundaries, and 1,164 detected
URLs. It is therefore a valuable discovery and source-routing corpus, but not a
single primary text. The generated audit is under
`artifacts/binder-corpus-audit/`.

The Binder led to a Project Hindsight translation of Paulus Alexandrinus. Its
title pages and Chapter 24, *On the Tabular Exposition of the Twelve Places*,
were inspected. Paulus explicitly begins the places from the Horoskopos by
whole signs and supplies topics and planet-in-place delineations. This supports
the report's whole-sign topical framework. It does not independently verify the
project's entire consolidated topic vocabulary or its condition-band heuristic.
The source is a copyrighted Robert Schmidt translation, third revised edition
(1995), and is registered for internal verification only.

Binder candidates for Valens Book IV and Bonatti Parts I/IV were also inspected
at the metadata/title-page level. They are copyrighted Project Hindsight
translations. They remain candidates until the exact rules used by the engine
are compared chapter by chapter and, where possible, checked against Greek or
Latin editions.

Valens Book IV was then inspected more deeply for the timing features exposed
to customers. Chapters 4-7 directly cover releasing from Fortune and Spirit,
Loosing of the Bond, and the sign-period years. These portions now have
`translation_inspected` status for Zodiacal Releasing. The text does not justify
treating every peak chapter as guaranteed eminence or every difficult chapter
as a concrete crisis.

The decennial layer was then checked against Mark T. Riley's complete
preliminary translation (2010 release, based on Kroll 1908 and Pingree 1986),
with Schmidt Book IV chapter 26 as a comparison. The transmitted major period
is 129 months, or 10 years 9 months. Its planetary month shares are Saturn 30,
Jupiter 12, Mars 15, Sun 19, Venus 8, Mercury 20, and Moon 25; these total 129.
The old engine converted each month to an uninterrupted 30-day block, dropping
intercalary days and moving every later civil date early. It now advances by
129 civil calendar months and uses the same calendar-month arithmetic for the
sub-period shares. The former post-seven-period jump to the fourth ruler was
removed because the inspected fourth-ruler restart belongs to a different
lunar-quarter method; the decennial zodiacal sequence repeats from its apheta.
Riley labels the detailed computational exposition a fifth-century addition,
although that addition says the method is also found in Valens. The report must
therefore call it a Valens-tradition transmission and preserve that caveat.

The annual sign rotation is registered from Paulus chapter 31: the first year
is assigned to the Horoskopos, each subsequent year advances one sign, and the
thirteenth returns to the Horoskopos. This verifies the annual rotation shown
in the customer report. It does not yet verify every monthly or daily extension
computed elsewhere in the engine.

Paulus chapter 24 was also checked place by place for the planetary joys. It
explicitly assigns Hermes/Mercury to the first, the Moon to the third,
Aphrodite/Venus to the fifth, Ares/Mars to the sixth, the Sun to the ninth,
Zeus/Jupiter to the eleventh, and Kronos/Saturn to the twelfth. This verifies
the joy-house table used by the engine. A joy remains a place-based affinity;
it does not cancel essential debility, sect, maltreatment, or contrary
testimony.

The same chapter's chart-relevant planet-in-place passages were inspected
against the facing page images rather than inferred from the generic house
topics. For the Fairfield test nativity this verifies Mercury in the first,
Jupiter in the fifth, Saturn in the eighth, Mars and Venus in the eleventh,
and the Sun and Moon in the twelfth. The implementation preserves the source's
conditions: Mars's harsh daytime branch is used because the nativity is diurnal;
Venus's favorable promise is damaged when malefic rays scrutinize her; and the
Moon's severer twelfth-place result is activated only when malefic regard or
application is actually present. Dignity, sect, motion, and aspect quality are
printed as modifiers. They do not silently delete a severe place rule.

Paulus chapter 22 was inspected for the twelfth-parts. The translated rule says
to multiply the degrees held within a sign by 13 and count the resulting arc
from that sign; its 11° Aries example arrives at 23° Leo. This verifies the
engine's Pauline x13 calculation. The legacy engine name “Valens x12” is not
treated as verified. In the inspected Valens text, the example of a Sun at 22°
Aquarius producing a twelfth-part in Scorpio agrees with the x13 projection,
not the x12 projection. The x12 result therefore remains available only as a
configured standard variant with unresolved attribution, and customer output
must display the fork rather than silently choosing one.

Paulus chapters 5 and 32 and their facing canons were inspected for
monomoiria. Chapter 5 starts each sign's first degree with its domicile ruler
and continues in the order of the seven-zoned sphere. Chapter 32 uses a
different seven-ruler sequence for each triplicity and sect and applies it to
the degree of the sect light. This exposed a calculation and scope defect: the
engine had advanced the trigonal form through the ordinary Chaldean order and
attached a result to every planet. The printed day/night table is now encoded,
and only the Sun in a day chart or Moon in a night chart receives the trigonal
result. Paulus does not assign a numerical +1 to self-ruled monomoiria; that
project weighting is now explicitly labeled configured.

Firmicus Maternus, *Mathesis* II.29, was inspected in Jean Rhys Bram's
1975 translation and degree table. The text verifies the solstitial sign
pairs and explicitly treats trine, square, sextile, and opposition through an
antiscion as operative like the corresponding ordinary configuration. This
exposed a report-engine omission: the prior checker recognized only bodily
conjunctions to the reflected point. The audited customer calculation now
checks all five major configurations and publishes only those within a
conservative configured one-degree limit because Firmicus gives no numerical
orb in the inspected passage. Unsupported modern labels such as “secret ally”
or “secret enemy” are not attributed to Firmicus.

Ptolemy's bodily doryphory was rechecked in *Tetrabiblos* III.5 and IV.3.
The attendant belongs in the luminary's own sign or the sign next following;
morning/oriental stars attend the Sun and evening/occidental stars attend the
Moon. This invalidated the engine's old fixed 30-degree window. For the
Fairfield nativity, Mercury is 33.94 degrees after the Moon but is correctly in
the next following sign, occidental, and angular in the first house. It is
therefore a genuine lunar attendant. The report preserves Ptolemy's rank
hierarchy: neither luminary is angular, so this is not the royal configuration;
an angular Mercury attendant instead supports the lower branch of intellectual,
administrative, commercial, educational, or civic distinction. Aspectual
doryphory discussed in Ashmand's Placidus footnote remains outside this bodily
source pass.

Picatrix Book I.4 was inspected in Robert Thomas's selected English
translation for the lunar mansions. The chapter's own framing and every
mansion entry are electional or image-making instructions, not natal character
rules. The Fairfield Moon at Leo 13°14′ is robustly inside the eleventh mansion,
called Azobra in the inspected translation and Al-Zubrah in the configured
Arabic-name table. Some intermediate boundary minutes or seconds in the
selected transcription are internally inconsistent, so the equal tropical
division remains explicitly configured rather than presented as a fully
critical boundary edition. The customer report may name the calculated mansion
and the source scope; it may not convert coercive, martial, medical, financial,
or talismanic operations into personality traits or natal predictions.

For the already admitted Ascendant distributor, annual samples are no longer
reported as the transition itself. Once a change of Egyptian bound is bracketed
between two whole-year samples, the configured directed-Ascendant model now
bisects the interval to solve the crossover age. The resulting age and calendar
date are still explicitly model-derived because the one-degree key, bound table,
and latitude-free aspect points are configured. This improves numerical honesty
without pretending that the rest of Ptolemy's Fortune, Moon, Sun, and Midheaven
prorogations have been implemented or audited.

Paulus chapter 23 and its facing pages were inspected for all seven lots. The
engine's sect-reversing vectors for Fortune, Spirit, Eros, Necessity, Courage,
Victory, and Nemesis match the printed rules. The report now uses Paulus's own
fields rather than generic modern labels, including the severe terms:
Necessity covers submission, struggle, war, enmity, hatred, condemnation, and
restriction; Courage includes treachery and villainy as well as boldness and
might; Nemesis includes cold and subterranean fates, impotence, exile,
destruction, grief, and the quality of death. These are judged through each
lot's place, ruler, and ruler condition. Nemesis does not independently compute
a death date, and none of the lot material becomes professional advice.

Al-Biruni's *Book of Instruction in the Elements of the Art of Astrology*
(R. Ramsay Wright translation, Luzac, 1934) was inspected at section 395,
printed p. 32 (PDF p. 33), against the facing manuscript reproduction. The
source PDF SHA-256 is
`b5b15d3a25842072d680dd6e6d341c992bff0c2a43141d36b47e6a7e2cc761d2`.
The passage verifies the engine's seven-planet Firdaria core: Sun begins a day
nativity, Moon begins a night nativity, the remaining planets follow in
descending order, and each major period is divided into seven equal subperiods
beginning with its own ruler. The passage does not mention node periods. The
project's North/South Node periods therefore remain a separately labeled later
extension and are not attributed to al-Biruni.

Al-Biruni section 496, printed p. 101 (PDF p. 102), was inspected for hayyiz
and halb. It defines halb by matching a planet's diurnal/nocturnal family with
its position above or below ground at day or night. Hayyiz adds agreement
between planetary and sign gender, and explicitly treats Mars as male and
nocturnal. This exposed two engine defects: the old code used whole-sign house
number instead of calculated altitude and defined halb as “sect plus either
horizon or sign.” Both have been corrected. Mercury remains indeterminate
until its conditional family/gender through sign or association is modeled.

## Consequence for product claims

The system can become unusually transparent and text-faithful, but it must not
advertise "perfectly follows the original texts." The surviving tradition is
textually diverse, translations differ, and authorities openly disagree. The
defensible premium claim is: every published judgment is calculated, sourced,
edition-labeled, and explicit about disagreements and uncertainty.
