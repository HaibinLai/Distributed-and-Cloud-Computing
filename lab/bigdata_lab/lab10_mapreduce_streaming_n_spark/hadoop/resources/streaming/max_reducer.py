#!/usr/bin/python

import sys

KVs = {}

for line in sys.stdin:
    key, value = line.split('\t')

    value = int(value)

    current_max = KVs.get(key, None)

    if current_max is None or current_max < value:
        KVs[key] = value

for key, count in KVs.items():
    print(key + ' ' + str(count)) 



