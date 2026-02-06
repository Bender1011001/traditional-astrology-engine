# The Rule Ledger

The Rule Ledger is the "black box recorder" of the engine.

## Purpose
To ensure that every astrological judgment can be audited and traced to a source.

## Structure
A list of `RuleEntry` objects (serialized as JSON).

| Field | Description |
| :--- | :--- |
| `rule_id` | Unique slug (e.g., `mars-in-aries-rulership`) |
| `definition` | The logic applied (e.g., "Planet is in its Domicile") |
| `source` | Citation (e.g., "Ptolemy, Tetrabiblos I.4") |
| `value` | The output score or boolean result |
