from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

n = input("Enter folder number: ")
folder = DATA_DIR / f"D{n}"

df = pd.read_parquet(folder / f"{n}-before.parquet")
rules = pd.read_csv(folder / "smartrules.csv")

# Flatten all cell values to a set of lowercase strings for easy lookup
cells = set(str(v).strip().lower() for v in df.values.flatten())

for _, rule in rules.iterrows():
    o1 = str(rule["o1"]).strip().lower()
    o2 = str(rule["o2"]).strip().lower()
    prop = str(rule["property-or-threshold"]).strip().lower()
    value = str(rule["value"]).strip().lower()
    rule_type = str(rule["type"]).strip().lower()
    message = rule["message"]

    # Check if o1, o2, and property appear anywhere in the grid (partial match either way)
    o1_found = any(o1 in cell or cell in o1 for cell in cells)
    o2_found = any(o2 in cell or cell in o2 for cell in cells)
    prop_found = any(prop in cell or cell in prop for cell in cells)
    value_found = value in cells

    if rule_type == "predict":
        # Trigger when objects and property are found but value not yet reached
        if o1_found and o2_found and prop_found and not value_found:
            print(f"[predict] {message}")
    elif rule_type == "measurement":
        # Trigger when objects, property, and value are all found
        if o1_found and o2_found and prop_found and value_found:
            print(f"[measurement] {message}")
