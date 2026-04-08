#!/bin/bash
# PostToolUse hook — runs ruff format + ruff check --fix on the file just edited/written.
FILE="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"

if [ -z "$FILE" ]; then
    exit 0
fi

# Only Python files
if [[ "$FILE" != *.py ]]; then
    exit 0
fi

cd "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || exit 0

# Format, then autofix lint. Silent on success; swallow errors so the hook never blocks.
uv run ruff format "$FILE" 2>/dev/null
uv run ruff check --fix "$FILE" 2>/dev/null
exit 0
