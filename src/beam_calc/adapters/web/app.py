"""FastAPI application factory with dependency wiring."""
from __future__ import annotations

from fastapi import FastAPI

from beam_calc.adapters.timber_repository import InMemoryTimberRepository
from beam_calc.adapters.web.routes import build_router
from beam_calc.application.beam_service import BeamDesignService


def create_app() -> FastAPI:
    app = FastAPI(title="EC5 Timber Beam Designer")
    service = BeamDesignService(timber_repo=InMemoryTimberRepository())
    app.include_router(build_router(service))
    return app
