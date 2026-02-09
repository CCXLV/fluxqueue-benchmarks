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

# Helper to format epoch seconds in a portable way
format_epoch() {
    local epoch=$1
    if [ "$OS_TYPE" = "Darwin" ]; then
        date -r "$epoch" '+%Y-%m-%d %H:%M:%S'
    else
        date -d "@$epoch" '+%Y-%m-%d %H:%M:%S'
    fi
}

# Get initial CPU times (Linux /proc only)
if [ "$OS_TYPE" != "Darwin" ]; then
    for pid in $(cat pids.log 2>/dev/null); do
        if [ -f "/proc/$pid/stat" ]; then
            stat_content=$(cat /proc/$pid/stat)
            utime=$(echo "$stat_content" | awk '{print $14}')
            stime=$(echo "$stat_content" | awk '{print $15}')
            prev_utime[$pid]=$utime
            prev_stime[$pid]=$stime
            prev_time[$pid]=$(date +%s%N)
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
    current_time=$(date +%s%N)
    
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$TEMP_DATA"
    
    for pid in $(cat pids.log 2>/dev/null); do
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
                    if [ -n "${prev_utime[$pid]}" ] && [ "${prev_utime[$pid]}" -ne 0 ] 2>/dev/null; then
                        time_diff=$((current_time - prev_time[$pid]))
                        cpu_diff=$(( (utime + stime) - (prev_utime[$pid] + prev_stime[$pid]) ))
                        
                        if [ "$time_diff" -gt 0 ] 2>/dev/null; then
                            # Convert ns to seconds for more accurate interval
                            time_diff_sec=$(awk "BEGIN {printf \"%.6f\", $time_diff / 1000000000}")
                            # Calculate raw CPU percentage (can exceed 100 for multi-core)
                            cpu_usage=$(awk "BEGIN {printf \"%.2f\", (100 * $cpu_diff) / ($CLK_TCK * $time_diff_sec)}")
                        fi
                    fi
                    
                    # Calculate per-core CPU if multi-threaded
                    if [ "$is_multi" = true ] && [ "$(echo "$cpu_usage > 0" | bc -l)" -eq 1 ] 2>/dev/null; then
                        cpu_per_core=$(awk "BEGIN {printf \"%.2f\", $cpu_usage / $NUM_CORES}")
                    else
                        cpu_per_core=$cpu_usage
                    fi
                    
                    prev_utime[$pid]=$utime
                    prev_stime[$pid]=$stime
                    prev_time[$pid]=$current_time
                    
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
    
    # Check if all processes are dead
    if [ $alive_count -eq 0 ]; then
        echo "---" >> "$TEMP_DATA"
        echo "All processes terminated at $(date)" >> "$TEMP_DATA"
        break
    fi
    
    # Calculate total per-core from total raw CPU
    total_cpu_per_core=$(awk "BEGIN {printf \"%.2f\", $total_cpu / $NUM_CORES}")
    
    echo "---" >> "$TEMP_DATA"
    total_mb=$(awk "BEGIN {printf \"%.2f\", $total_rss/1024}")
    total_gb=$(awk "BEGIN {printf \"%.2f\", $total_rss/1024/1024}")
    printf "TOTAL (%d/%d alive): CPU: %s%% (%.2f%% per-core)  |  RSS: %d KB (%s MB) (%s GB)\n" \
           "$alive_count" "$(wc -w < pids.log)" "$total_cpu" "$total_cpu_per_core" "$total_rss" "$total_mb" "$total_gb" >> "$TEMP_DATA"
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
           "$alive_count" "$(wc -w < pids.log)" "$total_cpu" "$total_cpu_per_core" "$total_mb"
    
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