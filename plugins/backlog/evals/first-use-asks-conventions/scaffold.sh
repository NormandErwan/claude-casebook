#!/usr/bin/env bash
# app.py only (shared fixture).
set -euo pipefail
bash "$(dirname "$0")/../fixture-app.sh"
