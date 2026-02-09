#!/bin/bash

OUTPUT="monitor.log"
TEMP_DATA=$(mktemp)

OS_TYPE=$(uname -s)

# Get system info
CLK_TCK=$(getconf CLK_TCK 2>/dev/null || echo 100)

if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS: use sysctl to get core count
    NUM_CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo 1)
else
    # Linux and others: fall back to nproc
    if command -v nproc >/dev/null 2>&1; then
        NUM_CORES=$(nproc)
    else
        NUM_CORES=1
    fi
fi

INTERVAL=0.2

# Store previous CPU times for calculating usage
declare -A prev_utime
declare -A prev_stime
declare -A prev_time

# Statistics tracking
total_samples=0
sum_cpu=0
sum_rss=0
max_cpu=0
max_rss=0
min_cpu=999999
min_rss=999999

# Check if a process is multi-threaded
is_multithreaded() {
    local pid=$1

    if [ "$OS_TYPE" = "Darwin" ]; then
        # macOS: use ps thcount
        local threads
        threads=$(ps -p "$pid" -o thcount= 2>/dev/null | awk '{print $1}')
        if [ -n "$threads" ] && [ "$threads" -gt 1 ] 2>/dev/null; then
            return 0
        fi
    else
        # Linux: use /proc
        if [ -f "/proc/$pid/status" ]; then
            local threads
            threads=$(grep "^Threads:" /proc/$pid/status | awk '{print $2}')
            if [ -n "$threads" ] && [ "$threads" -gt 1 ] 2>/dev/null; then
                return 0
            fi
        fi
    fi

    return 1
}

