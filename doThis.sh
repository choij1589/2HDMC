#!/bin/sh
mkdir -p outputs/type1
./Production 1 1
./Production 1 2
./Production 1 3
./Production 1 4
./Production 1 5

mkdir -p outputs/type2
./Production 2 1
./Production 2 2
./Production 2 3
./Production 2 4
./Production 2 5

mkdir -p outputs/type3
./Production 3 1
./Production 3 2
./Production 3 3
./Production 3 4
./Production 3 5

mkdir -p outputs/type4
./Production 4 1
./Production 4 2
./Production 4 3
./Production 4 4
./Production 4 5
