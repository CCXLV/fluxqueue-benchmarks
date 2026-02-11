#!/bin/bash

set -euo pipefail

# Usage:
#   ./scripts/send_db_requests.sh path/to/emails.txt 100
# If not provided:
#   emails file defaults to scripts/emails.txt
#   limit defaults to 50

EMAILS_FILE="${1:-scripts/emails.txt}"
LIMIT="${2:-50}"

BASE_URL="http://localhost:8000/fluxqueue/db"

if ! command -v hey >/dev/null 2>&1; then
  echo "Error: 'hey' is not installed or not in PATH." >&2
  exit 1
fi

if [[ ! -f "$EMAILS_FILE" ]]; then
  echo "Error: emails file '$EMAILS_FILE' not found." >&2
  exit 1
fi

echo "Sending requests for first $LIMIT emails from '$EMAILS_FILE'"

head -n "$LIMIT" "$EMAILS_FILE" | while IFS= read -r email; do
  [[ -z "$email" ]] && continue

  echo "Sending load test for email: $email"
  hey -n 1 -c 1 -m POST "${BASE_URL}/${email}"
done

echo "Done sending requests."

