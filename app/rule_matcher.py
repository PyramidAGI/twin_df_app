"""
rule_matcher.py — Match input words against common sense rules CSV and show top 3 hits.
Uses entity_lookup.csv to resolve coded IDs (e.g. thing993 -> vase) in display.
"""

import os
from difflib import SequenceMatcher
import pandas as pd

CSV_PATH    = os.path.join(os.path.dirname(__file__), "..", "data", "common sense rules.csv")
LOOKUP_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "entity_lookup.csv")

STOPWORDS = {
    "who", "what", "where", "when", "why", "how",
    "is", "are", "was", "were", "be", "been", "being",
    "a", "an", "the", "in", "on", "at", "to", "of",
    "and", "or", "for", "with", "has", "have", "had",
    "do", "does", "did", "it", "its", "this", "that",
    "there", "their", "they", "he", "she", "we", "i",
}


def load_rules() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, sep=";")
    df["e0"] = df["e0"].ffill()
    return df


def load_lookup() -> dict[str, str]:
    """Return {code: name} for all entries that have a name."""
    ldf = pd.read_csv(LOOKUP_PATH, sep=";")
    return {
        row["code"]: row["name"]
        for _, row in ldf.iterrows()
        if pd.notna(row["name"]) and str(row["name"]).strip()
    }


def resolve(code: str, lookup: dict[str, str]) -> str:
    """Return 'name (code)' if known, otherwise just 'code'."""
    name = lookup.get(str(code).strip())
    return f"{name} ({code})" if name else str(code)


def row_tokens(row: pd.Series, lookup: dict[str, str]) -> list[str]:
    """Return all non-null cell values as lowercase tokens for matching.
    Entity codes are expanded with their lookup name; message is split into words."""
    tokens = []
    for col, val in row.items():
        if pd.notna(val) and str(val).strip():
            text = str(val).strip().lower()
            if col == "message":
                tokens.extend(text.split())
            else:
                tokens.append(text)
                # also add the human name so input like "vase" matches thing993
                name = lookup.get(text)
                if name:
                    tokens.append(name.lower())
    return tokens


def score_row(words: list[str], tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    total = 0.0
    for word in words:
        best = max(SequenceMatcher(None, word, token).ratio() for token in tokens)
        total += best
    return total


def find_top_matches(words: list[str], df: pd.DataFrame, lookup: dict[str, str], n: int = 3) -> pd.DataFrame:
    scores = []
    for _, row in df.iterrows():
        tokens = row_tokens(row, lookup)
        scores.append(score_row(words, tokens))

    df = df.copy()
    df["_score"] = scores
    top = df.nlargest(n, "_score").drop(columns=["_score"])
    return top


def format_row(row: pd.Series, lookup: dict[str, str]) -> str:
    entity_cols = {"e2", "e3", "e4"}
    parts = []
    for col, val in row.items():
        if pd.notna(val) and str(val).strip():
            display = resolve(val, lookup) if col in entity_cols else str(val)
            parts.append(f"{col}={display}")
    return "  |  ".join(parts)


def main():
    df     = load_rules()
    lookup = load_lookup()
    print(f"Loaded {len(df)} rules  |  {len(lookup)} lookup entries")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("Enter search string: ").strip()
        if user_input.lower() in ("quit", "q", "exit"):
            print("Goodbye.")
            break
        if not user_input:
            continue

        words = [w.strip("?!.,;:").lower() for w in user_input.split() if w.strip("?!.,;:").lower() not in STOPWORDS and w.strip("?!.,;:")]
        if not words:
            print("(no meaningful words to match after filtering stopwords)\n")
            continue
        top   = find_top_matches(words, df, lookup)

        print(f"\nTop {len(top)} matches for '{user_input}':")
        for rank, (_, row) in enumerate(top.iterrows(), start=1):
            msg = row.get("message", None)
            msg_str = f"\n     >> {msg}" if pd.notna(msg) and str(msg).strip() else ""
            print(f"  {rank}. {format_row(row, lookup)}{msg_str}")
        print()


if __name__ == "__main__":
    main()
