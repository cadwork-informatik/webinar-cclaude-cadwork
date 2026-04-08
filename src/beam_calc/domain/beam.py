"""Beam entity and load value objects."""
from __future__ import annotations

from dataclasses import dataclass

from beam_calc.domain.timber import LoadDuration, ServiceClass, TimberProperties


@dataclass(frozen=True)
class RectangularSection:
    """Rectangular cross-section in mm."""

    width_mm: float
    height_mm: float

    def section_modulus(self) -> float:
        return self.width_mm * self.height_mm**2 / 6.0  # mm^3

    def second_moment(self) -> float:
        return self.width_mm * self.height_mm**3 / 12.0  # mm^4


@dataclass(frozen=True)
class UniformLoads:
    """Characteristic uniformly distributed loads [kN/m]."""

    g_k: float  # permanent
    q_k: float  # variable


@dataclass(frozen=True)
class Beam:
    """Simply-supported timber beam with uniform load."""

    span_m: float
    section: RectangularSection
    timber: TimberProperties
    loads: UniformLoads
    service_class: ServiceClass
    duration: LoadDuration
