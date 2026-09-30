#!/usr/bin/env bash
# Checker self-test: a valid fixture must pass cleanly; a broken fixture must
# trip every seeded error class; the term-ok escape hatch must silence exactly
# the escaped forward reference; verify.py must genuinely verify the valid
# fixture's blocks, agreeing with the static fixture report; and the palette
# must clear WCAG AA in both themes.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
FIX="$HERE/fixtures"
mkdir -p /tmp/opencode

echo "== [1/5] valid fixture must pass"
if ! "$PY" "$HERE/check.py" --root "$FIX" valid.html; then
  echo "SELF-TEST FAIL: valid fixture reported errors"
  exit 1
fi

# Deterministic mtimes: manifest pages older than the report, broken.html
# newest, so the full run trips exactly one staleness seed.
touch -d "2020-01-01 00:00:00" "$FIX/valid.html" "$FIX/glossary.html" "$FIX/orphan.html"
touch -d "2021-01-01 00:00:00" "$FIX/verify-report.json"
touch "$FIX/broken.html"

echo "== [2/5] broken fixture must fail with every error class"
OUT="$("$PY" "$HERE/check.py" --root "$FIX" 2>&1)"
RC=$?
if [ "$RC" -eq 0 ]; then
  echo "SELF-TEST FAIL: broken fixture passed"
  printf '%s\n' "$OUT"
  exit 1
fi
MISSING=0
for CODE in E_MANIFEST E_STRUCT E_LINK E_EXTERNAL E_CODELANG E_CODELEN E_SVG E_WORDS E_TERM E_PROV E_TAKEAWAYS E_GLOSSARY E_VERIFY; do
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

echo "== [3/5] verify.py must genuinely verify the valid fixture"
TMPREPORT="/tmp/opencode/fixture-verify.json"
if ! "$PY" "$HERE/verify.py" --root "$FIX" --pages valid.html --report "$TMPREPORT"; then
  echo "SELF-TEST FAIL: valid fixture blocks did not verify"
  exit 1
fi

echo "== [4/5] live verification must agree with the static fixture report"
if ! "$PY" "$HERE/compare_reports.py" "$TMPREPORT" "$FIX/verify-report.json" valid.html; then
  echo "SELF-TEST FAIL: static fixture report disagrees with live verification"
  exit 1
fi

echo "== [5/5] palette must clear WCAG AA in both themes"
if ! "$PY" "$HERE/contrast.py"; then
  echo "SELF-TEST FAIL: contrast gate reported a failing pair"
  exit 1
fi

echo "SELF-TEST PASS: checker catches every seeded error class; runner verifies fixtures; palette clears AA"
