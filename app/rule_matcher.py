"""
rule_matcher.py — Match input words against common sense rules CSV and show top 3 hits.
"""

import os
from difflib import SequenceMatcher
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "common sense rules.csv")


def load_rules() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, sep=";")
    # Forward-fill e0 so every row knows its group
    df["e0"] = df["e0"].ffill()
    return df


def row_tokens(row: pd.Series) -> list[str]:
    """Return all non-null string cell values in a row as lowercase tokens."""
    tokens = []
    for val in row:
        if pd.notna(val):
            tokens.append(str(val).strip().lower())
    return tokens


def score_row(words: list[str], tokens: list[str]) -> float:
    """
    Score a row by summing the best fuzzy match ratio for each input word
    against any token in the row.
    """
    if not tokens:
        return 0.0
    total = 0.0
    for word in words:
        best = max(
            SequenceMatcher(None, word, token).ratio()
            for token in tokens
        )
        total += best
    return total


def find_top_matches(words: list[str], df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    scores = []
    for idx, row in df.iterrows():
        tokens = row_tokens(row)
        scores.append(score_row(words, tokens))

    df = df.copy()
    df["_score"] = scores
    top = df.nlargest(n, "_score").drop(columns=["_score"])
    return top


def format_row(row: pd.Series) -> str:
    parts = []
    for col, val in row.items():
        if pd.notna(val) and str(val).strip():
            parts.append(f"{col}={val}")
    return "  |  ".join(parts)


def main():
    df = load_rules()
    print(f"Loaded {len(df)} rules from '{CSV_PATH}'")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("Enter search string: ").strip()
        if user_input.lower() in ("quit", "q", "exit"):
            print("Goodbye.")
            break
        if not user_input:
            continue

        words = [w.lower() for w in user_input.split()]
        top = find_top_matches(words, df)

        print(f"\nTop {len(top)} matches for '{user_input}':")
        for rank, (_, row) in enumerate(top.iterrows(), start=1):
            print(f"  {rank}. {format_row(row)}")
        print()


if __name__ == "__main__":
    main()
