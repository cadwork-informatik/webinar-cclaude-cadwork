from __future__ import annotations

import pytest

from beam_calc.adapters.timber_repository import InMemoryTimberRepository

pytestmark = pytest.mark.unit


def test_get_known_class_returns_properties() -> None:
    repo = InMemoryTimberRepository()
    c24 = repo.get("C24")
    assert c24.f_m_k == 24.0
    assert c24.E_0_mean == 11000.0


def test_get_unknown_class_raises() -> None:
    repo = InMemoryTimberRepository()
    with pytest.raises(ValueError, match="Unknown timber class"):
        repo.get("C99")


def test_list_classes_contains_c24() -> None:
    assert "C24" in InMemoryTimberRepository().list_classes()
