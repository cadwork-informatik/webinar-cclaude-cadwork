"""Pure EC5 design checks — no I/O, no framework."""
from __future__ import annotations

from dataclasses import dataclass

from beam_calc.domain.beam import Beam
from beam_calc.domain.timber import k_def, k_mod

# Partial factors (EN 1990 / EN 1995-1-1)
GAMMA_M = 1.3
GAMMA_G = 1.35
GAMMA_Q = 1.5


@dataclass(frozen=True)
class UlsBendingResult:
    q_d_kN_per_m: float
    M_d_kNm: float
    V_d_kN: float
    sigma_m_d: float  # N/mm2
    f_m_d: float  # N/mm2
    ratio: float

    @property
    def passes(self) -> bool:
        return self.ratio <= 1.0


@dataclass(frozen=True)
class SlsDeflectionResult:
    w_inst_mm: float
    w_fin_mm: float
    w_lim_inst_mm: float
    w_lim_fin_mm: float

    @property
    def passes(self) -> bool:
        return self.w_inst_mm <= self.w_lim_inst_mm and self.w_fin_mm <= self.w_lim_fin_mm


def uls_bending(beam: Beam) -> UlsBendingResult:
    q_d = GAMMA_G * beam.loads.g_k + GAMMA_Q * beam.loads.q_k  # kN/m
    L = beam.span_m
    M_d = q_d * L * L / 8.0  # kNm
    V_d = q_d * L / 2.0  # kN

    W = beam.section.section_modulus()  # mm^3
    sigma_m_d = M_d * 1e6 / W  # N/mm2

    kmod = k_mod(beam.service_class, beam.duration)
    f_m_d = kmod * beam.timber.f_m_k / GAMMA_M

    return UlsBendingResult(
        q_d_kN_per_m=q_d,
        M_d_kNm=M_d,
        V_d_kN=V_d,
        sigma_m_d=sigma_m_d,
        f_m_d=f_m_d,
        ratio=sigma_m_d / f_m_d,
    )


def sls_deflection(beam: Beam) -> SlsDeflectionResult:
    q_sls = beam.loads.g_k + beam.loads.q_k  # kN/m == N/mm
    L_mm = beam.span_m * 1000.0
    E = beam.timber.E_0_mean
    I = beam.section.second_moment()

    w_inst = 5.0 * q_sls * L_mm**4 / (384.0 * E * I)
    w_fin = w_inst * (1.0 + k_def(beam.service_class))

    return SlsDeflectionResult(
        w_inst_mm=w_inst,
        w_fin_mm=w_fin,
        w_lim_inst_mm=L_mm / 300.0,
        w_lim_fin_mm=L_mm / 250.0,
    )


@dataclass(frozen=True)
class DiagramSamples:
    x_m: list[float]
    M_kNm: list[float]
    V_kN: list[float]
    w_mm: list[float]


def diagrams(beam: Beam, n: int = 40) -> DiagramSamples:
    q_d = GAMMA_G * beam.loads.g_k + GAMMA_Q * beam.loads.q_k
    q_sls = beam.loads.g_k + beam.loads.q_k
    L = beam.span_m
    L_mm = L * 1000.0
    EI = beam.timber.E_0_mean * beam.section.second_moment()

    xs = [i * L / n for i in range(n + 1)]
    M = [q_d * x * (L - x) / 2.0 for x in xs]
    V = [q_d * (L / 2.0 - x) for x in xs]
    w = []
    for x in xs:
        xmm = x * 1000.0
        w.append(q_sls * xmm * (L_mm**3 - 2 * L_mm * xmm**2 + xmm**3) / (24.0 * EI))
    return DiagramSamples(x_m=xs, M_kNm=M, V_kN=V, w_mm=w)
