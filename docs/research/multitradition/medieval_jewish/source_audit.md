# Medieval Jewish Astrology Source Audit

Status: an Ibn Ezra-specific research engine is feasible; a universal Jewish astrology engine is not  
Audit date: 2026-07-31  
Product status: `research_verified` corpus map; implementation remains `not_implemented`

## Decision

Medieval Jewish astrology must be modeled as an author-, work-, language- and
recension-scoped transmission tradition. It is not a separate zodiac with a
single timeless set of Jewish meanings. The strongest bounded starting point is
Abraham Ibn Ezra's Hebrew astrological corpus, for which Shlomo Sela has
published parallel Hebrew-English critical editions.

At least these tracks must remain separate:

1. Ibn Ezra's introductions and explanatory doctrine;
2. nativities and continuous horoscopy/annual revolutions;
3. elections;
4. interrogations;
5. medical critical-day theory;
6. historical and meteorological/world astrology;
7. Abraham bar Hiyya and other Jewish authors;
8. Hebrew translations or adaptations of Arabic works; and
9. astral magic, mystical correspondences and later manuscript compilations.

Arabic source ancestry does not make an Ibn Ezra rule non-Jewish, but neither
does its Hebrew wording make the underlying Arabic doctrine uniquely Jewish.
Every trace must preserve author, immediate source text, translation lineage
and Ibn Ezra's additions or disagreements where scholarship identifies them.

## Existing inspected source

The project already contains an inspected copy of Shlomo Sela's parallel
Hebrew-English critical edition of *The Book of Nativities* and *The Book of
Revolution*. Its PDF SHA-256 is
`58152334a828879e52a02e195589ee03189d681ea637572e08548dfd05403738`,
and the extracted text SHA-256 is
`036939ee2d52387035fa091142a499f3e70efaa890be2d44576ab24281bcf2b3`.
The edition is copyrighted and authorized only for internal verification.

The current Western report uses a very small, passage-identified subset from
the *Book of Revolution*. That does not mean a medieval Jewish engine exists.
It means those particular Ibn Ezra rules are already source-verified within the
live Western engine. The new engine must be independently manifested and may
not inherit all Western configuration defaults by accident.

## Critical-edition corpus

### Introductions and zodiacal judgments

Sela's 2017 *Abraham Ibn Ezra's Introductions to Astrology* is an 822-page
parallel Hebrew-English critical edition of *The Book of the Beginning of
Wisdom* (`Reshit Hokhmah`) and *The Book of the Judgments of the Zodiacal
Signs*. Publisher metadata identifies Greek, Arabic, Hebrew, biblical and
scientific source layers:
<https://www.degruyterbrill.com/de/document/isbn/9789004342286/html>.

This is the correct source family for terminology, zodiacal qualities,
planetary conditions, lots, aspects, houses and other prerequisites. It is not
a license to treat every introductory definition as a standalone natal
judgment.

### Reasons

Sela's 2007 *The Book of Reasons* provides parallel Hebrew-English critical
editions of two versions of the text, with separate notes and appendices:
<https://brill.com/downloadpdf/display/book/9789047421573/Bej.9789004157644.i-400_003.pdf>.
The two versions must retain separate passage identifiers. The work explains
reasons behind astrological concepts; it is a doctrine and source-criticism
layer, not automatically a procedural reading sequence.

### World astrology

The 2010 *Book of the World* edition contains two versions of Ibn Ezra's text,
an edition of Māshā'allāh's *Book on Eclipses*, and several shorter Ibn Ezra
passages:
<https://www.nli.org.il/en/books/NNL_ALEPH997010715813405171/NLI>.
The National Library description explicitly identifies historical and
meteorological astrology assembled from Greek, Hindu, Persian and Arabic
sources. The Māshā'allāh translation must have its own author and lineage ID;
it cannot be silently quoted as Ibn Ezra's original doctrine. None of this
belongs in an individual birth reading.

### Elections, interrogations and luminaries

The 2011 volume contains the first critical Hebrew edition, English translation
and commentary for seven treatises: three versions each of the *Book of
Elections* and *Book of Interrogations*, plus the *Book of the Luminaries*:
<https://www.nli.org.il/en/books/NNL_ALEPH997010705872505171/NLI>.
The catalog correctly distinguishes choosing a time, answering a question and
medical critical-day theory. These require activity time, question time or
illness-course information; birth data cannot substitute for those inputs.

### Nativities and continuous horoscopy

Bar-Ilan's publication record describes the 2013/2014 edition as the first
critical Hebrew text with English translation and commentary for *Sefer
ha-Moladot* and *Sefer ha-Tequfah*:
<https://cris.biu.ac.il/en/publications/abraham-ibn-ezra-on-nativities-and-continuous-horoscopy-a-paralle/>.
It distinguishes the natal chart from anniversary horoscopes superimposed on
it. This is the controlling family for a birth-driven pilot.

