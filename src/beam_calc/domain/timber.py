"""Timber domain enums and value objects (EN 338 / EN 1995-1-1)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ServiceClass(int, Enum):
    SC1 = 1
    SC2 = 2
    SC3 = 3


class LoadDuration(str, Enum):
    PERMANENT = "permanent"
    LONG = "long"
    MEDIUM = "medium"
    SHORT = "short"
    INSTANTANEOUS = "instantaneous"


@dataclass(frozen=True)
class TimberProperties:
    """Characteristic values from EN 338 for a strength class."""

    name: str
    f_m_k: float  # bending strength [N/mm2]
    E_0_mean: float  # mean modulus of elasticity parallel [N/mm2]


# EN 1995-1-1 Table 3.1 — k_mod for solid timber, service classes 1 & 2
_KMOD_SC12: dict[LoadDuration, float] = {
    LoadDuration.PERMANENT: 0.60,
    LoadDuration.LONG: 0.70,
    LoadDuration.MEDIUM: 0.80,
    LoadDuration.SHORT: 0.90,
    LoadDuration.INSTANTANEOUS: 1.10,
}
_KMOD_SC3: dict[LoadDuration, float] = {
    LoadDuration.PERMANENT: 0.50,
    LoadDuration.LONG: 0.55,
    LoadDuration.MEDIUM: 0.65,
    LoadDuration.SHORT: 0.70,
    LoadDuration.INSTANTANEOUS: 0.90,
}

# EN 1995-1-1 Table 3.2 — k_def for solid timber
_KDEF: dict[ServiceClass, float] = {
    ServiceClass.SC1: 0.60,
    ServiceClass.SC2: 0.80,
    ServiceClass.SC3: 2.00,
}


def k_mod(service_class: ServiceClass, duration: LoadDuration) -> float:
    table = _KMOD_SC3 if service_class is ServiceClass.SC3 else _KMOD_SC12
    return table[duration]


def k_def(service_class: ServiceClass) -> float:
    return _KDEF[service_class]
