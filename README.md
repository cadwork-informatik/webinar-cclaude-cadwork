# webinar-cclaude-cadwork — pro branch

EC5 timber beam designer built with **hexagonal architecture** and a professional
Claude Code setup (agents, hooks, skills, MCP). Demo project for the Claude Code webinar.

## Run

```bash
pip install -e ".[dev]"
uvicorn beam_calc.adapters.web.app:create_app --factory --reload --port 8000
```

Open http://localhost:8000.

## Test

```bash
pytest                  # all categories
pytest -m unit          # domain only
pytest -m integration   # + adapters
pytest -m smoke         # + web round-trip
ruff check src tests
mypy src
```

## Claude Code workflow

- `/start-server` — boot uvicorn for manual or Playwright testing.
- `/run-tests` — test-runner agent, categorized report.
- `/review-code` — code-reviewer agent, hexagonal boundary + typing review.
- `/verify-ui` — verify-ui agent drives the page via Playwright MCP (mandatory after any UI change).
- `/clean-post-plan` — post-plan-cleaner + guidelines-verifier in parallel.

See `CLAUDE.md` for architecture & testing rules.
