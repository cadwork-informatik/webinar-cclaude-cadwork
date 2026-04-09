---
name: format
description: Run ruff format and ruff check --fix on src and tests to auto-fix style issues.
---

Run formatting and auto-fixable lint corrections:

```bash
uv run ruff format src tests
uv run ruff check --fix src tests
```

Report what changed (if anything).
