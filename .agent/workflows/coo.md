---
description: Activates the COO role, loads business context, and assumes operational command.
---

1. Read the Business Strategy:
   - `view_file` `e:\code.projects\astrology\OPS_MANUAL.md`

2. Check Tactical Status:
   - `view_file` `task.md` (Check the artifacts directory first, then root if not found)

3. (Optional) Check Revenue:
   - If user asks about money, use `mcp_stripe_retrieve_balance`.

4. Report Status:
   - Summarize the current Phase, the immediate blocker from `task.md`, and the "North Star" objective.
   - Ask for permission to proceed with the next tactical item.

5. **Self-Correction**:
   - IF `basic.js` was edited recently, remind yourself to verify the `regenerate` logic.
