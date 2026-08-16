# Source acquisitions, 2026-08-11

Five rules were blocked on texts that were not on disk. Four sources were found on the
Internet Archive and downloaded to `tmp/acquire/pdfs/` (gitignored). **Every one was
verified by rendering a page and reading it** — not by trusting the catalogue metadata,
which was wrong or misleading in two of the four cases.

| source | edition | pages | rules unblocked |
|---|---|---|---|
| Ptolemy, *Apotelesmatica* | Boll–Boer, Teubner 1957, **Greek** | 236 | `ptolemy_doryphory_rank`, `ptolemy_perseus_algol`, `ptolemy_prorogation_distributor` |
| Lilly, *Christian Astrology* | 1647 first edition, Wellcome scan | 894 | `lilly_reception`, `lilly_planetary_conditions` |
| Firmicus, *Matheseos libri VIII* | Kroll–Skutsch, Teubner 1897, **Latin**, 2 vols | 300 + 638 | `firmicus_antiscia_major_configurations` |
| Picatrix, *Ghāyat al-Ḥakīm* | Ritter's critical edition, **Arabic** | 438 | `picatrix_lunar_mansions_electional_scope` |

**11 blocked rules became 4.**

## Where the metadata lied

- The Picatrix was listed only as "Picatrix Arabic", uploaded 2021, in a junk collection
  alongside a prize-bond leaflet and a pendulum manual. It is in fact **Ritter's critical
  edition**, with his apparatus citing the Latin Picatrix (`Pic.`) and the Hebrew (`Mon.`).
  Rendering the page was the only way to know.
- An item titled "Al Birini Elements of Astrology" looked like the al-Bīrūnī bilingual.
  Its metadata reports 100% English OCR confidence — an English-only reprint, not Wright's
  1934 facing-Arabic edition. Not downloaded.

## Pagination

Ptolemy Boll–Boer: `printed = pdf_page − 19` (verified: pdf 60 → printed 41).

## Still blocked, and why

| rule | needs | status |
|---|---|---|
| `ibn_ezra_triplicity_life_thirds` | Ibn Ezra, Hebrew | Not on archive.org. The usable critical editions are Shlomo Sela's Brill volumes — **in copyright**. Needs purchase or library access. |
| `ibn_ezra_annual_revolution_core` | same | same |
| `al_biruni_firdaria_seven_planet_core` | al-Bīrūnī, *Kitāb al-Tafhīm*, Arabic | Ramsay Wright's 1934 facing-Arabic edition is not on archive.org; only English-only reprints. Needs purchase or library access. |
| `al_biruni_hayz_halb` | same | same |

These four are an acquisition decision, not a reading task.

---

## al-Bīrūnī acquired — after I twice said it wasn't available (2026-08-11)

**Two files, neither of which is the thing our rule actually cites.** Recording precisely what was got, because the temptation is to call this "al-Bīrūnī done" and it isn't.

| file | what it is | pages |
|---|---|---|
| `albiruni_instruction_wright_1934.pdf` | Wright's **English** typescript of the astrological section — the exact edition `al_biruni_*` rules cite, but the translation half only | 128 |
| `albiruni_tafhim_persian.pdf` | al-Bīrūnī's own **Persian** recension of the *Tafhīm*, critical edition with manuscript apparatus | 867 |

**Still not held:** the **Arabic** facsimile of British Museum MS Or. 8349, which is what Wright printed facing his translation and what the registry means by "facing text".

**Why the Persian still counts for something:** al-Bīrūnī wrote the *Tafhīm* in Persian *and* Arabic himself. The Persian is an authorial version, not a translation of the Arabic — so reading it is reading al-Bīrūnī, in an original language, with an apparatus. It is a different recension from the one cited, which must be stated whenever it is used.

### The process failure, recorded because it happened three times

I said the al-Bīrūnī Arabic was "not digitised anywhere I can reach". The owner pushed back. **One web search found Wright's PDF; one Arabic-language search found the Persian critical edition on archive.org.**

That is the third instance today of the same error:

1. **Text-layer probe** → concluded the Dorotheus scan had no Arabic or Greek. It has both; the OCR simply cannot see non-Latin script.
2. **Truncated print** → concluded three Picatrix mansions were missing material. All three had it past the ~86-character cut.
3. **Unsuccessful search** → concluded two books were undigitised. Both were findable in one query each.

**The shape is identical every time: a negative result from a partial check, reported as a settled fact about the world.** The first two were retracted in this repo's notes; this is the third, and the pattern is now the finding rather than any individual instance.

**The rule that follows:** a failed search is evidence about the search, not about the thing searched for. Say "I haven't found it yet", never "it doesn't exist". The cost of the weaker claim is nothing; the cost of the stronger one was, here, three false blockers that would have sat in the handoff as permanent.

### §395 read (Wright's English, printed p. 32)

> *"The years of a man's life according to a **Persian** idea are divided into certain periods (firdār) governed by the lords of these known as **Chronocrators**… The **first** period always begins with the **sun** in a diurnal nativity and with the **moon** in a nocturnal one; the **second** with **Venus** in the one case, in the other with **Saturn**, the remaining periods with the other planets **in descending order**. The years of each period are **distributed equally between the seven planets**, the first seventh belonging **exclusively** to the chronocrator of the period, the second to it **in partnership with the planet next below it** and so on."*

**Checked against `FIRDARIA_DAY` / `FIRDARIA_NIGHT` — both match.** Day opens Sun → Venus; night opens Moon → Saturn; both continue in descending order. The rule is sound.

**One nuance not yet checked:** he says the second sub-period belongs to the chronocrator **in partnership with** the next planet, not to the next planet alone. Whether our sub-period rendering matches that co-rulership reading is an open question — flagged, not asserted, since it rests on one OCR'd line.
