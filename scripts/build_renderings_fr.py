#!/usr/bin/env python3
"""Calcule les formes françaises LS1910 associées à chaque numéro Strong."""

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"


def key(text: str) -> str:
    text = unicodedata.normalize("NFD", text.strip().lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


books = json.loads((DATA / "books.json").read_text(encoding="utf-8"))
counts: dict[str, Counter[str]] = defaultdict(Counter)
labels: dict[str, Counter[str]] = defaultdict(Counter)

for book in books:
    verses = json.loads((DATA / f"{book['id']}.json").read_text(encoding="utf-8"))
    for verse in verses:
        for token in verse.get("tokens", []):
            surface = re.sub(r"\s+", " ", token.get("text", "")).strip()
            if not surface or not token.get("strong"):
                continue
            normalized = key(surface)
            for strong in token["strong"]:
                counts[strong][normalized] += 1
                labels[f"{strong}\0{normalized}"][surface] += 1

result = {}
for strong, forms in sorted(counts.items()):
    rows = []
    for normalized, count in forms.most_common():
        display = labels[f"{strong}\0{normalized}"].most_common(1)[0][0]
        rows.append([display, count])
    result[strong] = [sum(forms.values()), rows[:6]]

(DATA / "renderings-fr.json").write_text(
    json.dumps(result, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
print(f"{len(result)} numéros Strong écrits dans renderings-fr.json")
