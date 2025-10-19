Architected by doctorcodex/ drferdiiskandar\nDeveloped by doctorcodex/ drferdiiskandar\n\n#!/usr/bin/env bash
# Architected by doctorcodex/ drferdiiskandarndar
# Developed by doctorcodex/ drferdiiskandarndar
set -euo pipefail
export LC_ALL=C

# silent pull (ok if no remote)
git pull >/dev/null 2>&1 || true

LATEST="$(ls -1 hub/sessions 2>/dev/null | sort | tail -n1 || true)"

if [[ -z "${LATEST}" ]]; then
  echo "no sessions found."
else
  echo "version:"
  if [[ -f "hub/version.json" ]]; then
    cat "hub/version.json" || true
  else
    echo "{}"
  fi
  echo "----- latest session: ${LATEST} -----"
  tail -n 40 "hub/sessions/${LATEST}" || true
fi

echo
echo "→ manual mode: owner decides when to rehydrate."
echo "→ send summary + version to agents via adapters/* (if active)."
echo "→ paste outputs to agents/<name>/log.md."
