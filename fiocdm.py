#!/usr/bin/python
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Michael Ortmann

import os
import subprocess
import sys

tests = ((0, "1M",    8,  1), # SEQ|RND, bs, iodepth, numjobs
         (0, "1M",    1,  1),
         (1, "512K",  1,  1),
         (1, "4K",   32, 16),
         (1, "4K",    1,  1))

if len(sys.argv) != 2:
    print("Usage: %s <path>" % sys.argv[0])
    sys.exit(os.EX_USAGE)

filename = "%s/.fiocdm.dat" % sys.argv[1]
args = ["fio",
        "--direct=1",
        "--filename=%s" % filename,
        "--ioengine=libaio",
        "--loops=5",
        "--output-format=json",
        "--runtime=5",
        "--size=1g",
        "--stonewall",
        "--time_based=1"]
rws = (("SEQ", "read", "write"), ("RND", "randread", "randwrite"))

for t in tests:
    for rw in rws[t[0]][1:]:
        args.append("--name=%s%sQ%iT%i" % (rws[t[0]][0], t[1], t[2], t[3]))
        args.append("--bs=%s" % t[1])
        args.append("--iodepth=%s" % t[2])
        args.append("--numjobs=%i" % t[3])
        args.append("--rw=%s" % rw)

p = subprocess.Popen(args, stdout=subprocess.PIPE)
stdout = p.stdout.read().decode(sys.stdout.encoding)
r = []

for t in tests:
    for rw in rws[t[0]][1:]:
        x = 0

        for i in range(0, t[3]):
            stdout = stdout[stdout.find("jobname"):]

            if rw.startswith("rand"):
                rw = rw[4:]

            stdout = stdout[stdout.find("%s\" " % rw):]
            stdout = stdout[stdout.find("bw\" : "):]
            x += float(stdout[6:stdout.find(",")])

        r.append(x / 1024)

print("            Read [MB/s] Write [MB/s]")
i = 0

for t in tests:
    n = "%s%sQ%iT%i" %  (rws[t[0]][0], t[1], t[2], t[3]) 
    print("%-11s %11.3f %12.3f" % (n, r[i], r[i + 1]))
    i += 2

os.unlink(filename)
