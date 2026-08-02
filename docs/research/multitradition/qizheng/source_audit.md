# Qizheng Siyu (七政四餘) source audit

Status: first pass; one primary Buddhist-astronomical witness read directly and
hash-verified, one Ming print edition and one Qing imperial redaction identified
and partially read through web-mediated access; not production approval
Updated: 2026-08-02

## Result of this pass

Qizheng Siyu ("Seven Governors and Four Surplus," 七政四餘) had zero files
anywhere in this repository before this pass. It is now demonstrated to be a
real, textually continuous, cross-witnessed tradition, and three things are
already provable from the sources rather than asserted:

1. **The tradition is genuinely syncretic, and one of its four "surplus"
   bodies changed identity inside the Chinese textual record itself.** The
   9th-century Tang translation of the Indian nine-luminary system, 《七曜攘災
   決》 (Qiyao Rangzai Jue, Taishō T21 no. 1308 — already hash-pinned in this
   repository by the `sukuyodo/` track, see below), defines 計都 (Ketu) not as
   a lunar node but as **the Moon's apogee**, moving prograde, and gives it the
   alternate name **月勃力** (Yuebo-li) — a name one step removed from 月孛
   (Yuebei), the name the mature Qizheng Siyu system uses for exactly that body.
   Rahu, in the same text, is retrograde and eclipse-causing. Modern
   scholarship (cited below) documents that Song-dynasty astrologers then
   re-paired Rahu and Ketu as opposed nodes, and that the early Qing Jesuit
   reform swapped which node got which name again — while working
   astrologers kept the pre-reform convention. None of this is invented; it is
   read directly from a primary text already sitting in this repository under
   a different tradition's folder, extended here with a new extraction.
2. **The twelve-palace rulership scheme is not a Chinese invention wearing a
   Western label — it is the Hellenistic domicile scheme, unmodified, mapped
   onto the twelve Chinese branches.** Rat/Ox → Saturn, Tiger/Boar → Jupiter,
   Rabbit/Dog → Mars, Dragon/Rooster → Venus, Monkey/Snake → Mercury, Horse →
   Sun, Sheep → Moon is — once the branches are read through the standard
   branch-to-zodiac-sign correlation used in Qizheng Siyu charts (午=Leo,
   未=Cancer, 申=Gemini, 巳=Virgo, 酉=Taurus, 辰=Libra, 戌=Aries, 卯=Scorpio,
   亥=Pisces, 寅=Sagittarius, 子=Aquarius, 丑=Capricorn) — **exactly** Ptolemy's
   domicile table: Sun/Leo, Moon/Cancer, Mercury/Gemini+Virgo, Venus/Taurus+
   Libra, Mars/Aries+Scorpio, Jupiter/Sagittarius+Pisces, Saturn/Capricorn+
   Aquarius. This is the single most surprising and most load-bearing finding
   of this pass. It is currently sourced only from modern web secondary
   material (graded accordingly below) and is the highest-value target for
   primary-text confirmation in the next pass.
