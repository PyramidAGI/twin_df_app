# Twin DataFrame Parquet App

This project creates a folder structure for coupled 10x10 pandas DataFrames.

## Structure

For each dataset index `N` from 1 to 10:

- Folder: `D<N>`
- Parquet files:
  - `<N>-before.parquet`
  - `<N>-after.parquet`
- Meta file:
  - `M<N>.json`

Example:

- `D10/10-before.parquet`
- `D10/10-after.parquet`
- `D10/M10.json`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Run

```bash
python app/main.py
```

This will create the folders and seed each one with two 10x10 DataFrames and one metadata file.

## Smart Rules

```bash
python app/smartrules.py
```

Asks for a folder number, then reads `smartrules.csv` from that folder and inspects `<N>-before.parquet` to trigger messages.

Each row in `smartrules.csv` defines a rule with these columns:

| Column | Description |
|---|---|
| `type` | `predict` or `measurement` |
| `o1` | First object to find in the grid |
| `o2` | Second object to find in the grid |
| `property-or-threshold` | Property name to find in the grid |
| `value` | Value to look for in the grid |
| `message` | Message to print when the rule triggers |

**predict** — triggers when `o1`, `o2`, and `property` are found in the grid but `value` is not yet present (a forward-looking warning).

**measurement** — triggers when `o1`, `o2`, `property`, and `value` are all found in the grid (a confirmed observation).

## Path Walk

```bash
python app/pathwalk.py
```

Asks for a folder number, then walks a path through the grid from the left anchor concept (`o1`) to the right anchor concept (`o2`) as defined in `smartrules.csv`. Concept names vary per folder and are resolved dynamically.

**Algorithm: column-by-column linear interpolation**

1. Locate `o1` and `o2` in the grid; the one with the smaller column index becomes the start (left), the other the end (right).
2. Step column by column from start to end, interpolating the row linearly at each step.
3. At each column, collect all cells within ±2 rows of the interpolated row.
4. Put all values from this corridor into a set.
5. Match the set against `smartrules.csv` and print triggered messages.

This ensures that concepts and properties lying along the diagonal between the two anchors are captured and evaluated, even when the path is not horizontal.
