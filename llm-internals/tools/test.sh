#!/usr/bin/env bash
# Checker self-test: a valid fixture must pass cleanly; a broken fixture must
# trip every seeded error class; the term-ok escape hatch must silence exactly
# the escaped forward reference.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"

echo "== [1/2] valid fixture must pass"
if ! "$PY" "$HERE/check.py" --root "$HERE/fixtures" valid.html; then
  echo "SELF-TEST FAIL: valid fixture reported errors"
  exit 1
fi

echo "== [2/2] broken fixture must fail with every error class"
OUT="$("$PY" "$HERE/check.py" --root "$HERE/fixtures" 2>&1)"
RC=$?
if [ "$RC" -eq 0 ]; then
  echo "SELF-TEST FAIL: broken fixture passed"
  printf '%s\n' "$OUT"
  exit 1
fi
MISSING=0
for CODE in E_MANIFEST E_STRUCT E_LINK E_EXTERNAL E_CODELANG E_CODELEN E_SVG E_WORDS E_TERM E_PROV E_TAKEAWAYS E_GLOSSARY; do
  if ! printf '%s\n' "$OUT" | grep -q "$CODE"; then
    echo "SELF-TEST FAIL: checker missed $CODE"
    MISSING=1
  fi
done
if [ "$MISSING" -ne 0 ]; then
  printf '%s\n' "$OUT"
  exit 1
fi

NTERM="$(printf '%s\n' "$OUT" | grep -c 'E_TERM')"
if [ "$NTERM" -ne 1 ]; then
  echo "SELF-TEST FAIL: expected exactly one E_TERM (escape hatch must work), got $NTERM"
  printf '%s\n' "$OUT"
  exit 1
fi

echo "SELF-TEST PASS: checker catches every seeded error class"
