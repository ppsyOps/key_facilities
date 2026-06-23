# flowgate-key-facilities

Identify the **key facilities** for a set of PSS/E flowgates — the equipment
whose loss (damage or outage) would most likely have a high impact on those
flowgates.

Given a flowgate-definition file (`.mon`) and a PSS/E model (`.raw`), this tool
finds, for each flowgate, the nearby high-impact equipment and writes it to CSVs.

## What it does

A flowgate (defined in the `.mon` file) is a set of monitored/contingency
elements. Equipment electrically *close* to those elements is the most likely to
matter if it goes out. "Key facilities" are selected with a deliberately simple,
transparent rule — for each flowgate in the `.mon` file:

1. Resolve the flowgate's elements to buses in the `.raw` model.
2. Take the **electrical neighborhood**: every bus within **`n` buses (hops)** of
   those elements (`--hops`, default 4).
3. From that neighborhood, keep the high-impact facilities:
   - **AC lines / 2-winding transformers** whose voltage is in a **kV range**
     (`--kv-min` / `--kv-max`, default 160–765 kV).
   - **Generators** with **PMax ≥ a threshold** (`--gen-min-mw`, default 15 MW).
   - **3-winding transformers** touching the neighborhood within the kV range.

It is *not* a contingency analysis or a flow-impact calculation — it's a fast,
proximity-based screen to surface candidate key facilities for further study.

## Installation

~~~
pip install --pre flowgate-key-facilities
~~~

This pulls in `psse-model-util` (the engine) from PyPI automatically. `--pre` is
required while both packages are pre-releases.

## Usage

~~~
flowgate-key-facilities \
  --mon path/to/flowgates.mon \
  --raw path/to/Model.raw \
  --areas 1 2 3 \
  --sc SCA \
  --out-dir outputs/
~~~

Required arguments:

- `--mon` — PSS/E `.mon` flowgate-definition file.
- `--raw` — PSS/E `.raw` model file.
- `--areas` — one or more area IDs (integers) restricting the search domain. The
  model is filtered to keep only equipment touching these areas before
  resolution. Seeds whose buses fall outside the listed areas appear in
  `unresolved.csv` with reason `bus_not_found`.
- `--sc` — security-coordinator code; only flowgates with this SC are processed.
- `--out-dir` — output directory for the CSVs (created if missing).

Selection overrides (the "key facility" thresholds):

- `--hops` — neighborhood radius in buses (default 4).
- `--kv-min` / `--kv-max` — line/transformer voltage range to keep (default 160 / 765).
- `--gen-min-mw` — minimum generator PMax to keep (default 15).
- `-v` / `--verbose` — debug logging.

## Output

Four CSV files in `--out-dir`:

- `branches.csv` — AC lines and 2W transformers within `--hops` buses of any
  flowgate element, filtered to `--kv-min <= kV <= --kv-max` (either end).
- `generators.csv` — generators in the neighborhood with `PMax >= --gen-min-mw`.
- `transformers_3w.csv` — 3W transformers with any winding in the neighborhood
  and any winding bus in the kV range.
- `unresolved.csv` — `.mon` elements that could not be resolved against the model
  (bus name not found, branch not found, generator not found).

## Development

~~~
pip install -e ../psse_model_util   # sibling repo, editable
pip install -e .
pytest
~~~
