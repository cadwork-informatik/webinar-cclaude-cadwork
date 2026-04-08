---
name: verify-ui
description: Drive the running beam designer at http://localhost:8000 via Playwright MCP and verify the UI round-trip.
---

Spawn the `verify-ui` agent. It will:

1. Navigate to `http://localhost:8000` (server must already be running — see `/start-server`).
2. Snapshot + screenshot the form.
3. Fill the canonical default beam (L=5, 120×240, g_k=2, q_k=3, C24, SC1, medium) and submit.
4. Verify ULS/SLS badges + Plotly chart render.
5. Capture console and network errors.
6. Return VERIFY-UI: PASS / FAIL.

**Mandatory** after any change under `src/beam_calc/adapters/web/` per `CLAUDE.md`.
