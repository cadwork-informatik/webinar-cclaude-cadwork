---
name: drift-check
description: Detect test coverage gaps and CLAUDE.md structural drift (read-only report).
---

Spawn the `drift-checker` agent on the full codebase.

Instruct it to:
- Run all checks (Categories A and B)
- Do NOT edit any files
- Produce the full Drift Report

Relay its complete report back to the user.
