#!/bin/bash
type_values=(1 2 3 4)
tanb_values=(1 5 10 50)

for TYPE in "${type_values[@]}"; do
  for TANB in "${tanb_values[@]}"; do
    python plotHcDecay.py --type $TYPE --tanb $TANB --mHc 70
    python plotHcDecay.py --type $TYPE --tanb $TANB --mHc 100
    python plotHcDecay.py --type $TYPE --tanb $TANB --mHc 130
    python plotHcDecay.py --type $TYPE --tanb $TANB --mHc 160

  done
done

