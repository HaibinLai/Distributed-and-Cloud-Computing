#!/usr/bin/python

import sys

sys.stdin.readline() # drop tittle

for line in sys.stdin:
    line = line.strip().split(',')
    poke_type = line[2]
    print(poke_type + "\t1")