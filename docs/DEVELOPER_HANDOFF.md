# DEVELOPER HANDOFF — how to actually work on this project

**Companion to `docs/HANDOFF.md`.** That one covers the business, the customer situation, and the source policy. This one covers **running, editing, testing, shipping, and verifying** — everything an agent needs to make a change and get it safely in front of users.

**Read section 1 before touching anything.** It is short and it will save you a wasted deploy.

---

# 1. The five things that will bite you

These are not hypothetical. Every one of them cost real time, and four of them produced work that *looked* finished and wasn't.

### 1.1 The deploy image is Python 3.10. Your local is 3.13.

PEP 701 f-strings — nested same-type quotes, backslashes inside the expression — parse fine on 3.13 and **crash the container build**. Always gate:

```bash
py -V:"Astral\CPython3.10.19" -m compileall -q src
```

If that is silent, you are clear. Run it before every commit that touches `src/`.

### 1.2 Emitting is not rendering. Rendering is not shipping.

This project has three layers that can each silently drop your work:

| layer | what "done" looks like | how it fails |
|---|---|---|
| **evidence** (`reading_evidence.py`) | an item appears in the packet | fires, but no renderer prints it |
| **composer** (`reading_composer.py`) | a heading appears in the draft | renders, but the deploy hasn't cut over |
| **live** | text appears in a real report | — |

This bit three separate times in one session. The bounds delineations emitted 8 evidence items and printed **zero** — the report shipped a caveat ("the domicile lord decides whether what the degree carries comes out base or good") attached to a claim that was never made. Lilly's reception was implemented in `calculate_planet_dignity` but the pipeline never passed `other_positions`, so the feature was live in the function and dead in the product.

**The rule: verify at the output, never at the layer you edited.** Generate a real report and grep its text.

An emitter needs all four of these, or it does nothing:
1. an `add(...)` call in `reading_evidence.py`
2. a `_xxx_paragraphs()` renderer in `reading_composer.py`
3. a `_group(packet, "category")` binding
4. a `lines.extend(...)` call site

`test_the_new_v_book_techniques_reach_the_prose_not_only_the_packet` guards this. Extend it when you add a category.

### 1.3 Cloud Run serves old and new instances during a rollout.

One successful request does **not** prove the fleet cut over. Neither does `uptime_seconds` resetting — that happens on any cold start of the *old* revision too.

Wrong: poll `/api/healthz` and trust a low uptime.
Right: poll for a **string only the new code can produce**, or wait for `deploy_cloud_run` to report a terminal state.

```bash
# wait for a marker unique to your change
until curl -s -X POST https://traditional-astrology.com/api/v1/charts/calculate-full \
  -H "Content-Type: application/json" \
  -d '{"date":"1996-08-13","time":"07:18","city":"Fairfield","state":"CA"}' \
  | grep -q "YOUR_NEW_MARKER"; do sleep 20; done
```

### 1.4 Two tests depend on a gitignored directory, so local green ≠ CI green.

`financial_astrology_analysis/` is gitignored ("never ship" research). Two test files import it, so they **pass locally by construction and can only fail in CI**. One imported at module scope, which made a miss a *collection* error that aborted the entire suite and gated the deploy.

To reproduce CI locally, hide the directory — **with a trap**, or an interrupted run leaves it renamed:

```bash
trap 'mv .ci_sim_financial financial_astrology_analysis 2>/dev/null' EXIT INT TERM
mv financial_astrology_analysis .ci_sim_financial
py -3.13 -m pytest src/tests -q
mv .ci_sim_financial financial_astrology_analysis
```

Expect **~1250 passed, 2 skipped**. A local run without hiding it reports ~130 more tests.

### 1.5 A text-layer probe can prove a script is PRESENT. It can never prove one is ABSENT.

Counting Arabic/Greek codepoints in a PDF text layer returned **zero** for a volume dense with both — the OCR fails on non-Latin script and emits garbage Latin instead. That false negative led to declaring a source unavailable twice.

**To establish absence, render the page and look at it.** Same family as declaring a source missing without searching: the negative result feels like evidence and isn't.

---

# 2. Running it locally

```bash
pip install -r requirements.txt
py -3.13 -m uvicorn src.app:app --reload --port 8080
```

Then `http://localhost:8080`. The container runs the same command (`Dockerfile` CMD) on `${PORT:-8080}`.

`src/app.py` mounts the static site **last**, at the root:

```python
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
```

So **API routes win over files**. A file at `src/static/foo.html` is served at `/foo.html`; anything under `/api/...` is handled by a router and never reaches the filesystem.

---

# 3. Editing the website

The site is **51 plain HTML files in `src/static/`** — no framework, no build step, no bundler. Edit the file, reload, done.

