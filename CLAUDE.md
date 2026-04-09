# CLAUDE.md — beam-calc project guidelines

This repository is an EC5 timber beam designer organized in **hexagonal architecture**.
Claude Code MUST follow these rules on every task.

## Architecture (non-negotiable)

Layers live under `src/beam_calc/`:

1. **`domain/`** — pure Python. Zero framework imports (no FastAPI, pydantic, Jinja, Plotly, httpx).
   No I/O. No logging. Dataclasses and functions only. Contains the EC5 formulas.
2. **`application/`** — depends only on `domain/`. Defines ports as `typing.Protocol` in `ports.py`
   (suffix `Port`). Services orchestrate domain objects. No framework imports.
3. **`adapters/`** — the **only** layer allowed to import FastAPI, pydantic, Jinja, Plotly, databases,
   HTTP clients, or anything I/O. Adapters implement ports.

**Forbidden cross-layer imports:**
- `domain/` importing from `application/` or `adapters/` — never.
- `application/` importing from `adapters/` — never.
- `adapters/web/` importing other adapters' internals — go through `application/` services.

## Naming

- Modules & functions: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Ports: Protocol classes suffixed `Port` (e.g. `TimberPropertyPort`).
- Tests: files named `test_*.py`, colocated by category under `tests/{unit,integration,smoke}/`.

## Typing & style

- **Full type hints** on every function signature. No `Any`. Use `unknown`-ish patterns
  (`object`, generics) if truly dynamic.
- No bare `except:`. Catch specific exceptions.
- No `print()` for debugging — use `logging` in adapters; domain stays silent.
- `from __future__ import annotations` at the top of every new module.
- `uv run ruff check` and `uv run mypy` must pass before any commit.

## Testing

Three categories, colocated:

- `tests/unit/` — pure domain, no I/O, no fixtures beyond dataclass construction. Fast.
- `tests/integration/` — real in-process adapters (e.g. `InMemoryTimberRepository`). **No network.**
- `tests/smoke/` — FastAPI `TestClient` round-trips.

Every new domain function or application service ships with a unit test in the same PR.
Run tests via the `/run-tests` skill (spawns the test-runner agent).

## UI verification (mandatory, no confirmation needed)

Any modification that has an impact on the front-end — whether it touches `adapters/web/` (routes,
templates, schemas), domain logic that affects displayed results, or application services that feed
the UI — is **not complete** until `/verify-ui` has been run against a local server. The skill
spawns the `verify-ui` agent, which drives the page via the Playwright MCP, takes a screenshot,
and checks for browser console errors.

**Do not ask the user for permission** — just run `/start-server` then `/verify-ui` automatically
whenever a change may affect the UI. This is a required step, not an optional one.

## Tooling workflow

This project uses **`uv`** for Python management. All commands are prefixed with `uv run` so the
correct environment is used regardless of the user's shell activation state.

### Slash commands (skills)

| Command | What it does |
|---|---|
| `/sync` | `uv sync --extra dev` — install/sync all dependencies |
| `/start-server` | Start the FastAPI server on port 8000 (background, with `--reload`) |
| `/lint` | Run `ruff check` + `mypy` on `src` and `tests` |
| `/format` | Run `ruff format` + `ruff check --fix` on `src` and `tests` |
| `/run-tests` | Run `pytest` via the test-runner agent with per-category triage |
| `/review-code` | Deep code review of branch changes (hexagonal + typing + EC5) |
| `/clean-post-plan` | Post-plan cleanup: ruff fix + guidelines verification in parallel |
| `/drift-check` | Detect test coverage gaps and CLAUDE.md structural drift (read-only report) |
| `/verify-ui` | Drive the running server via Playwright, verify UI round-trip |
| `/grill-me` | **Planning only.** Interview the user about a plan/design until shared understanding |

### Automated hooks

- Edit a `.py` file → the `format-py.sh` PostToolUse hook runs `uv run ruff format` + `uv run ruff check --fix`.
- Finish a plan with `.py` changes → the `post-plan-stop.sh` Stop hook prompts `/clean-post-plan`,
  which runs `post-plan-cleaner` and `guidelines-verifier` in parallel.

### Plan preparation (mandatory, planning phase only)

Before implementing any non-trivial plan, run `/grill-me` to stress-test the design with the user.
This ensures all design decisions are resolved **before** writing code. `/grill-me` is strictly a
planning tool — do not invoke it during implementation or review phases.

### Pre-commit checklist

Before completing any substantial change: `/review-code` (code-reviewer agent) and `/run-tests`.
