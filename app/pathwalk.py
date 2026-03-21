"""
pathwalk.py

Algorithm: column-by-column linear interpolation
-------------------------------------------------
1. Read smartrules.csv to find the two anchor concepts (o1, o2).
2. Locate both concepts in the grid; the one with the smaller column
   index is the start (left), the other is the end (right).
3. Walk column by column from start to end, interpolating the row
   linearly at each step (Bresenham-style).
4. For every column on the path, include all cells within ±2 rows.
5. Collect all cell values in that corridor into a set.
6. Apply smartrules against the set and print triggered messages.
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

n = input("Enter folder number: ")
folder = DATA_DIR / f"D{n}"

df = pd.read_parquet(folder / f"{n}-before.parquet")
rules = pd.read_csv(folder / "smartrules.csv")

rows = df.index.tolist()
cols = df.columns.tolist()
n_rows = len(rows)
n_cols = len(cols)


def find_concept(concept):
    """Return (row_idx, col_idx) of the first cell that partially matches concept."""
    concept_lc = concept.strip().lower()
    for ri, row in enumerate(rows):
        for ci, col in enumerate(cols):
            cell = str(df.at[row, col]).strip().lower()
            if concept_lc in cell or cell in concept_lc:
                return ri, ci
    return None


# Collect unique anchor pairs from rules
anchor_pairs = rules[["o1", "o2"]].drop_duplicates().values.tolist()

all_triggered = []

for o1_name, o2_name in anchor_pairs:
    pos1 = find_concept(o1_name)
    pos2 = find_concept(o2_name)

    if pos1 is None or pos2 is None:
        print(f"Could not find '{o1_name}' or '{o2_name}' in the grid.")
        continue

    # Ensure start is the left concept (smaller column index)
    if pos1[1] <= pos2[1]:
        start, end = pos1, pos2
    else:
        start, end = pos2, pos1

    r_start, c_start = start
    r_end, c_end = end
    col_span = c_end - c_start  # guaranteed >= 0

    print(f"\nPath from '{o1_name}' {start} to '{o2_name}' {end}:")

    # Build the corridor set
    corridor = set()
    path_cells = []

    for step in range(col_span + 1):
        ci = c_start + step
        # Linearly interpolate the row
        t = step / col_span if col_span > 0 else 0
        ri_center = round(r_start + t * (r_end - r_start))

        ri_min = max(0, ri_center - 2)
        ri_max = min(n_rows - 1, ri_center + 2)

        for ri in range(ri_min, ri_max + 1):
            cell_val = str(df.iat[ri, ci]).strip()
            corridor.add(cell_val)
            path_cells.append((rows[ri], cols[ci], cell_val))

    print("Corridor cells:", sorted(corridor))

    # Match smartrules against the corridor
    corridor_lc = {v.lower() for v in corridor}

    for _, rule in rules.iterrows():
        o1 = str(rule["o1"]).strip().lower()
        o2 = str(rule["o2"]).strip().lower()
        prop = str(rule["property-or-threshold"]).strip().lower()
        value = str(rule["value"]).strip().lower()
        rule_type = str(rule["type"]).strip().lower()
        message = rule["message"]

        o1_found = any(o1 in c or c in o1 for c in corridor_lc)
        o2_found = any(o2 in c or c in o2 for c in corridor_lc)
        prop_found = any(prop in c or c in prop for c in corridor_lc)
        value_found = value in corridor_lc

        if rule_type == "predict" and o1_found and o2_found and prop_found and not value_found:
            all_triggered.append(f"[predict] {message}")
        elif rule_type == "measurement" and o1_found and o2_found and prop_found and value_found:
            all_triggered.append(f"[measurement] {message}")

print("\n--- Triggered messages ---")
for msg in all_triggered:
    print(msg)