| file | is |
|---|---|
| `index.html` | landing page |
| `chart.html` | the chart/reading UI (calls the guest reading API) |
| `faq.html`, `about.html`, `contact.html` | content pages |
| `etsy-astrology-seller.html` | primary SEO landing page |
| `annual-profections.html`, `firdaria-astrology.html`, `almuten-figuris.html`, … | technique/SEO pages |
| `404.html` | not-found page |
| `style.css`, `script.js`, `basic.js` | shared styling and JS |

**To add a page:** drop `newpage.html` into `src/static/`. It is live at `/newpage.html` on the next deploy. Add it to the sitemap and link it from somewhere — orphan pages don't get indexed.

### ⚠ Accounts are RETIRED. The product is guest-only.

There is no login, no signup, and no dashboard. Do not go looking for `login.html` or `signup.html` — **they do not exist as files**, and they should not be recreated. `src/app.py` handles the old URLs explicitly:

- `/profile`, `/owner`, `/src/static/login.html` → a "retired private page" response
- `/account`, `/account.html`, `/dashboard` → `302` redirect to `/#get-reading`
- `/astroforge-vs-astrolabe.html` → `301` to `/#get-reading` (old brand)

A user gets a reading **without an account**, via the guest endpoints below. If you are asked to "fix login", the correct answer is that login was deliberately removed — confirm the intent before rebuilding it.

*(Consequence worth knowing: an unfinished email-verification feature is stashed in git from an earlier session. It is moot while accounts are retired, and shipping it would break signup for a flow that no longer exists.)*

**To change site behaviour**, the front-end talks to these endpoints (see `src/static/chart.html` for the canonical flow):

- `POST /api/v1/premium/guest/request` → `{task_id}` — start a free reading, no auth
- `GET  /api/v1/premium/guest/status/{task_id}` → poll until `status == "completed"`, then read `result.report_markdown`
- `POST /api/v1/charts/calculate-full` — full forensic chart JSON, no auth, no LLM. **Best endpoint for debugging engine changes** — deterministic and fast.

**Do not** hand-edit anything under `src/templates/email/` expecting it to be static — those are Jinja templates rendered by the mailer.

---

# 4. Test / commit / deploy

### The pipeline

```
push to main  →  ci  →  (green)  →  deploy_cloud_run  →  Cloud Run
                   ↓ (red)
                 deploy SKIPPED — prod keeps the old revision
```

**A red CI run is safe, not an outage.** Deploy is gated on it. There is no branch protection, so `git push origin main` is the deploy trigger.

### Before you commit

```bash
py -V:"Astral\CPython3.10.19" -m compileall -q src   # 3.10 gate (§1.1)
# then the CI-equivalent suite (§1.4)
```

### Watching the deploy

```bash
gh run list --branch main --limit 6 \
  --json name,status,conclusion,headSha \
  --jq '.[] | select(.headSha[0:7]=="<sha>") | "\(.name): \(.status)/\(.conclusion)"'
```

Wait for `deploy_cloud_run: completed/success`. Then verify per §1.3.

### Deploy target

`scripts/deploy_cloudrun.py` — project `astrology-engine-prod`, region `us-central1`, service `astrology-engine`. The workflow smoke-checks `https://traditional-astrology.com/api/healthz` after deploying.

---

# 5. Verifying a change on prod

Generate a **real report through the customer path** and grep the text. This is the only check that catches all three failure layers in §1.2.

```bash
TID=$(curl -s -X POST https://traditional-astrology.com/api/v1/premium/guest/request \
  -H "Content-Type: application/json" \
  -d '{"date":"1996-08-13","time":"07:18","city":"Fairfield","state":"CA"}' \
  | py -3.13 -c "import sys,json;print(json.load(sys.stdin)['task_id'])")

# poll until completed, then:
curl -s "https://traditional-astrology.com/api/v1/premium/guest/status/$TID" \
  | py -3.13 -c "import sys,json;print(json.load(sys.stdin)['result']['report_markdown'])" \
  > report.md

grep -c "your new heading" report.md
```

**Take a baseline BEFORE deploying** so the check is falsifiable. If the marker is 0 both before and after, you learn nothing; if it's 0 → N, the change is real.

A useful tell: if the **word count is identical across runs**, you are looking at the old code. Two runs of the same chart on the same revision produce the same deterministic draft.

---

# 6. The reading pipeline, end to end

```
birth data
   ↓  src/services/engine_bridge.py :: generate_full_nativity_async
   ↓  src/engine/forensic_engine.py :: Auditor          → analysis{} (all the astrology)
   ↓  src/services/reading_evidence.py :: build_reading_evidence  → evidence packet
   ↓  src/services/reading_composer.py :: compose_deterministic_draft → markdown draft
   ↓  LLM editor pass (tier `free` / `free_instant`: 0, deterministic; some other free_* tiers: 1)
   ↓  src/services/reading_contract.py :: validate/enforce   ← FAIL-CLOSED
   ↓  report_markdown
```

**The contract is fail-closed**: a violation means the customer gets *nothing*, not a trimmed report. Check `src/services/reading_contract.py` before adding prose that could trip it. The live checks are:

