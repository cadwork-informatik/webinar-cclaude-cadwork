"""In-memory EN 338 timber property repository."""
from __future__ import annotations

from beam_calc.domain.timber import TimberProperties

# EN 338 characteristic values for a subset of softwood classes
_CLASSES: dict[str, TimberProperties] = {
    "C14": TimberProperties("C14", f_m_k=14.0, E_0_mean=7000.0),
    "C16": TimberProperties("C16", f_m_k=16.0, E_0_mean=8000.0),
    "C18": TimberProperties("C18", f_m_k=18.0, E_0_mean=9000.0),
    "C20": TimberProperties("C20", f_m_k=20.0, E_0_mean=9500.0),
    "C22": TimberProperties("C22", f_m_k=22.0, E_0_mean=10000.0),
    "C24": TimberProperties("C24", f_m_k=24.0, E_0_mean=11000.0),
    "C27": TimberProperties("C27", f_m_k=27.0, E_0_mean=11500.0),
    "C30": TimberProperties("C30", f_m_k=30.0, E_0_mean=12000.0),
}


class InMemoryTimberRepository:
    """Implements TimberPropertyPort from a static EN 338 lookup."""

    def get(self, class_name: str) -> TimberProperties:
        try:
            return _CLASSES[class_name]
        except KeyError as exc:
            raise ValueError(f"Unknown timber class: {class_name}") from exc

    def list_classes(self) -> list[str]:
        return list(_CLASSES.keys())
