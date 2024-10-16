#!/bin/sh
TYPE=$1

python plotting.py --type $TYPE --tanb 1 --mHc 70
python plotting.py --type $TYPE --tanb 5 --mHc 70
python plotting.py --type $TYPE --tanb 10 --mHc 70
python plotting.py --type $TYPE --tanb 50 --mHc 70
python plotting.py --type $TYPE --tanb 1 --mHc 100
python plotting.py --type $TYPE --tanb 5 --mHc 100
python plotting.py --type $TYPE --tanb 10 --mHc 100
python plotting.py --type $TYPE --tanb 50 --mHc 100
python plotting.py --type $TYPE --tanb 1 --mHc 130
python plotting.py --type $TYPE --tanb 5 --mHc 130
python plotting.py --type $TYPE --tanb 10 --mHc 130
python plotting.py --type $TYPE --tanb 50 --mHc 130
python plotting.py --type $TYPE --tanb 1 --mHc 160
python plotting.py --type $TYPE --tanb 5 --mHc 160
python plotting.py --type $TYPE --tanb 10 --mHc 160
python plotting.py --type $TYPE --tanb 50 --mHc 160