## Manuscript witness

National Library of Israel Ms. Heb. 3906=8 is a digitized 1749 composite of
123 Hebrew folios:
<https://www.nli.org.il/en/manuscripts/NNL_ALEPH990000433960205171/NLI>.
Its catalog lists *Reshit Hokhmah*, *Book of Reasons*, zodiacal judgments,
*Book of Nativities*, revolutions, elections, luminaries, *Book of the World*,
other material and several horoscopes. It records codicological complications,
reordered and inserted leaves, annotations, a named copyist and colophons.

This is an excellent public-domain collation and worked-chart witness, but it
is six centuries later than Ibn Ezra and is a composite codex. Its magical
notes, later family horoscopes and copied Ibn Ezra works require separate hands,
dates and provenance. A folio appearing in the same binding is not evidence of
common authorship.

## Beyond Ibn Ezra

Abraham bar Hiyya's calendrical, astronomical and historical-astrological work
predates or overlaps Ibn Ezra and influenced Hebrew scientific writing. Levi
ben Gerson and later Hebrew authors form additional transmission lines. The
current source set does not yet justify encoding their rules. They require
their own critical editions and work audits.

Likewise, `Sefer Yetzirah`, zodiac imagery in synagogues, biblical exegesis,
astral magic and Kabbalistic correspondences are not interchangeable with
Ibn Ezra's horoscopic procedures. A modern “Jewish zodiac” assembled from
tribes, Hebrew months and signs would be a new synthesis unless a named source
explicitly supplies that system.

## Valid-input map

| Work or technique | Required input | Birth-only capability |
|---|---|---|
| Nativities | Exact birth time/place plus source astronomy | Yes |
| Continuous horoscopy/revolutions | Natal chart, target anniversary and return location convention | Yes, with target date |
| Elections | Proposed action, candidate times and location | No |
| Interrogations | Genuine question time/place and question topic | No |
| Luminaries/critical days | Illness onset/course and lunations | No; Historical Use Only |
| World/historical astrology | Collective epoch, conjunction, ingress, eclipse or weather context | No |
| Introductory doctrine | Chart facts supplied to another procedure | Not a reading by itself |
| Astral magic | Ritual/material inputs and cultural permissions | Excluded from customer guidance |

## First valid pilot

The first pilot is an Ibn Ezra nativities-and-revolution pack:

1. Use the already hashed Sela edition and record every natal and revolution
   section with Hebrew/English page pairs.
2. Build a manuscript-version map and compare Ms. Heb. 3906=8 where the same
   passages survive.
3. Extract calculation rules separately from judgments.
4. Reproduce every complete chart or numerical example in the critical
   edition and manuscript.
5. Version house division, astronomical tables, lots, directions, profections,
   return location and day-boundary assumptions rather than inheriting modern
   defaults.
6. Encode precedence: natal promise, longer-term direction, annual revolution
   and shorter testimony may not be flattened into points.
7. Obtain independent Hebrew review and separately identify Arabic technical
   loans and Ibn Ezra's own position.
8. Emit omissions and disagreements in the coverage manifest.

Elections, interrogations and world astrology become later, input-specific
modules. They are not added to a birth report merely because the corpus
contains them.

`rule_manifest.json` now has complete vector coverage in
`validation_vectors.json`: eight tests cover return-definition dependencies,
unknown return location, relative life phases without invented ages, rejection
of equal numeric thirds, unresolved active triplicity rulers, the three annual
Ascendant witnesses without Tajika Muntha, and annual-testimony precedence.
They validate abstention and evidence ordering, not a finished calculator.

## Safety and religious dignity

Historical texts include claims about lifespan, illness, disability,
fertility, children, religion, wealth and death. They may be studied and cited
in a forensic historical trace, but customer prose may not diagnose, predict a
death age, deny religious agency, prescribe medical action, or make coercive
claims about relatives. Medical astrology remains Historical Use Only.

The system must not imply that astrology represents a universal Jewish belief
or religious requirement. Medieval Jewish authors disagreed about astrology,
and the product must name Ibn Ezra or another selected author rather than
speaking for Judaism.

## Failure conditions

The track is not production-ready if:

- Ibn Ezra is treated as the whole of Jewish astrology;
- Arabic, Hebrew, French and Latin versions lose their transmission identity;
- multiple versions in a critical edition are merged into one rule silently;
- Māshā'allāh's translated work is attributed to Ibn Ezra;
- introductory lists are converted into isolated keyword readings;
- elections, questions, critical days or world astrology are driven by birth
  time alone;
- modern Hebrew-month or tribe-sign meanings are invented;
- no Hebrew reviewer approves the extraction;
- copyrighted critical editions are redistributed; or
- the interface implies a live Jewish engine while only Western is live.
