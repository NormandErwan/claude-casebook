#!/usr/bin/env python3
"""Replace OLD by NEW in FILE, only if OLD occurs exactly once.

Builds an arm from a base by explicit edits, never by regex: a pattern that
matches more than the intended line silently changes the arm.

usage: edit-once.py FILE OLD NEW      (OLD/NEW: literal text; "@path" reads a file)
"""
import sys


def arg(s):
    if s.startswith("@"):
        with open(s[1:], encoding="utf-8") as f:
            return f.read()
    return s


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__.strip())
    path, old, new = sys.argv[1], arg(sys.argv[2]), arg(sys.argv[3])
    with open(path, encoding="utf-8") as f:
        text = f.read()
    n = text.count(old)
    if n != 1:
        sys.exit(f"edit-once: {path}: expected 1 match, found {n}: {old[:60]!r}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))
    print(f"edit-once: {path}: 1 edit")


if __name__ == "__main__":
    main()
