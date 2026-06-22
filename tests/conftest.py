"""Shared fixtures for the key_facilities CLI tests.

Fixtures live in tests/data/ and are copies of the psse_model_util test
fixtures (Model_1.raw, synthetic_flowgates.mon). The .mon defines four
flowgates: three under security coordinator ``SCA`` and one under ``SCB``.
Model_1.raw spans PSS/E areas 1-5.
"""
from __future__ import annotations

from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent / "data"


@pytest.fixture(scope="session")
def mon_file() -> Path:
    return DATA_DIR / "synthetic_flowgates.mon"


@pytest.fixture(scope="session")
def raw_file() -> Path:
    return DATA_DIR / "Model_1.raw"
