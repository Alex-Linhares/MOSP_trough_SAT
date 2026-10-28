#!/bin/sh
# Builds grtd.bin (the PACE 2017 exact-track submission: `grtd -m 64`) and tw-exact.bin
# (Tamaki's 2016 PID solver, ported) without autotools.  Needs g++ and Boost headers;
# grtd also links boost_thread/boost_system.  Written 2026-10-28 against g++ 15.2 and the
# conda Boost 1.86; adjust BOOST to a different Boost prefix.  See ../README.md.
set -e
cd "$(dirname "$0")"
BOOST=${BOOST:-$HOME/anaconda3}
FLAGS="-std=gnu++11 -fnew-ttp-matching -O3 -march=native -fpermissive -include cstdint -w
       -I. -Iinc -Itdlib/src -Itdlib/grtd -I../stx-btree/include -I$BOOST/include
       -Dunreachable() -Dincomplete()"
g++ $FLAGS -DUSE_GALA tdlib/grtd/grtd.cc -o grtd.bin \
    -L$BOOST/lib -Wl,-rpath,$BOOST/lib -lboost_thread -lboost_system -lpthread
g++ $FLAGS tdlib/grtd/tw-exact.cc -o tw-exact.bin
./grtd.bin -m 64 < tdlib/grtd/HoffmanGraph.gr 2>/dev/null | grep -q "^s td [0-9]* 7 16" && echo "grtd ok (Hoffman graph: treewidth 6)"
./tw-exact.bin < tdlib/grtd/HoffmanGraph.gr 2>/dev/null | grep -q "^s td 11 7 16" && echo "tw-exact ok"
