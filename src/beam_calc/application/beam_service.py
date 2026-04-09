"""BeamDesignService — application-layer orchestration of EC5 checks."""

from __future__ import annotations

from dataclasses import dataclass

from beam_calc.application.ports import TimberPropertyPort
from beam_calc.domain.beam import Beam, RectangularSection, UniformLoads
from beam_calc.domain.checks import (
    DiagramSamples,
    SlsDeflectionResult,
    UlsBendingResult,
    diagrams,
    sls_deflection,
    uls_bending,
)
from beam_calc.domain.timber import LoadDuration, ServiceClass


@dataclass(frozen=True)
class DesignRequest:
    name: str
    span_m: float
    width_mm: float
    height_mm: float
    g_k: float
    q_k: float
    timber_class: str
    service_class: ServiceClass
    duration: LoadDuration


@dataclass(frozen=True)
class DesignReport:
    beam: Beam
    uls: UlsBendingResult
    sls: SlsDeflectionResult
    diagrams: DiagramSamples

    @property
    def passes(self) -> bool:
        return self.uls.passes and self.sls.passes


class BeamDesignService:
    def __init__(self, timber_repo: TimberPropertyPort) -> None:
        self._timber_repo = timber_repo

    def design(self, req: DesignRequest) -> DesignReport:
        timber = self._timber_repo.get(req.timber_class)
        beam = Beam(
            name=req.name,
            span_m=req.span_m,
            section=RectangularSection(width_mm=req.width_mm, height_mm=req.height_mm),
            timber=timber,
            loads=UniformLoads(g_k=req.g_k, q_k=req.q_k),
            service_class=req.service_class,
            duration=req.duration,
        )
        return DesignReport(
            beam=beam,
            uls=uls_bending(beam),
            sls=sls_deflection(beam),
            diagrams=diagrams(beam),
        )

    def available_classes(self) -> list[str]:
        return self._timber_repo.list_classes()
