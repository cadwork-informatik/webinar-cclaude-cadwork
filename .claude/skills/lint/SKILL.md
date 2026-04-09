---
name: lint
description: Run ruff check and mypy against src and tests to catch lint and type errors.
---

Run both linting and type checking sequentially:

```bash
uv run ruff check src tests
uv run mypy src
```

Report the combined output. Do not auto-fix — use `/format` for that.
