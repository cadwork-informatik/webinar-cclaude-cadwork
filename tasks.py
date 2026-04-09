from invoke import Collection, Context, task


# ── server ───────────────────────────────────────────────────────────────────
@task(name="debug-uvicorn")
def debug_uvicorn(c: Context) -> None:
    """Start uvicorn dev server with --reload on port 8000."""
    c.run(
        "uv run uvicorn beam_calc.adapters.web.app:create_app "
        "--factory --reload --port 8000",
        pty=False,
    )


server = Collection("server")
server.add_task(debug_uvicorn)

# ── quality ──────────────────────────────────────────────────────────────────
@task
def lint(c: Context) -> None:
    """Run ruff check + mypy on src and tests."""
    c.run("uv run ruff check src tests", pty=False)
    c.run("uv run mypy src tests", pty=False)


@task
def format(c: Context) -> None:
    """Run ruff format + ruff check --fix on src and tests."""
    c.run("uv run ruff format src tests", pty=False)
    c.run("uv run ruff check --fix src tests", pty=False)


@task
def test(c: Context) -> None:
    """Run the full pytest suite."""
    c.run("uv run pytest", pty=False)


@task
def sync(c: Context) -> None:
    """Install/sync all dependencies including dev extras."""
    c.run("uv sync --extra dev", pty=False)


# ── namespace ────────────────────────────────────────────────────────────────
ns = Collection()
ns.add_collection(server)
ns.add_task(lint)
ns.add_task(format)
ns.add_task(test)
ns.add_task(sync)
