#!/bin/bash
# Run ScanBR for all 4 types × 10 tanβ values (40 jobs)
# Uses xargs for parallelization

set -e
mkdir -p outputs

for type in 1 2 3 4; do
    for tanb in $(seq 1 10); do
        echo "$type $tanb"
    done
done | xargs -P 4 -n 2 bash -c './bin/ScanBR "$0" "$1"'

echo "All scans complete."
