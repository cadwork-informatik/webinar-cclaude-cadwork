#!/bin/bash
# Stop hook — nudges /clean-post-plan when Python changes are detected.
CLAUDE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNNING="$CLAUDE_DIR/.post-plan-running"
FINGERPRINT="$CLAUDE_DIR/.post-plan-fingerprint"

# Phase 2: cleanup already ran — save fingerprint and allow stop.
if [ -f "$RUNNING" ]; then
    rm -f "$RUNNING"
    { git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; } \
        | grep -E '\.py$' | sort -u | md5sum > "$FINGERPRINT"
    exit 0
fi

CHANGED_PY=$(git diff --name-only HEAD 2>/dev/null | grep -E '\.py$' | head -1)
if [ -z "$CHANGED_PY" ]; then
    CHANGED_PY=$(git diff --cached --name-only 2>/dev/null | grep -E '\.py$' | head -1)
fi

if [ -z "$CHANGED_PY" ]; then
    rm -f "$FINGERPRINT"
    exit 0
fi

# Skip if we already cleaned this exact changeset.
if [ -f "$FINGERPRINT" ]; then
    CURRENT=$({ git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; } \
        | grep -E '\.py$' | sort -u | md5sum)
    PREVIOUS=$(cat "$FINGERPRINT")
    if [ "$CURRENT" = "$PREVIOUS" ]; then
        exit 0
    fi
    rm -f "$FINGERPRINT"
fi

touch "$RUNNING"

CHANGED_COUNT=$({ git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; } \
    | grep -E '\.py$' | sort -u | wc -l)
if [ "$CHANGED_COUNT" -gt 50 ]; then
    rm -f "$RUNNING"
    echo "Large Python changeset ($CHANGED_COUNT files) — skipping auto /clean-post-plan. Run manually." >&2
    exit 0
fi

echo "Python code changes detected. Run /clean-post-plan to clean dead code and verify CLAUDE.md compliance." >&2
exit 2
