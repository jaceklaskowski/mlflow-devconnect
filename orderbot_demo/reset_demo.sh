#!/bin/sh
# Wipe local MLflow state and pytest cache so a rehearsal starts from a clean slate.
set -e
cd "$(dirname "$0")"
rm -rf mlruns mlartifacts .pytest_cache
echo "Demo state reset. Next 'pytest test_agent_quality.py -v' will be a fresh run."
