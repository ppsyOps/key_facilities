"""End-to-end tests for flowgate_key_facilities.main().

main() runs the full pipeline in-process (parse .mon -> filter by SC ->
load + area-filter the model -> resolve seeds -> collect neighborhood ->
write four CSVs) and returns an exit code. These tests drive it with the
Model_1 / synthetic_flowgates fixtures.
"""
from __future__ import annotations

import pandas as pd
import pytest
from psse_model_util.common.dirs import clear_cache

from flowgate_key_facilities import main

OUTPUT_CSVS = ["branches.csv", "generators.csv", "transformers_3w.csv", "unresolved.csv"]


@pytest.fixture(scope="module", autouse=True)
def _clean_cache():
    """Parse the .raw fresh so a stale pickle from interactive use can't leak
    duplicate/enriched columns into the run."""
    clear_cache()


def _run(mon_file, raw_file, out_dir, *, sc="SCA", areas=("1", "2", "3"), extra=()):
    argv = [
        "--mon", str(mon_file),
        "--raw", str(raw_file),
        "--areas", *areas,
        "--out-dir", str(out_dir),
        "--sc", sc,
        *extra,
    ]
    return main(argv)


def test_main_happy_path_writes_four_csvs(mon_file, raw_file, tmp_path):
    rc = _run(mon_file, raw_file, tmp_path)
    assert rc == 0
    for name in OUTPUT_CSVS:
        path = tmp_path / name
        assert path.exists(), f"missing {name}"
        # Every output must be a readable CSV (header at minimum).
        pd.read_csv(path)


def test_main_creates_missing_nested_out_dir(mon_file, raw_file, tmp_path):
    nested = tmp_path / "a" / "b" / "out"
    assert not nested.exists()
    rc = _run(mon_file, raw_file, nested)
    assert rc == 0
    assert nested.is_dir()
    assert (nested / "branches.csv").exists()


def test_main_prints_summary(mon_file, raw_file, tmp_path, capsys):
    _run(mon_file, raw_file, tmp_path)
    out = capsys.readouterr().out
    assert "Wrote" in out
    assert str(tmp_path) in out
    for name in OUTPUT_CSVS:
        assert name in out


def test_out_of_scope_areas_leave_everything_unresolved(mon_file, raw_file, tmp_path):
    """With an area set containing no equipment, every SCA seed should be
    unresolvable and the equipment CSVs should be empty (header-only)."""
    rc = _run(mon_file, raw_file, tmp_path, areas=("9999",))
    assert rc == 0
    assert len(pd.read_csv(tmp_path / "branches.csv")) == 0
    assert len(pd.read_csv(tmp_path / "generators.csv")) == 0
    assert len(pd.read_csv(tmp_path / "transformers_3w.csv")) == 0
    assert len(pd.read_csv(tmp_path / "unresolved.csv")) > 0


def test_sc_filter_selects_only_matching_flowgates(mon_file, raw_file, tmp_path):
    """SCB matches a single flowgate; SCA matches three. A SC code that
    matches nothing yields an empty unresolved set (no seeds to resolve)."""
    out_none = tmp_path / "none"
    rc = _run(mon_file, raw_file, out_none, sc="NO_SUCH_SC")
    assert rc == 0
    # No flowgates selected -> nothing to resolve, nothing collected.
    assert len(pd.read_csv(out_none / "unresolved.csv")) == 0
    assert len(pd.read_csv(out_none / "branches.csv")) == 0
