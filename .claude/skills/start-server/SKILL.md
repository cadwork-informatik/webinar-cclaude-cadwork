---
name: start-server
description: Health-check that the FastAPI beam designer is reachable on port 8000 (user-managed server).
---

**Do NOT start, restart, or kill the server.** The user manages it themselves.

Check that `http://localhost:8000` responds:

```bash
curl -sf http://localhost:8000 > /dev/null && echo "Server is up" || echo "Server is NOT running — ask the user to start it with: uv run invoke server.debug-uvicorn"
```

If the server is not running, inform the user and stop. Never spawn uvicorn or run a background process.
