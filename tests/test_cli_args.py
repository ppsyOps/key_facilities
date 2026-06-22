"""Unit tests for key_facilities._parse_args (the CLI contract).

These are fast and fixture-free: they assert which arguments are required,
that the optional overrides default to the flowgate package constants, and
that types/nargs are parsed as documented.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from psse_model_util.flowgate import (
    DEFAULT_GEN_MIN_MW,
    DEFAULT_HOPS,
    DEFAULT_KV_MAX,
    DEFAULT_KV_MIN,
)

from key_facilities import _parse_args

# A minimal complete set of the five required arguments.
REQUIRED = [
    "--mon", "fg.mon",
    "--raw", "model.raw",
    "--areas", "1",
    "--out-dir", "out",
    "--sc", "SCA",
]


def test_required_args_parse_into_expected_types():
    ns = _parse_args(REQUIRED)
    assert ns.mon == Path("fg.mon")
    assert ns.raw == Path("model.raw")
    assert ns.out_dir == Path("out")
    assert ns.areas == [1]
    assert ns.sc == "SCA"
    # --areas elements are coerced to int, not left as str.
    assert all(isinstance(a, int) for a in ns.areas)


def test_optional_overrides_default_to_flowgate_constants():
    """Unset optional knobs must fall back to the flowgate package defaults,
    so the CLI and library stay in lockstep."""
    ns = _parse_args(REQUIRED)
    assert ns.hops == DEFAULT_HOPS
    assert ns.kv_min == DEFAULT_KV_MIN
    assert ns.kv_max == DEFAULT_KV_MAX
    assert ns.gen_min_mw == DEFAULT_GEN_MIN_MW
    assert ns.verbose is False


def test_areas_accepts_multiple_ints():
    ns = _parse_args(
        ["--mon", "m", "--raw", "r", "--out-dir", "o", "--sc", "X",
         "--areas", "1", "2", "3"]
    )
    assert ns.areas == [1, 2, 3]


def test_optional_overrides_parse_with_correct_types():
    ns = _parse_args(
        REQUIRED + ["--hops", "5", "--kv-min", "160", "--kv-max", "765",
                    "--gen-min-mw", "20", "--verbose"]
    )
    assert ns.hops == 5 and isinstance(ns.hops, int)
    assert ns.kv_min == 160.0 and isinstance(ns.kv_min, float)
    assert ns.kv_max == 765.0 and isinstance(ns.kv_max, float)
    assert ns.gen_min_mw == 20.0 and isinstance(ns.gen_min_mw, float)
    assert ns.verbose is True


def test_verbose_short_flag():
    ns = _parse_args(REQUIRED + ["-v"])
    assert ns.verbose is True


@pytest.mark.parametrize(
    "drop",
    ["--mon", "--raw", "--areas", "--out-dir", "--sc"],
)
def test_each_required_arg_is_enforced(drop):
    """Removing any one required flag (and its value) must abort with
    SystemExit from argparse."""
    argv = []
    skip = False
    for tok in REQUIRED:
        if tok == drop:
            skip = True  # also skip this flag's value
            continue
        if skip:
            skip = False
            continue
        argv.append(tok)
    with pytest.raises(SystemExit):
        _parse_args(argv)


def test_non_integer_area_is_rejected():
    argv = ["--mon", "m", "--raw", "r", "--out-dir", "o", "--sc", "X",
            "--areas", "not_an_int"]
    with pytest.raises(SystemExit):
        _parse_args(argv)
