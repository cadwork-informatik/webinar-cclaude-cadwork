"""Standalone drift checker — mirrors .claude/agents/drift-checker.md logic.

Produces a Markdown drift report on stdout.
Exit code: 0 = clean, 1 = drift detected.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "beam_calc"
TESTS = ROOT / "tests"
CLAUDE_MD = ROOT / "CLAUDE.md"
SKILLS_DIR = ROOT / ".claude" / "skills"
AGENTS_DIR = ROOT / ".claude" / "agents"
HOOKS_DIR = ROOT / ".claude" / "hooks"
SETTINGS = ROOT / ".claude" / "settings.json"

EXEMPT_MODULES = {"__init__.py", "ports.py"}

LAYER_DIRS = [
    SRC / "domain",
    SRC / "application",
    SRC / "adapters",
    TESTS / "unit",
    TESTS / "integration",
    TESTS / "smoke",
]


def _src_modules() -> list[Path]:
    return [
        p
        for p in SRC.rglob("*.py")
        if p.name not in EXEMPT_MODULES
    ]


def _test_files() -> list[Path]:
    return list(TESTS.rglob("*.py"))


def _module_dotpath(p: Path) -> str:
    rel = p.relative_to(ROOT / "src")
    return str(rel.with_suffix("")).replace("\\", "/").replace("/", ".")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


# ── A1: Module coverage matrix ──────────────────────────────────────────


def check_a1() -> tuple[list[tuple[str, str, str]], bool]:
    rows: list[tuple[str, str, str]] = []
    drift = False
    test_contents = {tf: _read(tf) for tf in _test_files()}

    for mod in sorted(_src_modules()):
        dotpath = _module_dotpath(mod)
        covering = [
            tf.relative_to(ROOT).as_posix()
            for tf, content in test_contents.items()
            if dotpath in content
        ]
        if covering:
            rows.append((mod.relative_to(SRC).as_posix(), ", ".join(covering), "COVERED"))
        else:
            rows.append((mod.relative_to(SRC).as_posix(), "-", "GAP"))
            drift = True
    return rows, drift


# ── A2: Untested public functions ────────────────────────────────────────

_PUB_FUNC = re.compile(r"^(?:    )?def ([a-z]\w+)\(", re.MULTILINE)


def check_a2() -> tuple[list[str], bool]:
    untested: list[str] = []
    test_blob = "\n".join(_read(tf) for tf in _test_files())
    target_dirs = [SRC / "domain", SRC / "application"]

    for d in target_dirs:
        for mod in sorted(d.rglob("*.py")):
            if mod.name in EXEMPT_MODULES:
                continue
            source = _read(mod)
            for m in _PUB_FUNC.finditer(source):
                fname = m.group(1)
                if fname.startswith("_"):
                    continue
                if fname not in test_blob:
                    label = mod.relative_to(SRC).as_posix()
                    untested.append(f"`{label}::{fname}()`")
    return untested, bool(untested)


# ── A3: Test placement ───────────────────────────────────────────────────


def check_a3() -> tuple[list[str], bool]:
    issues: list[str] = []
    unit_dir = TESTS / "unit"
    smoke_dir = TESTS / "smoke"

    for tf in sorted(unit_dir.glob("*.py")):
        if "beam_calc.adapters.web" in _read(tf):
            issues.append(f"Unit test `{tf.name}` imports from `adapters.web` (should not)")

    for tf in sorted(smoke_dir.glob("*.py")):
        content = _read(tf)
        if "TestClient" not in content and "beam_calc.adapters.web" not in content:
            issues.append(f"Smoke test `{tf.name}` uses neither TestClient nor web imports (may be misplaced)")

    return issues, bool(issues)


# ── B1: Layer directories ───────────────────────────────────────────────


def check_b1() -> tuple[list[str], bool]:
    issues: list[str] = []
    for d in LAYER_DIRS:
        if not d.is_dir() or not list(d.glob("*.py")):
            issues.append(f"Missing or empty: `{d.relative_to(ROOT).as_posix()}`")
    return issues, bool(issues)


# ── B2: Slash commands table ─────────────────────────────────────────────


def check_b2() -> tuple[list[str], bool]:
    issues: list[str] = []
    claude_text = _read(CLAUDE_MD)

    table_cmds: set[str] = set()
    for m in re.finditer(r"\|\s*`?/([^`|\s]+)`?\s*\|", claude_text):
        table_cmds.add(m.group(1))

    disk_skills = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}

    for cmd in sorted(table_cmds - disk_skills):
        issues.append(f"CLAUDE.md lists `/{cmd}` but `.claude/skills/{cmd}/SKILL.md` missing")
    for skill in sorted(disk_skills - table_cmds):
        issues.append(f"Skill `{skill}` exists on disk but not in CLAUDE.md table")

    return issues, bool(issues)


# ── B3: Agent references ────────────────────────────────────────────────


def check_b3() -> tuple[list[str], bool]:
    issues: list[str] = []
    claude_text = _read(CLAUDE_MD)

    mentioned: set[str] = set()
    for m in re.finditer(r"(\w[\w-]+)\s+agent", claude_text):
        mentioned.add(m.group(1))
    for m in re.finditer(r"`([\w-]+)`", claude_text):
        candidate = m.group(1)
        if (AGENTS_DIR / f"{candidate}.md").exists():
            mentioned.add(candidate)

    disk_agents = {p.stem for p in AGENTS_DIR.glob("*.md")}

    for agent in sorted(mentioned - disk_agents):
        issues.append(f"CLAUDE.md mentions `{agent}` agent but `.claude/agents/{agent}.md` missing")
    for agent in sorted(disk_agents - mentioned):
        issues.append(f"Agent `{agent}` exists on disk but not referenced in CLAUDE.md")

    return issues, bool(issues)


# ── B4: Hook scripts ────────────────────────────────────────────────────


def check_b4() -> tuple[list[str], bool]:
    issues: list[str] = []
    claude_text = _read(CLAUDE_MD)

    for m in re.finditer(r"`([\w-]+\.sh)`", claude_text):
        script = m.group(1)
        if not (HOOKS_DIR / script).exists():
            issues.append(f"CLAUDE.md references `{script}` but not found in `.claude/hooks/`")

    return issues, bool(issues)


# ── B5: Settings ↔ Skills sync ──────────────────────────────────────────


def check_b5() -> tuple[list[str], bool]:
    issues: list[str] = []
    settings = json.loads(_read(SETTINGS))

    settings_skills: set[str] = set()
    for entry in settings.get("permissions", {}).get("allow", []):
        m = re.match(r"Skill\((\S+)\)", entry)
        if m:
            settings_skills.add(m.group(1))

    disk_skills = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}

    for s in sorted(settings_skills - disk_skills):
        issues.append(f"Settings allows `Skill({s})` but skill dir missing on disk")
    for s in sorted(disk_skills - settings_skills):
        issues.append(f"Skill `{s}` on disk but not in settings.json permissions")

    return issues, bool(issues)


# ── Report ───────────────────────────────────────────────────────────────


def main() -> int:
    drift_found = False

    lines: list[str] = ["# Drift Report", ""]

    # ── A) Test coverage ──
    lines.append("## A) Test <-> Code Coverage")
    lines.append("")

    a1_rows, a1_drift = check_a1()
    drift_found |= a1_drift
    lines.append("### Module Coverage Matrix")
    lines.append("| Source Module | Test File(s) | Status |")
    lines.append("|---|---|---|")
    for mod, tests, status in a1_rows:
        lines.append(f"| {mod} | {tests} | {status} |")
    lines.append("")

    a2_untested, a2_drift = check_a2()
    drift_found |= a2_drift
    lines.append("### Untested Public Functions")
    if a2_untested:
        for u in a2_untested:
            lines.append(f"- {u} — no direct test reference")
    else:
        lines.append("- None found — all public functions have test references")
    lines.append("")

    a3_issues, a3_drift = check_a3()
    drift_found |= a3_drift
    lines.append("### Test Placement")
    if a3_issues:
        for issue in a3_issues:
            lines.append(f"- ISSUE: {issue}")
    else:
        lines.append("- OK: all tests correctly placed")
    lines.append("")

    # ── B) CLAUDE.md sync ──
    lines.append("## B) CLAUDE.md <-> Codebase")
    lines.append("")
    lines.append("| Check | Status | Detail |")
    lines.append("|---|---|---|")

    b1_issues, b1_drift = check_b1()
    drift_found |= b1_drift
    lines.append(f"| Layer directories | {'DRIFT' if b1_drift else 'PASS'} | {'; '.join(b1_issues) or 'All present'} |")

    b2_issues, b2_drift = check_b2()
    drift_found |= b2_drift
    lines.append(f"| Slash commands table | {'DRIFT' if b2_drift else 'PASS'} | {'; '.join(b2_issues) or 'All match'} |")

    b3_issues, b3_drift = check_b3()
    drift_found |= b3_drift
    lines.append(f"| Agent references | {'DRIFT' if b3_drift else 'PASS'} | {'; '.join(b3_issues) or 'All match'} |")

    b4_issues, b4_drift = check_b4()
    drift_found |= b4_drift
    lines.append(f"| Hook scripts | {'DRIFT' if b4_drift else 'PASS'} | {'; '.join(b4_issues) or 'All present'} |")

    b5_issues, b5_drift = check_b5()
    drift_found |= b5_drift
    lines.append(f"| Settings <-> Skills sync | {'DRIFT' if b5_drift else 'PASS'} | {'; '.join(b5_issues) or 'All match'} |")
    lines.append("")

    # ── Summary ──
    gap_count = sum(1 for _, _, s in a1_rows if s == "GAP")
    func_count = len(a2_untested)
    claude_drift_count = sum(len(x) for x in [b1_issues, b2_issues, b3_issues, b4_issues, b5_issues])

    severity = "LOW"
    if gap_count > 0:
        severity = "HIGH"
    elif func_count > 0 or claude_drift_count > 0:
        severity = "MEDIUM"

    lines.append("## Summary")
    lines.append(f"- Test coverage gaps: {gap_count} modules, {func_count} functions")
    lines.append(f"- CLAUDE.md drift: {claude_drift_count} items")
    lines.append(f"- Severity: {severity}")
    lines.append("")
    verdict = "DRIFT DETECTED" if drift_found else "CLEAN"
    lines.append(f"**VERDICT: {verdict}**")

    report = "\n".join(lines)
    print(report)
    return 1 if drift_found else 0


if __name__ == "__main__":
    sys.exit(main())
