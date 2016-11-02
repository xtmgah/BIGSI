#! /usr/bin/env python
import time
import sys
import os
import random
sys.path.append(
    os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            "..")))
sys.path.append(
    os.path.realpath(
        os.path.join(
            os.path.dirname(__file__),
            "../redis-py")))
from atlasseq import ProbabilisticMultiColourDeBruijnGraph as Graph


keys = []
N = 1000
with open('scripts/ERR1095101_1000000.txt', 'r') as infile:
    keys.extend(infile.read().splitlines()[:N])

for storage in [{'dict': None}, {'berkeleydb': {'filename': './db'}},
                {"redis": {
                    "conn": [('localhost', 6379, 2)]}}
                ]:
    sname = [k for k in storage.keys()][0]
    mc = Graph(storage=storage)
    mc.delete_all()
    c = 3
    start = time.time()
    for i in range(c):
        mc.insert(keys, str(i))
    end = time.time()
    print("insert %s - %i %i colours" % (sname, N, c), end-start)
    start = time.time()
    vals = mc.lookup(keys)
    end = time.time()
    print("get %s - %i" % (sname, N), end-start)
    start = time.time()
    vals = mc.search(keys[0])
    end = time.time()
    print("query %s - %i" % (sname, N), end-start)
