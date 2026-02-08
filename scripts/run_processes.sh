#!/bin/bash

set -e

if [[ $# -lt 2 || ! "$1" =~ ^[0-9]+$ ]]; then
  echo "Usage: $0 <num_processes> <command...>"
  exit 1
fi

N=$1
shift

PID_FILE="pids.log"

> "$PID_FILE"

for ((i=1; i<=N; i++)); do
  "$@" &
  PID=$!
  echo -n "$PID " >> "$PID_FILE"
done

echo >> "$PID_FILE"

wait
