---
name: review-code
description: Deep code review of branch changes via the code-reviewer agent (hexagonal + typing + EC5 correctness).
---

Spawn the `code-reviewer` agent on the current branch's changes vs `main`.

Instruct it to:
- Only review files in `git diff --name-only main...HEAD`
- Report blocking issues, warnings, and nits
- Do NOT edit files

Relay its full report back to the user.
