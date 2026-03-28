"""
insert_item.py — Ask for a folder number, row number, column number, and a string,
then replace the cell content and display the updated dataframe.
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
VALID_FOLDERS = [f"D{i}" for i in range(1, 11)]


def load_df(folder_num: str) -> tuple[pd.DataFrame, str]:
    folder = f"D{folder_num}"
    path = os.path.join(DATA_DIR, folder, f"{folder_num}-before.parquet")
    df = pd.read_parquet(path)
    return df, path


def main():
    # --- folder selection ---
    print(f"Available folders: {', '.join(VALID_FOLDERS)}")
    folder_num = input("Enter folder number (1-10): ").strip()
    if f"D{folder_num}" not in VALID_FOLDERS:
        print(f"Invalid folder number '{folder_num}'. Must be 1-10.")
        return

    df, path = load_df(folder_num)
    print(f"\nCurrent dataframe (D{folder_num}):")
    print(df.to_string())

    # --- row selection ---
    print(f"\nRows: {list(df.index)}")
    row_num = input("Enter row number: ").strip()
    row_label = f"r{row_num}"
    if row_label not in df.index:
        print(f"Row '{row_label}' does not exist.")
        return

    # --- column selection ---
    print(f"Columns: {list(df.columns)}")
    col_num = input("Enter column number: ").strip()
    col_label = f"c{col_num}"
    if col_label not in df.columns:
        print(f"Column '{col_label}' does not exist.")
        return

    # --- value input ---
    old_value = df.at[row_label, col_label]
    new_value = input(f"Current value at ({row_label}, {col_label}): '{old_value}'\nEnter new string: ").strip()

    # --- replace ---
    df.at[row_label, col_label] = new_value

    print(f"\nUpdated dataframe (D{folder_num}):")
    print(df.to_string())

    save = input("\nSave changes to parquet? (y/n): ").strip().lower()
    if save == "y":
        df.to_parquet(path)
        print(f"Saved to {path}")
    else:
        print("Changes not saved.")


if __name__ == "__main__":
    main()
