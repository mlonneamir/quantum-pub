#!/usr/bin/env bash

# Navigate to working directory
cd /Users/maxon/src/quantum || exit 1

TOTAL_RUNS=6
INTERVAL_SECONDS=14400  # 4 hours in seconds
#SHOTS=8192

echo "=================================================="
echo "🚀 Starting 24-Hour Quantum Benchmark Suite"
echo "Start Time: $(date)"
echo "Total Runs: $TOTAL_RUNS (Every 4 Hours)"
echo "Target Shots: 8192"
echo "=================================================="

for ((i=1; i<=TOTAL_RUNS; i++)); do
    # Record the start timestamp in seconds since epoch
    START_TS=$(date +%s)
    
    echo ""
    echo "--------------------------------------------------"
    echo "▶ Execution $i of $TOTAL_RUNS | $(date)"
    echo "--------------------------------------------------"
    
    # Execute Master Quantum Suite
    python3 master_single.py --shots 8192
    
    # Calculate how long the execution (and queueing) took
    END_TS=$(date +%s)
    DURATION=$((END_TS - START_TS))
    
    # Sleep until the next 4-hour window (skip after final run)
    if [ "$i" -lt "$TOTAL_RUNS" ]; then
        # Calculate remaining time to sleep
        SLEEP_TIME=$((INTERVAL_SECONDS - DURATION))
        
        # Safety net: If the queue took longer than 4 hours, sleep for 0 seconds
        if [ "$SLEEP_TIME" -lt 0 ]; then
            SLEEP_TIME=0
            echo "⚠️ Warning: Run took longer than the 4-hour interval!"
        fi
        
        echo "✅ Finished Run $i in $DURATION seconds."
        echo "💤 Sleeping for $SLEEP_TIME seconds to maintain schedule..."
        sleep "$SLEEP_TIME"
    fi
done

echo ""
echo "=================================================="
echo "🎉 All 6 periodic runs completed at $(date)"
echo "=================================================="