# Expand the list of PIDs we monitor to include process trees (useful for Celery-style workers)
get_monitored_pids() {
    # On macOS, just use the PIDs from the file as-is
    if [ "$OS_TYPE" = "Darwin" ]; then
        cat pids.log 2>/dev/null
        return
    fi

    # On Linux, walk full process subtrees under the base PIDs
    if [ ! -f pids.log ]; then
        return
    fi

    local base_pids
    base_pids=$(cat pids.log 2>/dev/null)

    local all_pids=()
    local frontier=()

    # Seed with the base PIDs
    for pid in $base_pids; do
        all_pids+=("$pid")
        frontier+=("$pid")
    done

    # BFS over children using ps --ppid to capture all descendants
    while ((${#frontier[@]})); do
        local new_frontier=()

        for ppid in "${frontier[@]}"; do
            if ps -p "$ppid" >/dev/null 2>&1; then
                while read -r child; do
                    [ -z "$child" ] && continue
                    all_pids+=("$child")
                    new_frontier+=("$child")
                done < <(ps --ppid "$ppid" -o pid= 2>/dev/null)
            fi
        done

        frontier=("${new_frontier[@]}")
    done

    # Deduplicate and output as a flat list
    printf '%s\n' "${all_pids[@]}" | sort -n | uniq
}

# Helper to format epoch seconds in a portable way
format_epoch() {
    local epoch=$1
    if [ "$OS_TYPE" = "Darwin" ]; then
        date -r "$epoch" '+%Y-%m-%d %H:%M:%S'
    else
        date -d "@$epoch" '+%Y-%m-%d %H:%M:%S'
    fi
}

# Capture the baseline set of PIDs we will monitor for the entire session
BASELINE_PIDS=$(get_monitored_pids)
TOTAL_BASELINE=$(echo "$BASELINE_PIDS" | wc -w | awk '{print $1}')

# Get initial CPU times (Linux /proc only)
if [ "$OS_TYPE" != "Darwin" ]; then
    # Track previous total CPU jiffies for system-wide baseline
    prev_total_jiffies=$(awk '/^cpu / {sum=0; for (i=2; i<=NF; i++) sum+=$i; print sum}' /proc/stat)

    for pid in $BASELINE_PIDS; do
        if [ -f "/proc/$pid/stat" ]; then
            stat_content=$(cat /proc/$pid/stat)
            utime=$(echo "$stat_content" | awk '{print $14}')
            stime=$(echo "$stat_content" | awk '{print $15}')
            prev_utime[$pid]=$utime
            prev_stime[$pid]=$stime
        fi
    done
fi

echo "Monitoring processes (auto-detecting multi-threaded processes)..."
echo "CPU cores detected: $NUM_CORES"
sleep $INTERVAL

start_time=$(date +%s)

while true; do
    total_rss=0
    total_cpu=0
    count=0
    alive_count=0
    
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$TEMP_DATA"

    # Use the baseline set of PIDs (masters + workers) for the entire session
    monitored_pids="$BASELINE_PIDS"
    total_monitored="$TOTAL_BASELINE"

    # For Linux, precompute total CPU jiffies delta for this sampling interval
    if [ "$OS_TYPE" != "Darwin" ]; then
        current_total_jiffies=$(awk '/^cpu / {sum=0; for (i=2; i<=NF; i++) sum+=$i; print sum}' /proc/stat)
        total_jiffies_diff=$((current_total_jiffies - prev_total_jiffies))
        if [ "$total_jiffies_diff" -le 0 ] 2>/dev/null; then
            total_jiffies_diff=1
        fi
        prev_total_jiffies=$current_total_jiffies
    fi
    
    for pid in $monitored_pids; do
        if [ "$OS_TYPE" = "Darwin" ]; then
            # macOS path: use ps for CPU/memory
            if ps -p "$pid" >/dev/null 2>&1; then
                alive_count=$((alive_count + 1))

                # %cpu from ps is already a percentage and can exceed 100 for multi-threaded workloads.
                read -r cpu_usage vmrss vmsize comm <<<"$(ps -p "$pid" -o %cpu= -o rss= -o vsz= -o comm= 2>/dev/null)"

                cpu_usage=${cpu_usage:-0}
                vmrss=${vmrss:-0}
                vmsize=${vmsize:-0}
                comm=${comm:-unknown}

                # Detect multi-threaded using thcount
                is_multi=false
                threads=$(ps -p "$pid" -o thcount= 2>/dev/null | awk '{print $1}')
                threads=${threads:-1}
                if [ "$threads" -gt 1 ] 2>/dev/null; then
                    is_multi=true
                fi

                # Per-core adjustment only for multi-threaded processes
                if [ "$is_multi" = true ]; then
                    cpu_per_core=$(awk "BEGIN {printf \"%.2f\", $cpu_usage / $NUM_CORES}")
                else
                    cpu_per_core=$cpu_usage
                fi

                thread_indicator=""
                if [ "$is_multi" = true ]; then
                    thread_indicator="[T:$threads]"
                fi

                printf "PID: %7s  CPU: %6s%% (per-core: %6s%%)  RSS: %10s KB  VSZ: %10s KB  %s CMD: %s\n" \
                       "$pid" "$cpu_usage" "$cpu_per_core" "$vmrss" "$vmsize" "$thread_indicator" "$comm" >> "$TEMP_DATA"

                total_rss=$((total_rss + vmrss))
                total_cpu=$(awk "BEGIN {printf \"%.2f\", $total_cpu + $cpu_usage}")
                ((count++))
            fi
        else
            # Linux /proc-based path
            if [ -d "/proc/$pid" ]; then
                alive_count=$((alive_count + 1))
                comm=$(cat /proc/$pid/comm 2>/dev/null || echo "unknown")
                
                # Check if multi-threaded
                is_multi=false
                if is_multithreaded "$pid"; then
                    is_multi=true
                fi
                if [ -f "/proc/$pid/stat" ]; then
                    stat_content=$(cat /proc/$pid/stat)
                    utime=$(echo "$stat_content" | awk '{print $14}')
                    stime=$(echo "$stat_content" | awk '{print $15}')
                    
                    cpu_usage=0
                    if [ -n "${prev_utime[$pid]}" ]; then
                        cpu_diff=$(( (utime + stime) - (prev_utime[$pid] + prev_stime[$pid]) ))
                    else
                        cpu_diff=0
                    fi
                    
                    # Calculate per-process CPU percentage relative to total system CPU
                    if [ "$total_jiffies_diff" -gt 0 ] 2>/dev/null; then
                        cpu_usage=$(awk "BEGIN {printf \"%.2f\", (100 * $cpu_diff) / $total_jiffies_diff}")
                    else
                        cpu_usage=0
                    fi

                    # Calculate per-core CPU if multi-threaded
                    if [ "$is_multi" = true ] && [ "$(echo "$cpu_usage > 0" | bc -l)" -eq 1 ] 2>/dev/null; then
                        cpu_per_core=$(awk "BEGIN {printf \"%.2f\", $cpu_usage / $NUM_CORES}")
                    else
                        cpu_per_core=$cpu_usage
                    fi
                    
                    prev_utime[$pid]=$utime
                    prev_stime[$pid]=$stime
                    
                    if [ -f "/proc/$pid/status" ]; then
                        vmrss=$(grep "^VmRSS:" /proc/$pid/status | awk '{print $2}')
                        vmsize=$(grep "^VmSize:" /proc/$pid/status | awk '{print $2}')
                        threads=$(grep "^Threads:" /proc/$pid/status | awk '{print $2}')
                    else
                        vmrss=0
                        vmsize=0
                        threads=1
                    fi
                    
                    thread_indicator=""
                    if [ "$is_multi" = true ]; then
                        thread_indicator="[T:$threads]"
                    fi
                    
                    printf "PID: %7s  CPU: %6s%% (per-core: %6s%%)  RSS: %10s KB  VSZ: %10s KB  %s CMD: %s\n" \
                           "$pid" "$cpu_usage" "$cpu_per_core" "$vmrss" "$vmsize" "$thread_indicator" "$comm" >> "$TEMP_DATA"
                    
                    total_rss=$((total_rss + vmrss))
                    total_cpu=$(awk "BEGIN {printf \"%.2f\", $total_cpu + $cpu_usage}")
                    ((count++))
                fi
            fi
        fi
    done
    
    # Stop as soon as any baseline PID exits (so averages only cover the full pool)
    if [ "$alive_count" -lt "$total_monitored" ]; then
        echo "---" >> "$TEMP_DATA"
        echo "Monitoring stopped early at $(date) because at least one monitored PID exited." >> "$TEMP_DATA"
        break
    fi
    
    # Calculate total per-core from total raw CPU
    total_cpu_per_core=$(awk "BEGIN {printf \"%.2f\", $total_cpu / $NUM_CORES}")
    
    echo "---" >> "$TEMP_DATA"
    total_mb=$(awk "BEGIN {printf \"%.2f\", $total_rss/1024}")
    total_gb=$(awk "BEGIN {printf \"%.2f\", $total_rss/1024/1024}")
    printf "TOTAL (%d/%d alive): CPU: %s%% (%.2f%% per-core)  |  RSS: %d KB (%s MB) (%s GB)\n" \
           "$alive_count" "$total_monitored" "$total_cpu" "$total_cpu_per_core" "$total_rss" "$total_mb" "$total_gb" >> "$TEMP_DATA"
    echo "" >> "$TEMP_DATA"
    
    # Update statistics - track raw CPU only, calculate per-core from it
    total_samples=$((total_samples + 1))
    sum_cpu=$(awk "BEGIN {printf \"%.2f\", $sum_cpu + $total_cpu}")
    sum_rss=$((sum_rss + total_rss))
    
    # Update max/min values
    max_cpu=$(awk "BEGIN {print ($total_cpu > $max_cpu) ? $total_cpu : $max_cpu}")
    max_rss=$(( total_rss > max_rss ? total_rss : max_rss ))
    min_cpu=$(awk "BEGIN {print ($total_cpu < $min_cpu) ? $total_cpu : $min_cpu}")
    min_rss=$(( total_rss < min_rss ? total_rss : min_rss ))
    
    # Show progress on console
    printf "\rMonitoring: %d/%d alive, CPU: %s%% (%.2f%% per-core), RSS: %s MB       " \
           "$alive_count" "$total_monitored" "$total_cpu" "$total_cpu_per_core" "$total_mb"
    
    sleep $INTERVAL
done

end_time=$(date +%s)
duration=$((end_time - start_time))

# Calculate averages - compute per-core from raw values
if [ "$total_samples" -gt 0 ] 2>/dev/null; then
    avg_cpu=$(awk "BEGIN {printf \"%.2f\", $sum_cpu / $total_samples}")
    avg_cpu_per_core=$(awk "BEGIN {printf \"%.2f\", $avg_cpu / $NUM_CORES}")

    max_cpu_per_core=$(awk "BEGIN {printf \"%.2f\", $max_cpu / $NUM_CORES}")
    min_cpu_per_core=$(awk "BEGIN {printf \"%.2f\", $min_cpu / $NUM_CORES}")

    avg_rss=$(awk "BEGIN {printf \"%.2f\", $sum_rss / $total_samples}")
    avg_rss_mb=$(awk "BEGIN {printf \"%.2f\", $avg_rss / 1024}")
    avg_rss_gb=$(awk "BEGIN {printf \"%.2f\", $avg_rss / 1024 / 1024}")
else
    avg_cpu="0.00"
    avg_cpu_per_core="0.00"
    max_cpu_per_core="0.00"
    min_cpu_per_core="0.00"

    avg_rss="0.00"
    avg_rss_mb="0.00"
    avg_rss_gb="0.00"
fi

max_rss_mb=$(awk "BEGIN {printf \"%.2f\", $max_rss / 1024}")
max_rss_gb=$(awk "BEGIN {printf \"%.2f\", $max_rss / 1024 / 1024}")

min_rss_mb=$(awk "BEGIN {printf \"%.2f\", $min_rss / 1024}")
min_rss_gb=$(awk "BEGIN {printf \"%.2f\", $min_rss / 1024 / 1024}")

# Append to log file
echo ""
cat >> "$OUTPUT" << EOF

################################################################################
#                       NEW MONITORING SESSION
################################################################################
Run at: $(date)
System Info: $NUM_CORES CPU cores, CLK_TCK=$CLK_TCK

================================================================================
                          MONITORING SUMMARY
================================================================================
Start Time:           $(format_epoch "$start_time")
End Time:             $(format_epoch "$end_time")
Duration:             ${duration} seconds
Total Processes:      $(wc -w < pids.log)
Total Samples:        $total_samples
Sample Interval:      ${INTERVAL} seconds

--------------------------------------------------------------------------------
                           CPU STATISTICS
--------------------------------------------------------------------------------
Average CPU Usage:              ${avg_cpu}% (raw) = ${avg_cpu_per_core}% per-core
Maximum CPU Usage:              ${max_cpu}% (raw) = ${max_cpu_per_core}% per-core
Minimum CPU Usage:              ${min_cpu}% (raw) = ${min_cpu_per_core}% per-core

Note: Per-core percentage = raw CPU% / ${NUM_CORES} cores
      Values >100% (raw) indicate multi-threaded workload using multiple cores.
      Per-core values show effective single-core utilization.

--------------------------------------------------------------------------------
                          MEMORY STATISTICS (RSS)
--------------------------------------------------------------------------------
Average Memory:       ${avg_rss} KB (${avg_rss_mb} MB / ${avg_rss_gb} GB)
Maximum Memory:       ${max_rss} KB (${max_rss_mb} MB / ${max_rss_gb} GB)
Minimum Memory:       ${min_rss} KB (${min_rss_mb} MB / ${min_rss_gb} GB)

================================================================================
                          DETAILED MONITORING LOG
================================================================================

EOF

cat "$TEMP_DATA" >> "$OUTPUT"
rm "$TEMP_DATA"

echo "Monitoring complete! Results saved to: $OUTPUT"
echo ""
echo "Summary:"
echo "  Duration: ${duration}s | Samples: $total_samples | Cores: $NUM_CORES"
echo "  Avg CPU: ${avg_cpu}% (raw) = ${avg_cpu_per_core}% per-core"
echo "  Max CPU: ${max_cpu}% (raw) = ${max_cpu_per_core}% per-core"
echo "  Avg RAM: ${avg_rss_mb} MB | Max RAM: ${max_rss_mb} MB"