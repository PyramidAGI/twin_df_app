from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
GRID_SIZE = 10
DATASET_COUNT = 10


@dataclass
class TwinMeta:
    dataset_id: int
    folder_name: str
    before_file: str
    after_file: str
    grid_rows: int
    grid_cols: int
    created_utc: str
    description: str


def make_grid_dataframe(dataset_id: int, state: str, rows: int = GRID_SIZE, cols: int = GRID_SIZE) -> pd.DataFrame:
    """Create a 10x10 grid DataFrame with simple seeded cell values."""
    data = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(f"D{dataset_id}-{state}-r{r + 1}c{c + 1}")
        data.append(row)

    index = [f"r{r + 1}" for r in range(rows)]
    columns = [f"c{c + 1}" for c in range(cols)]
    return pd.DataFrame(data, index=index, columns=columns)


def write_dataset(dataset_id: int) -> None:
    folder = DATA_DIR / f"D{dataset_id}"
    folder.mkdir(parents=True, exist_ok=True)

    before_name = f"{dataset_id}-before.parquet"
    after_name = f"{dataset_id}-after.parquet"
    meta_name = f"M{dataset_id}.json"

    before_df = make_grid_dataframe(dataset_id, "before")
    after_df = make_grid_dataframe(dataset_id, "after")

    before_path = folder / before_name
    after_path = folder / after_name
    meta_path = folder / meta_name

    before_df.to_parquet(before_path, index=True)
    after_df.to_parquet(after_path, index=True)

    meta = TwinMeta(
        dataset_id=dataset_id,
        folder_name=folder.name,
        before_file=before_name,
        after_file=after_name,
        grid_rows=GRID_SIZE,
        grid_cols=GRID_SIZE,
        created_utc=datetime.now(timezone.utc).isoformat(),
        description="Twin 10x10 grid DataFrames stored as Parquet.",
    )

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(meta), f, indent=2)


def setup_all_datasets() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for dataset_id in range(1, DATASET_COUNT + 1):
        write_dataset(dataset_id)


if __name__ == "__main__":
    setup_all_datasets()
    print(f"Created datasets in: {DATA_DIR}")
