#!/usr/bin/env bash
#
# rex_validate.sh
#
# Validates the health of the Sentra infrastructure dashboard by performing a series of checks.
# This script is intended to be run as part of a CI/CD pipeline or manually to ensure that
# the dashboard is functioning correctly.
#
# Usage:
#   scripts/rex_validate.sh
#
set -euo pipefail

# Use BASE environment variable if provided, otherwise detect from script location
if [ -n "${BASE:-}" ]; then
  ROOT_DIR="$BASE"
else
  ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
fi

DASH_DIR="$ROOT_DIR/sentra/infrastructure/dashboard"
LOG_FILE="$ROOT_DIR/ops/health/daily.md"

iso_time() {
  date -Iseconds
}

commit_hash() {
  if git -C "$ROOT_DIR" rev-parse --short HEAD >/dev/null 2>&1; then
    git -C "$ROOT_DIR" rev-parse --short HEAD
  else
    echo "NO-VCS"
  fi
}

status_code() {
  local url="$1"
  curl --max-time 10 -s -o /dev/null -w "%{http_code}\n" "$url"
}

header_has() {
  local url="$1"; shift
  local pattern="$1"
  curl --max-time 10 -sI "$url" | grep -iE "^content-type:.*$pattern" >/dev/null 2>&1 && echo OK || echo FAIL
}

jq_check() {
  local url="$1"
  curl --max-time 10 -s "$url" | jq -e '.packet and .versionContext and .latestSession and .recentDiscussions' >/dev/null 2>&1 && echo OK || echo FAIL
}

branding_count() {
  if command -v rg >/dev/null 2>&1; then
    rg -n "Architected by doctorcodex/ drferdiiskandar|Developed by doctorcodex/ drferdiiskandar" "$DASH_DIR/src" | wc -l | tr -d ' '
  else
    grep -RinE "Architected by doctorcodex/ drferdiiskandar|Developed by doctorcodex/ drferdiiskandar" "$DASH_DIR/src" | wc -l | tr -d ' '
  fi
}

path_check() {
  if git -C "$ROOT_DIR" ls-files >/dev/null 2>&1; then
    git -C "$ROOT_DIR" ls-files | xargs grep -n "sentra/dashboard/" >/dev/null 2>&1 && echo HAS_OLD_PATH || echo OK
  else
    # Fallback: scan workspace
    if grep -Rin "sentra/dashboard/" "$ROOT_DIR" >/dev/null 2>&1; then
      echo HAS_OLD_PATH
    else
      echo OK
    fi
  fi
}

main() {
  local ts commit
  ts=$(iso_time)
  commit=$(commit_hash)

  # Status codes
  local code_rehydrate code_memory code_rollup code_packet_json
  code_rehydrate=$(status_code "http://127.0.0.1:3000/api/rehydrate") || true
  code_memory=$(curl --max-time 10 -s -o /dev/null -w "%{http_code}\n" -X POST -H 'Content-Type: application/json' -d '{"type":"note","title":"health-check","content":"ok"}' http://127.0.0.1:3000/api/memory) || true
  code_rollup=$(curl --max-time 10 -s -o /dev/null -w "%{http_code}\n" -X POST -H 'Content-Type: application/json' -d '{"content":"health rollup"}' http://127.0.0.1:3000/api/rollup) || true
  code_packet_json=$(status_code "http://127.0.0.1:3000/api/packet?format=json") || true

  # Content-type checks
  local ct_packet_text ct_packet_json
  ct_packet_text=$(header_has "http://127.0.0.1:3000/api/packet" "text/plain")
  ct_packet_json=$(header_has "http://127.0.0.1:3000/api/packet?format=json" "application/json")

  # JSON structure
  local json_ok
  json_ok=$(jq_check "http://127.0.0.1:3000/api/packet?format=json")

  # Branding & path checks
  local brand_cnt path_stat
  brand_cnt=$(branding_count)
  path_stat=$(path_check)

  # Decide Passed/Failed
  local status="Passed"
  if [ "$code_rehydrate" != "200" ] || [ "$code_memory" != "200" ] || [ "$code_rollup" != "200" ] || [ "$code_packet_json" != "200" ] || [ "$ct_packet_text" != "OK" ] || [ "$ct_packet_json" != "OK" ] || [ "$json_ok" != "OK" ] || [ "$path_stat" != "OK" ]; then
    status="Failed"
  fi

  # Compose log entry
  {
    echo "## Validation $(iso_time)"
    echo "- commit: $commit"
    echo "- rehydrate: $code_rehydrate"
    echo "- memory: $code_memory"
    echo "- rollup: $code_rollup"
    echo "- packet_json: $code_packet_json"
    echo "- ct_packet_text: $ct_packet_text"
    echo "- ct_packet_json: $ct_packet_json"
    echo "- json_structure: $json_ok"
    echo "- branding_count: $brand_cnt"
    echo "- path_check: $path_stat"
    echo "- status: $status"
    if [ "$status" = "Failed" ]; then
      echo "- Root Cause + Fix Needed:"
      [ "$code_rehydrate" = "200" ] || echo "  * rehydrate HTTP != 200"
      [ "$code_memory" = "200" ] || echo "  * memory HTTP != 200 (check POST body handling)"
      [ "$code_rollup" = "200" ] || echo "  * rollup HTTP != 200 (check POST body handling and file write paths)"
      [ "$code_packet_json" = "200" ] || echo "  * packet?format=json HTTP != 200"
      [ "$ct_packet_text" = "OK" ] || echo "  * /api/packet content-type not text/plain"
      [ "$ct_packet_json" = "OK" ] || echo "  * /api/packet?format=json content-type not application/json"
      [ "$json_ok" = "OK" ] || echo "  * JSON structure missing required fields"
      [ "$path_stat" = "OK" ] || echo "  * Legacy path detected"
    fi
    echo
  } >> "$LOG_FILE"

  echo "Validation $status. Log written to $LOG_FILE"
}

main "$@"
