Architected by doctorcodex/ drferdiiskandar\nDeveloped by doctorcodex/ drferdiiskandar\n\n#!/usr/bin/env bash
# Architected by doctorcodex/ drferdiiskandarndar
# Developed by doctorcodex/ drferdiiskandarndar
set -euo pipefail

# Usage:
#   scripts/bundle_archive.sh            # auto-detect bulan (YYYY-MM) dari tanggal hari ini
#   scripts/bundle_archive.sh 2025-10    # arsip untuk bulan tertentu

MONTH="${1:-$(date +%Y-%m)}"
OUTDIR="archives"
mkdir -p "${OUTDIR}"

NAME="knowledge-vault-${MONTH}.zip"
ZIP="${OUTDIR}/${NAME}"

rm -f "${ZIP}" || true

# Arsipkan direktori penting (tanpa .git bila ada)
zip -rq "${ZIP}"       hub agents ops configs scripts readme.txt owner-command.md       -x "*.git*" "archives/*"

echo "archive created: ${ZIP}"
