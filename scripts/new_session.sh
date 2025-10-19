Architected by doctorcodex/ drferdiiskandar\nDeveloped by doctorcodex/ drferdiiskandar\n\n#!/usr/bin/env bash
# Architected by doctorcodex/ drferdiiskandarndar
# Developed by doctorcodex/ drferdiiskandarndar
set -euo pipefail

# Usage:
#   scripts/new_session.sh            # pakai tanggal hari ini
#   scripts/new_session.sh 2025-10-19 # pakai tanggal tertentu (YYYY-MM-DD)

DATE="${1:-$(date +%F)}"

FILE="hub/sessions/${DATE}.md"
if [[ -f "${FILE}" ]]; then
  echo "session already exists: ${FILE}"
  exit 0
fi

mkdir -p "hub/sessions"

cat > "${FILE}" <<'EOF'
Architected by doctorcodex/ drferdiiskandarndar
Developed by doctorcodex/ drferdiiskandarndar

# session — YYYY-MM-DD

## summary
-

## new decisions
-

## priority impact
-

## open issues / dependencies
-
EOF

# replace placeholder date in title
# note: portable sed for macOS/BSD and GNU
if sed --version >/dev/null 2>&1; then
  sed -i "s/YYYY-MM-DD/${DATE}/g" "${FILE}"
else
  sed -i '' "s/YYYY-MM-DD/${DATE}/g" "${FILE}"
fi

echo "new session created: ${FILE}"
