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
