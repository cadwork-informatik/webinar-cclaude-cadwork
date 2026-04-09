"""DTOs for the web adapter — the only place pydantic is allowed."""

from __future__ import annotations

from pydantic import BaseModel, Field

from beam_calc.application.beam_service import DesignRequest
from beam_calc.domain.timber import LoadDuration, ServiceClass


class DesignFormDto(BaseModel):
    name: str = ""
    span_m: float = Field(gt=0)
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    g_k: float = Field(ge=0)
    q_k: float = Field(ge=0)
    timber_class: str
    service_class: ServiceClass
    duration: LoadDuration

    def to_request(self) -> DesignRequest:
        return DesignRequest(
            name=self.name,
            span_m=self.span_m,
            width_mm=self.width_mm,
            height_mm=self.height_mm,
            g_k=self.g_k,
            q_k=self.q_k,
            timber_class=self.timber_class,
            service_class=self.service_class,
            duration=self.duration,
        )
