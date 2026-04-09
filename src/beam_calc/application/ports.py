"""Ports — protocols defining outbound dependencies of the application layer."""

from __future__ import annotations

from typing import Protocol

from beam_calc.domain.timber import TimberProperties


class TimberPropertyPort(Protocol):
    """Source of characteristic timber properties by strength class name."""

    def get(self, class_name: str) -> TimberProperties: ...

    def list_classes(self) -> list[str]: ...
