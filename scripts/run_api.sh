#!/usr/bin/env bash
set -euo pipefail
uvicorn api.server:app --host 0.0.0.0 --port 8080 --reload
