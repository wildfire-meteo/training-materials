#!/usr/bin/env bash
# Build the book locally and serve it at http://localhost:3000, rebuilding on every save.
# The first run creates .venv/ and installs requirements.txt. Stop with Ctrl+C.
set -e
cd "$(dirname "$0")"

if ! command -v node > /dev/null; then
    echo "Node.js is required: install it from https://nodejs.org (or: brew install node)."
    exit 1
fi

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
.venv/bin/pip install --quiet --disable-pip-version-check -r requirements.txt

export PATH="$PWD/.venv/bin:$PATH"
# The execution cache is keyed on the notebooks only, so changes to odet_meteo/ would not show.
jupyter book clean --execute --yes > /dev/null
exec jupyter book start --execute
