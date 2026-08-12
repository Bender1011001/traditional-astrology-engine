# William Lilly, *Christian Astrology* (London 1647, first edition)

Wellcome facsimile, 894 PDF pages. **Lilly wrote in English, so this scan IS the original** — there is no translation layer, and the earlier `translation_inspected` status on his rules was a category error.

Pagination: PDF page ≈ printed page + 33 (verified: pdf 145 → printed 112; pdf 148 → printed 115).

---

## Reception — printed p. 112

> *Reception is when two Planets that are significators in any Question or matter, are in each others dignity … here is reception of these two Planets by Houses; and certainly **this is the strongest and best of all receptions**. It may be by triplicity, terme or face, or any essentiall dignity … The use of this is much; for many times when as the effecting of a matter is denyed …*

Three things the text states plainly:

1. Reception is mutual presence **in each other's dignity** — not one-way.
2. Reception **by domicile is the strongest**; but it may be by *any* essential dignity, including triplicity, term, or face.
3. Its function is to **effect a matter otherwise denied** — that is the reason Lilly gives for caring about it.

---

## ⚠ The Fortitudes table — printed p. 115, and a gap it exposes

> *A ready Table whereby to examine the Fortitudes and Debilities of the Planets.*

| Lilly | value | ours (`DignityCalculator`) |
|---|---|---|
| own house **or mutuall reception by house** | 5 | `DOMICILE = 5` |
| exaltation **or reception by exaltation** | 4 | `EXALTATION = 4` |
| own Triplicity | 3 | `TRIPLICITY = 3` |
| own Terme | 2 | `TERM = 2` |
| Decanate or Face | 1 | `FACE = 1` |
| Detriment | −5 | `DETRIMENT = -5` |
| Fall | −4 | `FALL = -4` |
| Peregrine | −5 | `PEREGRINE = -5` |

**All eight point values match exactly.** The table is Lilly's.

**But the two reception clauses are not implemented.** Lilly's own rubric awards a planet in *mutual reception by house* the **same 5 points** as a planet in its own house, and *reception by exaltation* the **same 4** as exaltation. `grep -n reception src/engine/dignities.py` returns nothing but a comment: reception is computed elsewhere (`reception.py`) and never reaches the dignity score.

**Unlike the Dorotheus "share", this gap has an explicit weight in the source** — 5 and 4, printed in the table. So it is implementable without guessing. It is nevertheless **not patched here**, because awarding 5 points for mutual reception changes essential-dignity totals on any chart containing one, and the almuten is decided by those totals — so it would silently move the chart ruler in some nativities. That is a decision to take deliberately, not a side effect of a reading session.

Also worth noting for the accidental-fortitude table on the same page (angularity, direct motion, swift motion, orientality for Saturn/Jupiter/Mars and occidentality for Mercury/Venus): not audited against our implementation in this pass.

---

## Status

Both `lilly_reception` and `lilly_planetary_conditions` move from `translation_inspected` to `facsimile_inspected_1647_first_edition` — the correct status for an author who wrote in English.
