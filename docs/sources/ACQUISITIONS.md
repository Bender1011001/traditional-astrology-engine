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
