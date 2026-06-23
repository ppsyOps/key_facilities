# psse-utils

A collection of small PSS/E utility scripts built on
[`psse-model-util`](https://pypi.org/project/psse-model-util/). Instead of a new
repo + PyPI project per script, scripts live here and ship as one package.

## Installation

~~~
pip install --pre psse-utils
~~~

`--pre` is required while this package (and `psse-model-util`) are pre-releases.

## Scripts

### `flowgate-key-facilities`

Identify the **key facilities** for a set of PSS/E flowgates — the equipment
whose outage would most likely have a high impact on those flowgates. For each
flowgate in a `.mon` file, it keeps AC lines in a kV range and generators above a
PMax, all within `n` buses (hops) of the flowgate's elements, and writes the
results to CSVs.

~~~
flowgate-key-facilities \
  --mon flowgates.mon --raw Model.raw \
  --areas 1 2 3 --sc SCA --out-dir outputs/
~~~

Full options: `flowgate-key-facilities --help`. Outputs `branches.csv`,
`generators.csv`, `transformers_3w.csv`, `unresolved.csv` in `--out-dir`.

## Adding a script

1. Create `src/psse_utils/<name>.py` with the **logic as importable functions**
   plus a thin `main(argv=None) -> int` that parses args and calls them (keeping
   logic separate from the CLI leaves room for a future TUI/web UI).
2. Add a console command in `pyproject.toml`:
   `[project.scripts]` → `your-command = "psse_utils.<name>:main"`.
3. Add tests `tests/test_<name>_*.py` (script-prefixed).
4. Put any heavy/extra dependencies behind an extra in `[project.optional-dependencies]`.

## Development

~~~
python -m venv .venv
.venv\Scripts\python -m pip install --pre -e .
.venv\Scripts\python -m pip install pytest pytest-cov
.venv\Scripts\python -m pytest
~~~

Versioning is CalVer (`YYYY.M.micro`) from `src/psse_utils/__about__.py`.
Releases publish to PyPI via Trusted Publishing — see the team setup runbook and
`psse-model-util`'s `docs/PUBLISHING.md`.
