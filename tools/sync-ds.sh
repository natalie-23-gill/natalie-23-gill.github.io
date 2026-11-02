#!/usr/bin/env bash
# Refresh the design system files copied into the site.
#
# Get the export: open the "Natalie Gill" design system on claude.ai, download its files, and unzip
# them; pass the folder that holds tokens.json, fonts/, components/ and assets/ (the "project/" folder).
#   tools/sync-ds.sh path/to/project        (or set DS_DIR)
# Needs a Python with fontTools, brotli and Pillow (pip install fonttools brotli pillow in a venv) for the
# WOFF2 conversion and the still frames; set PYTHON to that interpreter if it is not python3.
# gen_tokens.py itself is stdlib only.
#
# What it refreshes: assets/tokens.css and the FIELD constants line in assets/field.js (gen_tokens.py),
# assets/bundle.css, the fonts, the plot themes, the favicon (logo/favicon.svg, which switches by color scheme),
# and the still frames (social card, footer strip). The header mark is the path of the Logo group's ng-mark.svg
# inlined in _templates/partials/header.html, and the PNG favicons in assets/logo/ are asset-store uploads:
# refresh those by hand if the mark changes.
# The field engine itself is a port of the Field/Engine code in components/bundle.js; tools/ds-engine.sha256
# records the version it was ported from. If that code changes, the script stops with an error after syncing
# everything else: port the change into assets/field.js and tools/still_frames.py, then rerun with
# ACCEPT_ENGINE=1 to record the new hash.
set -euo pipefail
DS="${1:-${DS_DIR:?usage: tools/sync-ds.sh path/to/design-system/project}}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; PY="${PYTHON:-python3}"
mkdir -p "$ROOT/assets/fonts" "$ROOT/tools/plots/fonts"
python3 "$ROOT/tools/gen_tokens.py" "$DS/tokens.json" "$ROOT/assets/tokens.css" "$ROOT/assets/field.js"
cp "$DS/components/bundle.css" "$ROOT/assets/bundle.css"
for f in "$DS"/fonts/*.ttf; do
  "$PY" -m fontTools.ttLib.woff2 compress -o "$ROOT/assets/fonts/$(basename "${f%.ttf}").woff2" "$f"
  cp "$f" "$ROOT/tools/plots/fonts/"   # TTFs for figure rendering only (matplotlib/systemfonts cannot read WOFF2)
done
cp "$DS/logo/favicon.svg" "$ROOT/assets/favicon.svg"
cp "$DS/assets/Plots/theme_ng.R" "$DS/assets/Plots/ngtheme.py" "$ROOT/tools/plots/"
"$PY" "$ROOT/tools/still_frames.py"

# The engine: the bundle.js source from "function Engine" up to "function Field", minus the generated
# FIELD constants (those come from the tokens above).
engine_hash() { sed -n '/function Engine/,/function Field/p' "$DS/components/bundle.js" | sha256sum | cut -d' ' -f1; }
NEW="$(engine_hash)"; OLD="$(cat "$ROOT/tools/ds-engine.sha256" 2>/dev/null || true)"
if [ "$NEW" != "$OLD" ]; then
  if [ "${ACCEPT_ENGINE:-}" = 1 ]; then
    echo "$NEW" > "$ROOT/tools/ds-engine.sha256"; echo "Recorded the new field engine hash."
  else
    echo "error: the field engine in components/bundle.js changed since assets/field.js was ported." >&2
    echo "Port the change into assets/field.js and tools/still_frames.py, then rerun with ACCEPT_ENGINE=1." >&2
    exit 3
  fi
fi
echo "Synced."
