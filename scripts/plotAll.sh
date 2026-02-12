#!/bin/bash
# Generate all plots from CSV scan outputs

set -e

for type in 1 2 3 4; do
    for tanb in $(seq 1 10); do
        csv="outputs/scan_type${type}_tanb${tanb}.csv"
        if [ -f "$csv" ]; then
            echo "Plotting type=$type tanb=$tanb"
            python3 scripts/plotBR.py --type "$type" --tanb "$tanb"
            python3 scripts/plot2D.py --type "$type" --tanb "$tanb"
        else
            echo "SKIP: $csv not found"
        fi
    done
    echo "Plotting TopBR for type=$type"
    python3 scripts/plotTopBR.py --type "$type"
done

echo "All plots done."
