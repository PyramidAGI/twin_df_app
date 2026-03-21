import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

n = input("Enter folder number: ")
folder = DATA_DIR / f"D{n}"

src = folder / f"{n}-before.parquet"
dst = folder / f"{n}-after.parquet"

shutil.copy2(src, dst)
print(f"Copied {src.name} -> {dst.name}")
