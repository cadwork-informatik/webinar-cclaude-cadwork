"""Integration tests — BeamDesignService wired to real in-memory repo, no network."""

from __future__ import annotations

import pytest

from beam_calc.adapters.timber_repository import InMemoryTimberRepository
from beam_calc.application.beam_service import BeamDesignService, DesignRequest
from beam_calc.domain.timber import LoadDuration, ServiceClass

pytestmark = pytest.mark.integration


def test_service_designs_default_beam() -> None:
    service = BeamDesignService(timber_repo=InMemoryTimberRepository())
    report = service.design(
        DesignRequest(
            name="Test beam",
            span_m=5.0,
            width_mm=120,
            height_mm=240,
            g_k=2.0,
            q_k=3.0,
            timber_class="C24",
            service_class=ServiceClass.SC1,
            duration=LoadDuration.MEDIUM,
        )
    )
    assert report.uls.M_d_kNm == pytest.approx(22.5)
    assert report.sls.w_inst_mm > 0
    assert report.diagrams.x_m[0] == 0.0


def test_service_lists_available_classes() -> None:
    service = BeamDesignService(timber_repo=InMemoryTimberRepository())
    classes = service.available_classes()
    assert "C24" in classes
    assert len(classes) >= 4
