"""Unit tests — pure domain checks, no I/O."""
from __future__ import annotations

import pytest

from beam_calc.domain.beam import Beam, RectangularSection, UniformLoads
from beam_calc.domain.checks import diagrams, sls_deflection, uls_bending
from beam_calc.domain.timber import LoadDuration, ServiceClass, TimberProperties

pytestmark = pytest.mark.unit

C24 = TimberProperties("C24", f_m_k=24.0, E_0_mean=11000.0)


def _default_beam() -> Beam:
    return Beam(
        span_m=5.0,
        section=RectangularSection(width_mm=120, height_mm=240),
        timber=C24,
        loads=UniformLoads(g_k=2.0, q_k=3.0),
        service_class=ServiceClass.SC1,
        duration=LoadDuration.MEDIUM,
    )


def test_uls_bending_canonical_beam_passes() -> None:
    res = uls_bending(_default_beam())
    # q_d = 1.35*2 + 1.5*3 = 7.2 kN/m; M_d = 7.2*25/8 = 22.5 kNm
    assert res.q_d_kN_per_m == pytest.approx(7.2)
    assert res.M_d_kNm == pytest.approx(22.5)
    # W = 120*240^2/6 = 1_152_000 mm3; sigma = 22.5e6/1.152e6 ≈ 19.531 N/mm2
    assert res.sigma_m_d == pytest.approx(19.53125, rel=1e-4)
    # f_m_d = 0.8 * 24 / 1.3 ≈ 14.769 N/mm2
    assert res.f_m_d == pytest.approx(14.76923, rel=1e-4)
    assert res.ratio > 1.0  # default beam actually fails ULS — good teaching moment
    assert res.passes is False


def test_sls_deflection_magnitudes() -> None:
    res = sls_deflection(_default_beam())
    assert res.w_lim_inst_mm == pytest.approx(5000 / 300)
    assert res.w_lim_fin_mm == pytest.approx(5000 / 250)
    assert res.w_fin_mm > res.w_inst_mm  # creep amplifies


def test_diagrams_endpoints_zero_moment() -> None:
    d = diagrams(_default_beam(), n=20)
    assert d.M_kNm[0] == pytest.approx(0.0)
    assert d.M_kNm[-1] == pytest.approx(0.0)
    assert len(d.x_m) == 21
