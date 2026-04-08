"""Smoke tests — FastAPI TestClient round-trip."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from beam_calc.adapters.web.app import create_app

pytestmark = pytest.mark.smoke


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_get_index_renders_form(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "EC5 Timber Beam Designer" in r.text
    assert '<form method="post">' in r.text


def test_post_default_inputs_returns_results(client: TestClient) -> None:
    r = client.post(
        "/",
        data={
            "span_m": 5.0,
            "width_mm": 120,
            "height_mm": 240,
            "g_k": 2.0,
            "q_k": 3.0,
            "timber_class": "C24",
            "service_class": 1,
            "duration": "medium",
        },
    )
    assert r.status_code == 200
    assert "ULS" in r.text
    assert "SLS" in r.text
    assert "chart" in r.text
