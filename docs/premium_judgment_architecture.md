# Premium Judgment Architecture

The premium reading is built in four layers. Each layer has one job, and later
layers may not overwrite facts established by earlier ones.

## 1. Calculation

`src/engine/forensic_engine.py` remains the central calculator. It supplies the
astronomical positions, sect, planetary condition, aspects, receptions, ruler
chains, lots, source-audited doctrine, longevity branches, and timing systems.

The composer never recalculates a missing placement and never invents an aspect.

## 2. Admitted Evidence

`src/services/reading_evidence.py` converts the engine payload into individually
cited evidence items. Every item records its authority, verification state,
provenance, interpretive limit, and structured details.

This is the publication boundary. A claim absent from the evidence packet cannot
be added by either the deterministic composer or an optional language model.

## 3. Judgment Planning

`src/services/judgment_planner.py` ranks the admitted evidence before prose is
written. It determines:

- the actual Ascendant ruler and tenth-place ruler;
- the strongest usable planet, based on condition, angularity, rulership, joy,
  motion, and maltreatment;
- the dominant final dispositor and the number of chains ending there;
- the largest connected hard-aspect network, its houses, and its hubs;
- the relationship of the two lights;
- the rulers repeated across the active timing systems.

The planner is generic. It does not assume Mercury rules the chart, that the
lights occupy the twelfth, that Fortune is in Leo, or that the surviving
longevity branch equals 76 years.

## 4. Customer Reading

`src/services/reading_composer.py` writes the report in judgment order:

1. direct chart verdict;
2. strongest source of agency;
3. governing contradiction between agency and final disposition;
4. principal pressure network;
5. person-level and life-topic judgments;
6. complete planetary, house, lot, longevity, and timing proof;
7. doctrinal disagreements and evidence ledger.

The deterministic report is always available. An optional language model may
rewrite it for cadence and transitions, but it receives the bounded evidence
packet, must preserve citations and severe testimony, and must pass the same
publication contract before its prose can ship.

## Regression Gates

The test suite includes deliberately different charts to prevent one customer's
placements from leaking into another customer's prose. Current gates verify:

- a Mars-ruled alternate chart ranks Mars rather than Mercury as the helm;
- a Jupiter 63.5-year longevity branch does not inherit the Fairfield Mercury
  76-year result;
- doryphory uses the actual guard and luminary;
- lunar-mansion prose uses the actual Moon position without inventing natal
  meanings from electional material;
- every Hermetic lot follows its actual house, ruler, and condition.

The final report must also pass citation validation, publication-contract
validation, word-count and coverage checks, PDF rendering, and representative
visual inspection.
