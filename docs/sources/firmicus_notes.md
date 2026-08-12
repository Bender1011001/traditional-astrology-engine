# Firmicus Maternus, *Matheseos libri VIII* (Kroll–Skutsch, Teubner 1897)

Latin. Vol. 1 = 300 PDF pages. Pagination: `printed = pdf_page − 15` (verified against the running heads, e.g. pdf 94 carries `II 29,2—7` and prints 79).

---

## II.29 — antiscia. Printed pp. 77–84, PDF 92–99.

### The construction (II.29,3)

> *Initium antisciorum aut a Geminis et Cancro est aut a Sagittario et Capricorno … Gemini in Cancrum antiscium mittunt et Cancer in Geminos, Leo in Taurum et in Leonem Taurus, Virgo in Arietem et Aries in Virginem, Pisces in Libram et Libra in Pisces, Aquarius in Scorpium et Scorpius in Aquarium, Sagittarius in Capricornum et Capricornus in Sagittarium.*

The solstitial axis, six mutual pairs. **All six verified against `calculate_antiscia_points`.**

### The degree table (II.29,5–6)

Firmicus prints the whole Gemini/Cancer table degree by degree — I→XXIX, II→XXVIII, … XV→XV, … XXIX→I — and says it applies to every pair: *"Hoc itaque exemplum … ad omnium signorum antiscia pertinebit."*

**All 29 degree mappings verified exactly** against our formula `antiscia = (180 − λ) % 360`, reading his degree numbers as exact degree *points* (Gemini 1° → Cancer 29°, and 15° → 15° as the fixed point).

He also states the reciprocity explicitly: *"nam pars, a qua exceperit antiscium, ad eam a se rursus mittit antiscium"* — the degree it receives from, it sends back to.

### The 30th-degree exclusion (II.29,4)

> *in XXX. partem signi nulla pars mittat et quod XXX. in nullam partem mittat antiscium*

No degree sends its antiscion to the 30th, and the 30th sends to none. Under our continuous formula the 30th degree of a sign is the sign boundary itself (Gemini 30° = 90° = Cancer 0°), i.e. **degenerate rather than wrong** — it maps onto the boundary it sits on. Our implementation does not special-case it, and does not need to; recorded so that anyone comparing our output to Firmicus's printed table at that one degree knows why it looks different.

---

## ⚠ Source history: Firmicus points away from himself

> *[Ptolemy] quasi per speculum quidem antisciorum rationem attigit; **Dorotheus vero Sidonius**, vir prudentissimus et qui apotelesmata verissimis et disertissimis versibus scripsit, **antisciorum rationem manifestis sententiis explicavit, in libro scilicet quarto**.* (II.29,2)

Firmicus says Ptolemy touched antiscia only *"as if through a mirror"*, and that **Dorotheus of Sidon set the doctrine out plainly in his FOURTH BOOK**.

Our rule `firmicus_antiscia_major_configurations` cites Firmicus as its authority. Firmicus himself names Dorotheus IV as the clear source. **We now hold Dorotheus** (Pingree 1976, Arabic + English + Greek fragments), so that attribution is checkable — and the Dorotheus volume's own Appendix I is *Fragmentum e Firmici Materni Mathesios libro II 29,2*, i.e. Pingree prints this very passage as a witness to Dorotheus. The two volumes point at each other.

**Not yet done:** reading Dorotheus IV on antiscia to see whether his version agrees with Firmicus's table.
