---
name: clean-post-plan
description: Run post-plan-cleaner and guidelines-verifier in parallel against changed Python files.
---

Spawn TWO agents **in parallel** (single message, two tool calls):

1. `post-plan-cleaner` — edits changed `.py` files: ruff format/fix, remove dead imports & debug prints.
2. `guidelines-verifier` — read-only check against `CLAUDE.md` (layer imports, typing, Port suffix, etc.).

When both finish, combine their reports:
- Cleaner: what was changed.
- Verifier: PASS/FAIL per rule + violations list.

If the verifier reports violations, surface them prominently — they need user attention before the plan can be considered done.
