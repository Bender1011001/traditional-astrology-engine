# Mon Astrology and Astral Manuscript Source Audit

Status: source-limited  
Audit date: 2026-07-31  
Product status: `source_limited`; no calculation or customer reading is authorized

## Decision

The evidence establishes that astrology, divination and horoscopology occur in
Mon manuscript environments. It does not yet establish a reproducible,
specifically Mon birth-reading system. No Mon engine should be built by
renaming Burmese, Thai, Lanna, Khmer or generic Indian calculations.

The next valid deliverable is a language/script/genre catalog and one
community-confirmed Mon-language procedural witness. Until that exists, the
coverage manifest must report `source_limited` and produce no simulated
reading.

## Identity controls

Every candidate must record these dimensions independently:

| Dimension | Permitted values/examples | Why it matters |
|---|---|---|
| Language | Mon, Pali, Burmese, Thai, Sanskrit, mixed | A Mon-script Pali text is not a Mon-language rulebook |
| Script | Mon/Myanmar, Thai, Khom, other | Script does not establish language or ethnicity |
| Place/custodian | Mon State, central Myanmar, a Mon monastery in Thailand, other | Repository location does not establish textual identity |
| Genre | astrology, astronomy, calendrics, horoscopology, divination, cosmology, ritual | Catalog labels are too broad for an engine |
| Input | birth moment, question moment, omen, calendar date, ritual situation | Only some genres can answer a birth-data request |
| Date/lineage | colophon date, copy date, inferred range, teacher/copyist lineage | Later copies may transmit much earlier or imported procedures |

An item is promoted to the Mon technical corpus only when language is verified
from the text or a qualified cataloger, the relevant passage is procedural,
and its input/output semantics are clear.

## EAP1432: strongest corpus lead

The British Library Endangered Archives Programme project EAP1432 digitized a
large set of Mon-associated palm-leaf manuscripts in Thailand. The inspected
project account reports nearly one thousand manuscripts, mainly from the
nineteenth and early twentieth centuries, with some earlier and later items:
<https://seajunction.org/recalling-a-translocal-past-digitizing-mon-palm-leaf-manuscripts-of-thailand-part-2/>.
It reports Mon and Pali in Mon script, and Thai and Pali in Khom script, with
astrology and divination among the subjects.

This is corpus evidence, not a rule source. The EAP project page is
<https://eap.bl.uk/project/EAP1432>. The indexed methodology report is
<https://eap.bl.uk/sites/default/files/2024-09/EAP1432%20Methodology%20Report.pdf>.
The report could not be retrieved directly during this pass and remains
`search_metadata_only`. Indexed descriptions indicate cataloging limitations
and the need for stronger Mon-language review; those details must be confirmed
from the report itself before use.

An inspected item pattern such as <https://eap.bl.uk/archive-file/EAP1432-2-70>
shows that records can expose language, script, date range and monastery. That
particular item is not promoted as an astrology source. The catalog must be
searched and corrected at item level, not inferred from the collection title.

The EAP1123 pilot catalog describes six Thai-Mon collections:
<https://searcharchives.bl.uk/catalog/032-003708970>. The first inspection did
not identify a technical astrology witness, so no negative inference about the
whole collection is justified.

## U Po Thi Library and the Lower Myanmar boundary

The Myanmar Manuscript Digital Library provides the U Po Thi Library catalog
for Thaton, Mon State:
<https://mmdl.utoronto.ca/databases/u-po-thi-library/>. The repository and the
University of Toronto's project description state that the holdings include
astrology:
<https://munkschool.utoronto.ca/ai/news/new-open-access-database-myanmar-manuscripts-and-textual-artefacts-u-t>.

The catalog exposes relevant astral titles, including:

- `Adhimasa-tika` (UPT320F), associated with intercalation;
- `Ayudaya-dasa-kyam` (UPT158F), associated with longevity and periods;
- `Candasuriyagatidipani` (UPT538_3F), solar-lunar motion;
- `Dva-dasa-rasi-dhat-kyam` (UPT117F), twelve signs;
- nakshatra-related titles including UPT155F and UPT063F; and
- another `Candasuriyagati-dipani` witness in UPT644F.

