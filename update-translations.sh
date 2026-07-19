#!/usr/bin/env bash
# Update the translation catalogs after changing _() strings in the source
# or editing a .po file by hand:
#   1. Re-extract the .pot template from the source.
#   2. Merge it into each language's .po (new/changed strings in, existing
#      translations kept).
#   3. Recompile all .po files to .mo, which is what the app actually reads.
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! "$PYTHON" -c "import babel" >/dev/null 2>&1; then
    echo "Babel is required for this. Install it with: pip install -e .[dev]" >&2
    exit 1
fi

if ! command -v msgmerge >/dev/null 2>&1; then
    echo "msgmerge (GNU gettext) is required to merge new strings into" >&2
    echo "existing .po files. On macOS: brew install gettext" >&2
    exit 1
fi

"$PYTHON" setup.py extract_messages

POT=optimize_images_x/locale/optimize_images_x.pot
for po in optimize_images_x/locale/*/LC_MESSAGES/optimize_images_x.po; do
    echo "Merging into $po"
    msgmerge --update --backup=none "$po" "$POT"
done

"$PYTHON" setup.py compile_catalog
