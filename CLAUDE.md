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
- `ruff check` and `mypy --strict` must pass before any commit.

## Testing

Three categories, colocated:

- `tests/unit/` — pure domain, no I/O, no fixtures beyond dataclass construction. Fast.
- `tests/integration/` — real in-process adapters (e.g. `InMemoryTimberRepository`). **No network.**
- `tests/smoke/` — FastAPI `TestClient` round-trips.

Every new domain function or application service ships with a unit test in the same PR.
Run tests via the `/run-tests` skill (spawns the test-runner agent).

## UI verification (mandatory)

Any change that touches `adapters/web/` — routes, templates, schemas — is **not complete** until
`/verify-ui` has been run against a local server. The skill spawns the `verify-ui` agent, which
drives the page via the Playwright MCP, takes a screenshot, and checks for browser console errors.

Start the server for verification with `/start-server`.

## Tooling workflow

- Edit a `.py` file → the `format-py.sh` PostToolUse hook runs `ruff format` + `ruff check --fix`.
- Finish a plan with `.py` changes → the `post-plan-stop.sh` Stop hook prompts `/clean-post-plan`,
  which runs `post-plan-cleaner` and `guidelines-verifier` in parallel.
- Before completing any substantial change: `/review-code` (code-reviewer agent) and `/run-tests`.
