#!/usr/bin/env bash
set -euo pipefail

uv python install 3.12
uv venv --python 3.12 --clear .venv
source .venv/bin/activate
uv pip install -r requirements.txt
python repro_openlit_langgraph_messages.py
