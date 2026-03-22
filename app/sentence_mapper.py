"""
sentence_mapper.py

Takes a free-form sentence from the user, maps it to
(o1, o2, property, value) by matching against known concepts
in smartrules.csv, then logs the result with a timestamp.
"""

import re
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
LOG_FILE = BASE_DIR / "logs" / "sentence_mapper.log"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

n = input("Enter folder number: ")
folder = DATA_DIR / f"D{n}"

# Load all known concepts from smartrules
import pandas as pd
rules = pd.read_csv(folder / "smartrules.csv")

known_o1    = [str(v).strip().lower() for v in rules["o1"].unique()]
known_o2    = [str(v).strip().lower() for v in rules["o2"].unique()]
known_props = [str(v).strip().lower() for v in rules["property-or-threshold"].unique()]
known_vals  = [str(v).strip().lower() for v in rules["value"].unique()]

sentence = input("Enter sentence: ")
sentence_lc = sentence.lower()


def find_match(candidates, text):
    """Return first candidate that matches text via direct substring or shared 4-char chunk."""
    words = re.findall(r"[a-z]+", text)
    for candidate in candidates:
        # Direct substring match
        if candidate in text:
            return candidate
        # Shared chunk: any 4-char substring of the candidate appears in any word
        chunks = [candidate[i:i+4] for i in range(len(candidate) - 3)]
        if any(chunk in word for chunk in chunks for word in words if len(word) >= 4):
            return candidate
    return None


def find_number(text):
    """Return first integer found in text, else None."""
    match = re.search(r"\b\d+\b", text)
    return match.group() if match else None


mapped = {
    "o1":       find_match(known_o1, sentence_lc),
    "o2":       find_match(known_o2, sentence_lc),
    "property": find_match(known_props, sentence_lc),
    "value":    find_match(known_vals, sentence_lc) or find_number(sentence_lc),
}

timestamp = datetime.now(timezone.utc).isoformat()

log_entry = {
    "timestamp": timestamp,
    "folder":    f"D{n}",
    "sentence":  sentence,
    "mapping":   mapped,
}

with LOG_FILE.open("a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry) + "\n")

print("\nMapping:")
for k, v in mapped.items():
    print(f"  {k:10} -> {v}")
print(f"\nLogged to {LOG_FILE}")
