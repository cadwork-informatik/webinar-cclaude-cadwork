---
name: run-tests
description: Run the pytest suite via the test-runner agent with per-category triage.
---

Spawn the `test-runner` agent. It will:

1. Run `pytest -q`.
2. If failures, re-run per marker (`unit`, `integration`, `smoke`) to localize.
3. Triage each failure (file:line + likely cause).
4. Return GREEN or RED verdict.

Relay the report to the user. Do not fix code automatically.