The alphabetical catalog is accessible at
<https://mmdl.utoronto.ca/databases/u-po-thi-library/a-c/>. None of these titles
is accepted as Mon astrology merely because the library is in Mon State. The
next inspection must establish language, script, author, colophon, contents and
whether the procedure is astronomical, calendrical or divinatory.

## Transregional Pali and Sanskrit evidence

Gornall's "Conceptualising the World in Pali Literature" is important for
historical routing:
<https://hasp.ub.uni-heidelberg.de/journals/jpts/article/download/28261/27652/57506>.
It discusses the `Candasuriyagatidipani`, its Myanmar setting, canonical and
commentarial Pali material, and Sanskrit jyotisa/Vedic sources. It also notes a
teacher association tentatively connected with Martaban. This is evidence of a
transregional astral environment. It is not evidence that every procedure in
the work is ethnically Mon or that it supported natal readings.

## Calendar warning

An indexed article titled "George Coedes' Chronology of the Kingdom of
Haripunjaya" appears relevant to claims about a historical "Mon calendar" and
local intercalation. The direct ThaiScience endpoint returned an HTML analytics
shell rather than the article PDF:
<https://www.thaiscience.info/journals/Article/SUIJ/10559516.pdf>. No technical
claim from its search snippets is accepted. The actual article and the
epigraphic evidence it evaluates must be obtained before any Haripunjaya
calendar hypothesis is encoded.

This failure matters because a regular twelve-year cycle, a Burmese calendar
kernel, or an Indian back-calculation cannot be assigned to historical Mon
dates without proof of the local era, intercalation and day-boundary rules.

## Birth-input capability map

| Candidate material | Can birth data drive it? | Current disposition |
|---|---|---|
| Horoscopology manuscripts reported in EAP1432 | Unknown until an item and its procedure are identified | `source_limited` |
| U Po Thi longevity/period and zodiac titles | Possibly, but language and input semantics are unverified | Myanmar/Pali discovery leads, not Mon rules |
| Solar-lunar motion and intercalation works | They may supply a calendar kernel, not necessarily a reading | Verify witness, constants, epoch and examples |
| Divination manuscripts | Often require a question, omen or ritual act rather than birth data | Keep outside the natal workflow unless the source says otherwise |
| Cosmological works | Usually explanatory rather than natal | Context only unless explicit procedural passages exist |

## First valid pilot

The first pilot is a corpus classifier, not a horoscope generator:

1. acquire the EAP1432 and EAP1123 catalog exports and the EAP1432 methodology
   report;
2. preserve repository IDs, monastery/custodian, dimensions, date, language,
   script, genre and cataloger confidence;
3. have Mon-language reviewers correct the labels and identify procedural
   astrology or horoscopology items;
4. choose one complete Mon-language witness whose rule inputs are observable;
5. transcribe the relevant folios diplomatically, translate them with technical
   notes and record image-to-line concordance;
6. locate any worked example, almanac or parallel witness and independently
   reproduce its calendar and arithmetic; and
7. decide from the evidence whether the result is natal, calendrical,
   interrogational, omen-based or another module.

Only after those steps can a calculation specification be proposed. Shared
Burmese or Southeast Asian software may be reused internally only when the Mon
source proves the same constants and procedure; code reuse must never erase
source identity.

## Failure conditions

The track remains `source_limited` if:

- Mon language is inferred from Mon script, Mon State or a Mon monastery;
- a title is promoted without inspecting its item record and relevant folios;
- catalog subject labels substitute for a procedural passage;
- Burmese, Thai, Lanna, Khmer or generic Indian rules fill gaps;
- an astronomical/calendar work is presented as a divinatory birth reading;
- a historical calendar conversion lacks local era, intercalation and boundary
  evidence;
- no Mon-language reviewer validates the transcription and cultural identity;
  or
- the product presents a generic result instead of the explicit
  `source_limited` state.

