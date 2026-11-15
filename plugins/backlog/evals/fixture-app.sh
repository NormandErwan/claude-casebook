#!/usr/bin/env bash
# Shared fixture: writes app.py into the case workspace (the current directory).
set -euo pipefail
cat > app.py <<'PY'
import json


def load_config(path):
    with open(path) as f:
        return json.load(f)


def apply_discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


if __name__ == "__main__":
    config = load_config("config.json")
    print(apply_discount(config["price"], config["discount"]), config["currency"])
PY
