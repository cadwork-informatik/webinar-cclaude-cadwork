---
name: start-server
description: Start the FastAPI beam designer on port 8000 for manual or Playwright testing.
---

Run this in the background:

```bash
uv run uvicorn beam_calc.adapters.web.app:create_app --factory --reload --port 8000
```

Wait a second, then confirm `http://localhost:8000` responds (curl or TestClient). Keep the server
running so `/verify-ui` can drive it.