`internal_output` (leaked enums/paths) · `fatalistic_claim` · `doctrine_overreach` · `protected_directive` · `outer_planet_core`

There is deliberately **no word ceiling** and **no medical filter** — both were removed on 2026-08-11, with reasons in the file. Do not reinstate either without reading those comments; the medical filter was censoring the source texts, and the word cap was rejecting reports for the size of their own citation appendix.

---

# 7. The doctrine registry — how a rule earns its status

`src/database/data/doctrine_sources.json` → `verified_rules`. Every rule carries `edition_id`, `location`, `verification`, `verified_summary`, `publication_limit`.

**Status ladder**, honest names, no rounding up:

- `translation_inspected` — read only in a modern translation
- `facsimile_inspected_*` — read in a facsimile of the original printing
- `greek_text_read_directly` / `latin_…` / `arabic_text_read_directly` — read in the original language
- `…_partial` — some cited chapters read, others not. **Use it. It is not a failure.**
- `…_source_editorially_corrupt` — read, and the critical apparatus says the passage is damaged

**Two standing warnings from a full audit pass:**

1. **Printed page numbers in `location` are suspect.** Four Ptolemy rules cited pages that land in the wrong chapter of the edition on disk — Robbins-Loeb pagination inside Teubner citations. **Cite the chapter, not the page**, and verify any page number against the actual scan.
2. **Critical editions carry warnings translations hide.** Paulus ch. 24 has an `additamentum Z` (a span in one manuscript, absent from three others); ch. 32 carries Schato's *mutilus et depravatus*. A translation prints continuous text and the sigla simply are not there. This is the whole argument for reading critical editions.

**Adding or upgrading a rule changes tests.** Six tests assert specific `verification` strings. That is the system working — update the assertion *with the reason inline*, never delete it.

---

# 8. Reading primary sources

Scans live in `tmp/acquire/pdfs/` (gitignored — large, and not ours to redistribute).

```bash
py -3.13 scripts/composite_pages.py <pdf> <outdir> --start N --count M --per-image {1,2,4,6,8}
```

`--per-image 1` for legibility on dense apparatus; `2` is the usual working default; `4`+ for surveying structure.

**Always verify pagination against the scan's own printed folio number.** Filename ≠ printed page, and the offset is **not** constant across a volume — it held at 18 for Valens Book VIII and drifted inside Book VII. Mappings established so far:

| volume | mapping |
|---|---|
| Valens (Kroll 1908) | ~`printed = filename − 18`, **verify per book** |
| Paulus (Boer 1958) | `PDF = (printed + 26) / 2`; composites are 4 printed pages each |
| Dorotheus (Pingree 1976) | `printed_left = pdf × 2 − 18` |
| Picatrix (Ritter) | `folio = 420 − page` |

On disk and **unread**: Hephaistio (2 vols, Greek), Olympiodorus on Paulus (Greek), Abū Maʿshar (Arabic), Sahl, Bonatti, Morin, Māshāʾallāh, Lydus, three CCAG volumes. Plus most of Lilly's 894 pages and Firmicus's 938.

**Acquisition as of 2026-08-16:** all 37 rules have an original-language source on disk. al-Biruni: Wright 1934 English + Persian *Tafhim* (not the Arabic facing MS). Ibn Ezra: LJS 57 (1361 Hebrew) — *Reshit Hokhmah* / *Mivharim* / *Olam*, not *Moladot* or *Tequfah*. Claude cannot read the Sephardic semi-cursive; those two rules stay at parallel-text status. See `docs/sources/ACQUISITIONS.md`.

---

# 9. Working habits that paid off

- **Record gaps; never fill them by guessing.** A gap is a decision waiting for a human. A guessed value is a bug wearing a citation. Two live examples: the Dorotheus Virgo/Mercury *share* has no stated weight, so it stays out; Lilly's reception weights are printed (5 and 4), so they went in.
- **An expected-but-absent thing may never have existed.** A recorded "Jupiter's line lost to OCR" turned out to be Ptolemy giving Jupiter and Venus **one shared clause** — four clauses for five planets. The gap invited someone to invent doctrine to fill it.
- **Check whether it already exists before building it.** A decennial cascade was built from scratch that `src/engine/decennials.py` already had, better. Grep first.
- **Reading originals mostly confirms existing code.** That is the point, not a disappointment. Its value shows up in the exceptions.

---

# 10. Open decisions for the owner

- [ ] **Ptolemy's benefic rescue orbs** — Jupiter 12°, Venus 8°. Explicit in the source; sits on the protected longevity path, so the blast radius is larger than Lilly's reception was.
- [ ] **Dorotheus Virgo/Mercury triplicity share** — حظّ states no weight. Implementing means inventing a number. Recommend leaving out unless you want a documented house-rule.
- [ ] Everything in `docs/HANDOFF.md` section 11 (pricing, free-vs-paid, multi-tradition scope). Water triplicity is confirmed; see the 2026-08-16 state block.
