"""Graphs for `paper2/better_hunt.c` (loop0006 item 10): the definite move's two
counterexample graphs (`DEFINITE_CEX` in `paper2/search_check.py`), plus up to four extra
vertices (two on the 16-vertex one) with 1-4 random edges each, up to two edge flips, and a
random relabelling, so that the index order the better move uses cannot see the construction.

    python3 paper2/better_hunt_gen.py SEED COUNT | /tmp/better_hunt

Item 10 ran seeds 101-128 with COUNT 400 (11,200 graphs, 14-18 vertices) under MODE=0 and
MODE=2; and, with only the 14-vertex graph and up to three extra vertices, seeds 1-30 with
COUNT 150 (4,500 graphs).
"""
import sys, random
rng=random.Random(int(sys.argv[1])); cnt=int(sys.argv[2])
BASES=[[2201,102,30,13,21,6690,8514,9857,3904,4000,16256,3873,13344,13504],[18459,103,286,13,21,60578,8770,60320,7044,20416,7712,44961,13568,30944,58017,51360]]
for _ in range(cnt):
    base=rng.choice(BASES); n0=len(base); extra=rng.randint(0,4 if n0==14 else 2); n=n0+extra
    ms=list(base)+[0]*extra
    for i in range(n): ms[i]|=1<<i
    for v in range(n0,n):
        for u in rng.sample(range(v),rng.randint(1,4)):
            ms[v]|=1<<u; ms[u]|=1<<v
    # random edge flips
    for _ in range(rng.randint(0,2)):
        u,v=rng.sample(range(n),2)
        ms[u]^=1<<v; ms[v]^=1<<u
    p=list(range(n)); rng.shuffle(p)
    out=[0]*n
    for v in range(n):
        mm=0
        for u in range(n):
            if ms[v]>>u&1: mm|=1<<p[u]
        out[p[v]]=mm
    print(n,*out)
