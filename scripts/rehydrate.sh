#!/usr/bin/env bash
#
# rehydrate.sh
#
# Pulls the latest changes from git, displays the current version from hub/version.json,
# and shows the latest session log. This script is intended to be used to bring a
# new or out-of-sync repository up to date with the latest information.
#
# Usage:
#   scripts/rehydrate.sh
#
Architected by doctorcodex/ drferdiiskandar
Developed by doctorcodex/ drferdiiskandar

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