3. **The worked-example problem that sinks most classical-astrology tracks in
   this repository is, for once, not total.** 《張果星宗》/《果老星宗》 quotes
   short delineations for at least four real, datable Tang-dynasty figures —
   王勃 (the poet), 楊國忠 (Xuanzong's chancellor), 張巡 (the general who died
   defending Suiyang), and 安祿山 (the rebellion's namesake) — and at least two
   of them (王勃, 楊國忠) are independently attested in **both** the vernacular
   《張果星宗》 transcription and the Siku Quanshu's retitled redaction of the
   same tradition, 《星命溯源》. That cross-witness agreement is real evidence
   the two texts share a common ancestor rather than being unrelated works
   that happen to share a legendary author's name. It is not yet a
   reproducible worked example: this pass has the delineation fragments and
   their claimed historical outcomes, not structured birth data (year, month,
   day, double-hour) for any of the four figures, which is the access gap
   that would need closing before any of these becomes a machine-checkable
   vector rather than a documented fragment.

## What survives, and in what shape

| Work | Branch | Edition retrieved | Current evidentiary value | Main limitation |
|---|---|---|---|---|
| 《七曜攘災決》 Qiyao Rangzai Jue, Taishō T21 no. 1308 | four-surplus identity and computation, twelve-palace names, 9th-century layer | CBETA TEI P5, already hash-pinned in `sukuyodo/sources/T21n1308.xml` (sha256 `464d38d06fb926a7060866d275058802244bef5f4602bfd0b58dc97f59594df8`, independently re-verified in this pass) and its line-addressed rendering `T21n1308_lines.txt` (sha256 `50b9c1481eb25c8eefc97962602cb45f142039fcbe71a2a9df6983e627937a7d`, also re-verified) | **strongest source in this pack**: read directly in Classical Chinese, with exact Taishō page/column/line addresses for every rule; the Rahu and Ketu passages (juan 2, T21.0442b–0443b and T21.0446b–d) were not previously extracted by the `sukuyodo` track, which registered this text only as a contrast witness for its own 27-vs-28-mansion question | this text is a **nine-luminary** (九曜) system — seven classical bodies plus Rahu and Ketu only. It has no Ziqi and no Yuebei as independently named bodies; Yuebei's later independent identity is argued here from a name-cognate (月勃力 → 月孛) and a period match, not asserted as the text's own claim |
| 《張果星宗》 / 《果老星宗》, ctext.org wiki transcription | mature natal system: 51 star patterns, 12-palace patterns, four-surplus doctrine, four historical worked-example fragments | `ctext.org/wiki.pl?if=gb&chapter=349444` (six juan) and `chapter=530323` (parallel/duplicate entry, same content, self-referential) | machine-readable, quotable, cross-checked against a second independent web extraction pass for consistency; **base facsimile and collation history are unidentified on the page itself** — this is the same evidentiary situation the `ziwei/` track already documented for its own Wikisource transcription | anonymous transcription; no page images; no stated printing behind the transcribed text; graded D exactly as ziwei's comparable transcription is graded, for the same reason |
| 《果老星宗、鄭氏星案》 = 《果老星宗命格大全》, Ming Wanli 21 (1593), Nanjing, 大文堂 print, attributed "Zhang Guo, active 713–742" | the same natal system, ten juan (nine of Guo Lao Xing Zong proper plus a tenth juan of 鄭氏星案, "the Zheng clan's star cases") | Internet Archive item `guolaoxingzong` (identifier confirms `mdp.` HathiTrust/University of Michigan prefix on every per-juan file: `mdp.39015088726362` through `mdp.39015088726438`); title page OCR (juan 1, byte 1) reads *"Guo lao xing zong ming ge da quan. Zhang Guo, active 713-742. Nanjing: Da wen tang, 1593,"* with HathiTrust's own public-domain determination printed on the same leaf | **a real, named, dated Ming print edition, held by a named research library, with a HathiTrust public-domain determination already stamped on the scan** — this is materially stronger provenance than the ctext transcription | **the OCR is unusable.** All ten per-juan `_djvu.txt` files were downloaded and searched programmatically in this pass; none contains a single legible occurrence of 羅睺, 計都, 紫炁, 月孛, or 周天, and manual inspection of two full juan shows the OCR output is dominated by single stray characters, HathiTrust's own boilerplate repeated dozens of times, and Latin-letter noise (Tesseract 5.3 misreading vertical Classical Chinese woodblock/lead-type text). This is an **access-quality blocker, not a rights or language blocker** — precisely the same class of problem the `byzantine/` track recorded for John Lydus's *De ostentis*. The JP2 page images and the PDF exist and were not read as images in this pass |
| 《果老星宗》卷一 (juan 1 only), separate Internet Archive item `glxz1`, ABBYY OCR | a **different, later** compiled edition: the legible preface fragment names 量天尺 ("measuring-heaven scale") revision tables running from 康熙庚辰 through 民國丙寅 (1926), credited in part to 高魯, director of the Republic's Central Observatory (中央觀象臺) | Internet Archive item `glxz1` (`GLXZ1_djvu.txt`, 77,022 bytes, downloaded and hashed in this pass, sha256 recorded below) | confirms this is a **distinct print tradition from the 1593 Ming edition** — a Qing/Republican compiled reprint carrying a multi-reign-era astronomical conversion table not present in the 1593 print's structure — and that the "Guo Lao" tradition was still being actively revised and republished as late as the 1920s | same OCR-quality problem as `guolaoxingzong`; only the preface (roughly the first 40 legible lines) was readable at all, and even that required manual reading through heavy character corruption. Must never be silently merged with the 1593 print as if they were the same witness |
| 《星命溯源》, Siku Quanshu 欽定四庫全書 edition, compiled under the Qianlong-era editorial board (submitted 1781) | the **imperial library's own redaction and retitling** of the Zhang-Guo-attributed five-star tradition, five juan | zh.wikisource.org, `星命溯源_(四庫全書本)` and its five juan sub-pages, read via web-mediated extraction in this pass | the Siku Quanshu is one of the best-documented pre-modern Chinese textual projects in existence: dated, editorially supervised, publicly cross-indexed. The editors' own abstract states plainly that "the art of five-star fate-calculation is attributed to Zhang Guo; practitioners therefore named this school after 'Guo Lao's Five Stars'" (術者遂以果老五星自名一家) — an explicit, dated, official acknowledgment that "Guo Lao" branding is a school-naming convention layered onto an earlier, less personally-attributed technique, not a claim that Zhang Guo personally wrote either text | web-mediated extraction only in this pass, not a downloaded/hashed facsimile page image; graded accordingly below. Juan 2's own content dates the reputed Zhang-Guo dialogue to a Ming-dynasty interlocutor (李憕) meeting a Tang-dynasty immortal — an internally acknowledged anachronism in the transmission legend that the Siku editors evidently tolerated rather than corrected |
| zh.wikipedia.org, 七政四餘 article | secondary synthesis of the Rahu/Ketu definitional history and the Ziqi no-astronomical-referent question, citing named modern scholarship | `zh.wikipedia.org/zh-tw/七政四餘`, read via web-mediated extraction | cites real, checkable academic work — 陳于柱's 2009 study of a Dunhuang manuscript on 《推人九天宮法》, 譚冰's 2013 《古今曆術考》, and 曹士蒍's Tang-dynasty 《符天曆》 — which is exactly the kind of citation trail that would let a specialist verify or overturn the claims here | this pass did not retrieve any of the three cited academic works directly; the Wikipedia synthesis is quoted as a secondary source pointing at primary material, not treated as primary itself. Graded C, one step above the anonymous ctext transcription because its claims are individually attributed and in principle checkable |
| Planetary rulership of the twelve branches (Rat/Ox–Saturn, Tiger/Boar–Jupiter, Rabbit/Dog–Mars, Dragon/Rooster–Venus, Monkey/Snake–Mercury, Horse–Sun, Sheep–Moon) | dignity/rulership scheme | modern web secondary sources (getit01.com, baike.baidu.com), read via web search synthesis only | the scheme is internally coherent, matches the Hellenistic domicile table exactly under the standard branch-zodiac correlation, and is repeated consistently across independent modern sources without contradiction | **no primary classical-text citation was located for this scheme in this pass.** This is graded D and flagged as the single highest-priority item for the next pass: if it is confirmed inside 《張果星宗》 or 《星命溯源》 directly (plausible, since both were only partially read), it would be one of the strongest single findings in this entire multi-tradition project — a checkable, exact transplant of a named foreign technical system onto Chinese nomenclature |
| 五星三命指南 (named by the task brief as a possible earlier/parallel source) | unknown | **not located.** Targeted searches for this exact title returned no ctext, Wikisource, or Archive.org hits distinct from the works above | none | this is an open lead, not a negative result about the text's existence — the search terms used may simply not match how (or whether) this title is catalogued digitally. Recorded as a discovery candidate for the next pass, not as "does not survive" |

## The nine-luminary layer versus the four-surplus layer, read directly from T1308

This is the load-bearing technical finding of this pass and it rests entirely
on Classical Chinese read directly from the hash-pinned CBETA file, not on any
secondary synthesis.

**Rahu** (羅睺遏囉師, *Rāhu-graha*), T21.0442b02–0443b01: also called 黃幡
("Yellow Banner"), 蝕神頭 ("Eclipse-Deity's Head"), 複 ("Fu"), and 太陽首
("the Sun's Head"). The passage states it "constantly moves hidden and unseen"
and causes eclipses whenever it meets the Sun or Moon at new or full moon or in
opposition, and — remarkably for a 9th-century text — the passage explicitly
**compares two rival eclipse theories**, the Indian (attributed to "婆毘磨",
a transliteration attempt for an Indian astronomical authority) and the "Han"
(native Chinese) theory of a shadow-point 暗虛, and states outright that
"根據天竺曆，得其正理矣" — "having checked against the Indian calendar-method,
[we find] it has the correct principle" — an explicit, dated instance of a
Chinese astronomical text preferring an imported theory over a native one on
its stated merits. Rahu moves **retrograde**, uniformly, at rates the text
gives redundantly (19 days/degree; 1.6°/month; 19⅓°/year; 18 years per circuit
of heaven, short by 11⅔°; 93 years to a "Great Cycle," 大終). Recomputing the
93-year figure from the stated annual rate (19⅓° × 93 ≈ 1798°, i.e. 4.99
complete retrograde circuits) shows the Great Cycle is close to five full
revolutions at the stated rate — accurate to about 2° over 93 years. The
stated 18-year/11⅔° figure is *not* perfectly consistent with the stated
19⅓°/year rate (19⅓° × 18 = 348° exactly, implying a 12° shortfall, not
11⅔°) — a small, honestly-reported internal inconsistency of about a third of
a degree, the kind of rounding artifact ancient tabular astronomy commonly
carries and which this pack records rather than silently smooths over.

**Ketu** (計都遏囉師, *Ketu-graha*), T21.0446b01–d01: also called 豹尾
("Leopard's Tail"), 蝕神尾 ("Eclipse-Deity's Tail"), **月勃力** ("Yuebo-li"),
and 太陰首 ("the Moon's Head" — paired with Rahu's "the Sun's Head," a
Sun/Moon duality distinct from the "head/tail of one dragon" imagery familiar
from later, merged traditions). Ketu moves **prograde** — the text says so
explicitly, in direct contrast to Rahu's stated retrograde motion — at 9
days/degree, 3.4°/month, 40.7°/year, closing to "9 years per circuit, over by
6.3°" and "62 years per seven circuits, over by 3.4°." Both of these check out
**exactly** against the stated annual rate: 40.7° × 9 = 366.3° = 360° + 6.3°,
and 40.7° × 62 = 2523.4° = (7 × 360°) + 3.4°, with no rounding slack at all —
a cleanly self-consistent set of figures, in contrast to Rahu's. Solving for
the true period gives 360° ÷ 40.7°/year ≈ 8.845 years, which sits within about
half a day of the real astronomical lunar apsidal (apogee) precession period
of ≈ 8.85 years. **This body is not a lunar node.** Its alternate name
月勃力 differs from 月孛 (Yuebei), the name the mature Qizheng Siyu four-surplus
system uses for the lunar apogee, by one syllable rendered with a near-
homophone character (勃 *bo* vs 孛 *bei*/*bo*), and its stated behavior
(prograde, ~8.85-year period) is the lunar apogee's behavior, not a node's.
The conclusion drawn in this pack — that T1308's "Ketu" and the mature
system's "Yuebei" are the same underlying astronomical referent under two
names from two textual layers — is this encoder's inference from the primage
evidence, not a claim the text makes about itself, and it is labeled as such
in the rule manifest.

The twelve-palace scheme also appears in T1308, under the heading
七曜旁通九執至行年法 ("The Method by Which the Seven Luminaries Interpenetrate
the Nine Seizers, Extended to the Directed-Year Technique"), T21.0427c06–
0428a03: 命宮 (Life), 財宮 (Wealth), 兄弟 (Siblings), 田宅 (Estate), 男女
(Children), 僮僕 (Servants), 妻妾 (Spouse/Consorts), 疾病 (Illness), 遷移
(Travel), 官位 (Rank), 福相 (Fortune), 困窮 (Poverty/Hardship). Eleven of these
names match the mature system's twelve palaces closely or exactly; the twelfth
is named 困窮 ("Poverty/Hardship") here versus the mature system's more neutral
相貌 ("Appearance") — a semantic narrowing-then-widening worth flagging, not
resolving, since no intermediate witness was read in this pass.

## What Rahu and Ketu became later, per secondary synthesis (not yet primary-verified in this pass)

zh.wikipedia's 七政四餘 article, citing 陳于柱 (2009, on a Dunhuang manuscript
《推人九天宮法》) and other named modern scholarship, states that the
Tang-Song transition re-paired Rahu and Ketu as **opposed nodes** — Rahu
becoming the descending node (also called 交初), Ketu the ascending node
(交中) — and that the early Qing reform under 湯若望 (Johann Adam Schall von
Bell, "新法") swapped them again to match the modern Western/Vedic convention
(Rahu = ascending, Ketu = descending), **but that practicing fate-calculators
largely kept the pre-reform convention** (Rahu = descending, Ketu = ascending)
rather than following the court's astronomical reform. If this holds up under
primary-source review, it means **today's Qizheng Siyu convention for Rahu and
Ketu is the mirror image of the modern Western and Jyotisha convention** — a
fact any implementation must get right and disclose, since silently applying a
Western node convention to a Qizheng Siyu chart would invert the entire
Rahu/Ketu axis. This claim is graded C in the rule manifest: it is not
invented, it names real scholarship, but that scholarship was not
independently retrieved and read in this pass.

Ziqi (紫氣/紫炁) is a **fourth-body Chinese elaboration with no counterpart in
the nine-luminary Buddhist import** — it does not appear anywhere in T1308.
Per the same secondary synthesis, its stated period (28 or 29 years,
inconsistently across modern sources — a genuine cross-source numerical
disagreement this pack records rather than picks a side on) has **no
corresponding astronomical phenomenon**, and is theorized to derive either
from the 19-year/7-intercalation lunisolar leap-month cycle scaled up, or from
modeling it on the Tai Sui (太歲) duodecennial counter-Jupiter cycle extended
from twelve branches to the twenty-eight lunar mansions. Both explanations, if
correct, would make Ziqi a **calendrical bookkeeping construct given a
planetary personality**, not an approximation of any observed body — a
genuinely different epistemic status from Rahu (a real geometric point),
Ketu/Yuebei (a real apsidal point), and the seven visible bodies. This is
exactly the kind of thing the defensibility standard wants disclosed rather
than smoothed into "four surplus planets" as if they were epistemically
uniform.

## Worked examples (命例): found, not yet reproducible

Both 《張果星宗》 (ctext transcription) and 《星命溯源》 (Siku Quanshu,
independently) preserve short delineation fragments tied to real Tang-dynasty
figures:

- **王勃** (Wang Bo, the poet): life-palace in the Wing lodge (翼); "Mercury
  retrogrades, paying court to the rising sun at the Chariot-Platform [軫]...
  Wood generates Fire, and [Ziqi's] qi further nourishes the Legs-Wall
  sector." Attested in **both** witnesses.
- **楊國忠** (Yang Guozhong, Xuanzong's chancellor): "born at the You hour,
  life established in You [rooster] palace with Fire and Rahu flanking in
  mutual reception" (坐酉夘火羅夾拱). Attested in **both** witnesses.
- **張巡** (Zhang Xun, the general who died defending Suiyang): "his life sits
  at Heart-Moon-Fox [心月狐]; the present limit-period passes through
  Extended-Net-Moon-Deer [張月鹿]... Saturn ahead, Ketu behind... he did
  indeed die at [An] Lushan's soldiers' hands" (果死祿山兵手). Attested in
  ctext's 《張果星宗》 only, in this pass.
- **安祿山** (An Lushan, the rebellion's namesake): "life-palace falls on
  Robbery-and-Killing; life is established in the Si palace; Mercury is the
  Lu-master [祿主]... at fifty-two, in the You limit-period, on a Mao day...
  he did indeed that year scheme to depose and enthrone [himself]" (果其年謀
  廢立). Attested in ctext's 《張果星宗》 only, in this pass.

Two of four cases each check against a documented, independently known
historical outcome (Zhang Xun's death to An Lushan's forces in 757; An
Lushan's 755 self-proclamation as emperor of Yan), which is exactly the kind
of retrospective verification classical fate-calculation texts favor and which
gives these fragments real interpretive weight. **None of the four is
currently reproducible as a machine-checkable vector.** This pass located the
delineation text and, for two of the four, the claimed historical event the
delineation is checked against; it did not locate structured birth data
(year, month, day, double-hour) for any of the four figures in either witness.
Closing that gap — finding each figure's stated birth data inside the fuller
text, most likely in the sections this pass did not fully retrieve — is the
single highest-value next step for turning "worked examples exist" into
"worked examples reproduce."

## What blocks what

| Blocked item | Blocker class | What would unblock it |
|---|---|---|
| Any rule from the 1593 Ming print (`guolaoxingzong`) or the Republican compiled edition (`glxz1`) | **access quality** — the OCR is unusable, not the rights or the language | page images from the JP2/PDF files already present in both Internet Archive items; this pass did not attempt image-based reading |
| Structured birth data for any of the four worked-example figures | access — likely present in a fuller retrieval of the same texts this pass already identified | a complete read-through of all six juan of the ctext transcription and all five juan of 星命溯源, rather than the targeted passage searches performed in this pass |
| The Tang-Song and Qing-era Rahu/Ketu redefinition claims | access to the cited modern scholarship, not rights or language | retrieving 陳于柱 (2009) and 譚冰 (2013) directly, or locating the Song-era text that first states the paired-node redefinition and the Qing 湯若望 "新法" material that restates it |
| The twelve-branch planetary rulership (Hellenistic-domicile-parallel) scheme | access — not yet found in a primary text in this pass | a full read of 《張果星宗》's fifty-one star-pattern and twelve-palace-pattern juan (juan 2), which this pass only partially retrieved |
| 五星三命指南 | **not located** — an open discovery lead, not a negative finding | a differently-worded catalogue search, or a specialist's pointer to where this title is catalogued |
| Any rule from 《星命溯源》 (Siku Quanshu) beyond what web-mediated extraction surfaced | access — the text exists and is public domain, but this pass did not download and hash a facsimile page image | direct retrieval of the Wenyuange Siku Quanshu facsimile pages, or a stable plain-text mirror, with a page-image collation pass |
| Promotion of any rule from research to reading | specialist review | an independent reader of both Classical Chinese and the Qizheng Siyu technical vocabulary (祿主, 限運, 廟旺陷弱, 命主/度主), plus a second passage-to-predicate encoder |

## Rights status

- **T21n1308** (七曜攘災決): governed by the same CBETA non-commercial
  condition already recorded for this file under `sukuyodo_qiyao_rangzai_jue_
  t1308_cbeta` in the source registry. Not assumed public domain for
  customer-facing reuse; research use here is within the stated condition.
- **`guolaoxingzong`** (Ming Wanli 1593 print, HathiTrust/University of
  Michigan scan): HathiTrust's own access page states the determination that
  this work is in the public domain and free to copy, use, and redistribute
  in part or whole, with the caveat that illustrations or photographs within
  it might separately carry rights. This is about as clean a public-domain
  determination as exists in this project.
- **`glxz1`**: uploaded to Internet Archive by the same contributor
  (`EdwWh`) under the general Internet Archive "Books by Language" collection
  terms; no separate rights statement was located distinct from the general
  public-domain status implied by its pre-1929 core content, though the
  20th-century supplementary tables (through 1926) sit closer to the edge of
  the public-domain boundary in some jurisdictions and were not separately
  cleared in this pass.
- **ctext.org wiki transcription**: ctext.org's own terms permit reference use
  of transcribed pre-modern text; no base facsimile is identified on the page,
  so no independent rights determination can be made about the underlying
  print this transcription reproduces. Treated exactly as the `ziwei/` track
  treats its comparable Wikisource transcription: quotable for research, not a
  controlling edition.
- **zh.wikisource.org (星命溯源, Siku Quanshu)**: Wikisource marks the page
  public domain, consistent with an original compiled in 1781 by an
  editorial board none of whom could plausibly still be in copyright term
  under any jurisdiction.
- **zh.wikipedia.org**: CC BY-SA; quoted here only as attributed secondary
  synthesis pointing to named academic sources, not reproduced at length.

## Access log (this pass, 2026-08-02)

- Downloaded and independently re-hashed `sukuyodo/sources/T21n1308.xml`
  (280,824 bytes, sha256 `464d38d06fb926a7060866d275058802244bef5f4602bfd0b58dc97f59594df8`)
  and `T21n1308_lines.txt` (64,059 bytes, sha256
  `50b9c1481eb25c8eefc97962602cb45f142039fcbe71a2a9df6983e627937a7d`) — both
  match the hashes already recorded by the `sukuyodo` track, confirming this
  pass is reading the identical, unmodified file.
- Downloaded all ten per-juan OCR text files from Internet Archive item
  `guolaoxingzong` (`mdp.39015088726362` through `mdp.39015088726438`) and
  programmatically searched all ten for 周天/紫炁/紫氣/月孛/羅睺/計都: zero
  matches in any file. Manually read juan 1 and juan 2 in full: both are
  dominated by HathiTrust boilerplate and OCR noise, confirming the access-
  quality blocker rather than a absence of the terms in the source.
- Downloaded `GLXZ1_djvu.txt` (77,022 bytes) from Internet Archive item
  `glxz1` via direct HTTP; read in full; only the preface (roughly the first
  40 lines) was legible enough to extract bibliographic information.
- Read `ctext.org/wiki.pl?if=gb&chapter=349444` (and its duplicate,
  `chapter=530323`) via web-mediated extraction across four separate passes
  targeting: general structure, the four-surplus definitional passages, the
  twelve-palace and star-pattern table of contents, and the worked-example
  fragments.
- Read `zh.wikisource.org/.../星命溯源_(四庫全書本)` and juan 1 and juan 2
  specifically, via web-mediated extraction.
- Read `zh.wikipedia.org/zh-tw/七政四餘` via web-mediated extraction, targeting
  the Ziqi-origin and Rahu/Ketu-redefinition passages and the article's own
  citation list.
- Attempted to locate 五星三命指南 via targeted search: no distinct hit found.
- Attempted to locate a primary-text citation for the twelve-branch
  planetary-rulership scheme inside 《張果星宗》, 《星命溯源》, and 《協紀辨方
  書》 (the last checked specifically because it is a comparable Qing
  imperial astro-technical compilation): not found in any of the three within
  this pass's search depth. 《協紀辨方書》's own table of contents (36 juan,
  read via web-mediated extraction) confirms it does not cover the four
  surplus bodies at all — it is a day-selection (擇日) compendium organized
  around sexagenary and trigram systems, not a Qizheng Siyu source, and is
  recorded here only as a negative result closing off one candidate lead.
