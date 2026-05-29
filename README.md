# key-facilities

Standalone CLI for extracting "key facilities" near PSS/E flowgate elements.

Imports `psse_model_util.flowgate` to do the heavy lifting; this repo is just a
thin orchestrator that writes the four output DataFrames as CSVs.

## Usage

~~~
python key_facilities.py \
  --mon path/to/flowgates.mon \
  --raw path/to/Model.raw \
  --out-dir outputs/
~~~

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

or set `PYTHONPATH` to point at the sibling project root when invoking the CLI:

~~~
PYTHONPATH=../psse_model_util python key_facilities.py ...
~~~
