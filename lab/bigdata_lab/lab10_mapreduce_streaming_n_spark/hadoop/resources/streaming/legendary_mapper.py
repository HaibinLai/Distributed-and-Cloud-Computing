#!/usr/bin/python

import sys

sys.stdin.readline() # drop tittle

for line in sys.stdin:
    line = line.strip().split(',')
    poke_type, is_legendary = line[2], line[-1]
    if is_legendary == "True":
        print(poke_type + "\t1")