#!/bin/bash

PID_FILE="pids.log"

if [[ ! -f "$PID_FILE" ]]; then
  echo "pids.log not found"
  exit 1
fi

for pid in $(cat "$PID_FILE"); do
  if kill -0 "$pid" 2>/dev/null; then
    echo "Killing PID $pid"
    kill "$pid"
  else
    echo "PID $pid not running"
  fi
done
