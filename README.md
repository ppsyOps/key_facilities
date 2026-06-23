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
  --sc SCA \
  --out-dir outputs/
~~~

Required arguments:

- `--mon` - PSS/E `.mon` flowgate-definition file.
- `--raw` - PSS/E `.raw` model file.
- `--areas` - one or more area IDs (integers) restricting the search
  domain. The model is filtered to keep only equipment touching these
  areas before resolution. Seeds whose buses fall outside the listed
  areas appear in `unresolved.csv` with reason `bus_not_found`.
- `--sc` - security-coordinator code; only flowgates with this SC are
  processed.
- `--out-dir` - output directory for the CSVs (created if missing).

Optional overrides: `--hops 4`, `--kv-min 160`, `--kv-max 765`,
`--gen-min-mw 15`, `-v`/`--verbose`.

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

~~~
pip install --pre key-facilities
~~~

This pulls in `psse-model-util` from PyPI automatically. `--pre` is required
while both packages are pre-releases. After install, use the console script:

~~~
key-facilities --mon path/to/flowgates.mon --raw path/to/Model.raw \
  --areas 1 2 3 --sc SCA --out-dir outputs/
~~~

### Development

~~~
pip install -e ../psse_model_util   # sibling repo, editable
pip install -e .
~~~
