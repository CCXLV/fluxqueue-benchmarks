#!/bin/bash

set -e

if [[ $# -lt 2 || ! "$1" =~ ^[0-9]+$ ]]; then
  echo "Usage: $0 <num_processes> <command...>"
  exit 1
fi

N=$1
shift

PID_FILE="pids.log"

# Start the requested processes and capture their PIDs (these are typically "master" processes)
master_pids=()
> "$PID_FILE"

for ((i=1; i<=N; i++)); do
  "$@" &
  PID=$!
  master_pids+=("$PID")
done

# Give children (e.g. Celery workers) a moment to spawn
sleep 2

all_pids=("${master_pids[@]}")

# On Linux, also capture direct children of each master (covers Celery worker pool)
if [[ "$(uname -s)" == "Linux" ]]; then
  for mpid in "${master_pids[@]}"; do
    if ps -p "$mpid" > /dev/null 2>&1; then
      while read -r child; do
        [[ -n "$child" ]] && all_pids+=("$child")
      done < <(ps --ppid "$mpid" -o pid= 2>/dev/null)
    fi
  done
fi

# Deduplicate and write all PIDs (masters + workers) into pids.log on a single line
mapfile -t unique_pids < <(printf '%s\n' "${all_pids[@]}" | sort -n | uniq)
{
  for pid in "${unique_pids[@]}"; do
    printf "%s " "$pid"
  done
  echo
} > "$PID_FILE"

wait
