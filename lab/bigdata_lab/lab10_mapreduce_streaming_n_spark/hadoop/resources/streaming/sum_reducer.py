#!/usr/bin/python

import sys

KVs = {}

for line in sys.stdin:
    key, count = line.split('\t')
    KVs[key] = KVs.get(key, 0) + int(count)

for key, count in KVs.items():
    print(key + ' ' + str(count))



