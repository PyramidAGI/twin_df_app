from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

n = input("Enter folder number: ")
folder = DATA_DIR / f"D{n}"

before = pd.read_parquet(folder / f"{n}-before.parquet")
after = pd.read_parquet(folder / f"{n}-after.parquet")

print("\n--- BEFORE ---")
print(before)
print("\n--- AFTER ---")
print(after)
