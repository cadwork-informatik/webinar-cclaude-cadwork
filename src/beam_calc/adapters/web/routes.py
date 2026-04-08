"""HTTP routes for the beam designer."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from beam_calc.adapters.web.schemas import DesignFormDto
from beam_calc.application.beam_service import BeamDesignService, DesignReport
from beam_calc.domain.timber import LoadDuration, ServiceClass

_TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


def build_router(service: BeamDesignService) -> APIRouter:
    router = APIRouter()

    def _render(request: Request, report: DesignReport | None) -> HTMLResponse:
        context: dict[str, object] = {
            "classes": service.available_classes(),
            "report": report,
        }
        if report is not None:
            context["chart_json"] = json.dumps(
                {
                    "xs": report.diagrams.x_m,
                    "M": report.diagrams.M_kNm,
                    "V": report.diagrams.V_kN,
                    "w": report.diagrams.w_mm,
                }
            )
        return templates.TemplateResponse(request, "index.html", context)

    @router.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return _render(request, None)

    @router.post("/", response_class=HTMLResponse)
    def submit(
        request: Request,
        span_m: float = Form(5.0),
        width_mm: float = Form(120),
        height_mm: float = Form(240),
        g_k: float = Form(2.0),
        q_k: float = Form(3.0),
        timber_class: str = Form("C24"),
        service_class: ServiceClass = Form(ServiceClass.SC1),
        duration: LoadDuration = Form(LoadDuration.MEDIUM),
    ) -> HTMLResponse:
        dto = DesignFormDto(
            span_m=span_m,
            width_mm=width_mm,
            height_mm=height_mm,
            g_k=g_k,
            q_k=q_k,
            timber_class=timber_class,
            service_class=service_class,
            duration=duration,
        )
        report = service.design(dto.to_request())
        return _render(request, report)

    return router
