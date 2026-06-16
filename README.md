# key-facilities

Standalone CLI for extracting "key facilities" near PSS/E flowgate elements.

Imports `psse_model_util.flowgate` to do the heavy lifting; this repo is just a
thin orchestrator that writes the four output DataFrames as CSVs.

## Usage

~~~
python key_facilities.py \
  --mon path/to/flowgates.mon \
  --raw path/to/Model.raw \
  --areas 1 2 3 \
  --out-dir outputs/
~~~

Required arguments:

- `--mon` - PSS/E `.mon` flowgate-definition file.
- `--raw` - PSS/E `.raw` model file.
- `--areas` - one or more area IDs (integers) restricting the search
  domain. The model is filtered to keep only equipment touching these
  areas before resolution. Seeds whose buses fall outside the listed
  areas appear in `unresolved.csv` with reason `bus_not_found`.
- `--out-dir` - output directory for the CSVs (created if missing).

Optional overrides: `--hops 4`, `--kv-min 160`, `--kv-max 765`,
`--gen-min-mw 15`, `--sc PJM`.

## Output

Four CSV files in `--out-dir`:

- `branches.csv` - AC lines and 2W transformers within `--hops` buses of any
  flowgate seed, filtered to `--kv-min <= kV <= --kv-max` (either end).
- `generators.csv` - generators within the neighborhood with `PT >= --gen-min-mw`.
- `transformers_3w.csv` - 3W transformers with any winding in the neighborhood
  and any winding bus in the kV range.
- `unresolved.csv` - `.mon` elements that could not be resolved against the
  model (bus name not found, branch not found, generator not found).

## Installation

This repo depends on `psse_model_util`, which is developed as a sibling repo.
For development, either install it editably:

~~~
pip install -e ../psse_model_util
~~~

or set `PYTHONPATH` to the parent of the `psse_model_util` project dir (the
grandparent of this repo) so Python can import the package via the flat
layout:

~~~
PYTHONPATH=.. python key_facilities.py ...
~~~
