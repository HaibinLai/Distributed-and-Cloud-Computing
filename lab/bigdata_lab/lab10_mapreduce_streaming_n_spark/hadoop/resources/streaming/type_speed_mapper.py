#!/usr/bin/python
import sys

sys.stdin.readline()  # drop title

for line in sys.stdin:
    line = line.strip().split(',')
    poke_type, speed = line[2], line[-3]
    print (poke_type + "\t" + speed)