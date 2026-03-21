import json
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

n = input("Enter folder number: ")
json_path = input("Enter path to JSON file: ")

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

grid = data["grid"]
rows = [f"r{i+1}" for i in range(len(grid))]
cols = [f"c{j+1}" for j in range(len(grid[0]))]

df = pd.DataFrame(grid, index=rows, columns=cols)

out_path = DATA_DIR / f"D{n}" / f"{n}-before.parquet"
df.to_parquet(out_path, index=True)

print(f"Saved to {out_path}")
print(df)
