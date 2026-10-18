# pathwidth -- standalone exact pathwidth for graph6 input. MIT licence (see pathwidth.c).
#
#   make            build ./pathwidth
#   make test       unit tests against known values (tests/unit.sh)
#   make check-engine   confirm closing_search_w.c is still the solver's engine, byte for byte

CC      ?= gcc
CFLAGS  ?= -O2
# The search is popcount-bound: without a hardware popcount it runs ~1.8x
# slower. `make ARCH=` builds a portable binary; `make ARCH=-mpopcnt` keeps the
# instruction without tuning for this CPU.
ARCH    ?= -march=native
WARN    = -std=c99 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -pedantic
ENGINE_WORDS = 2 4 8 16
ENGINE_OBJS = $(foreach W,$(ENGINE_WORDS),engine_w$(W).o)

all: pathwidth

pathwidth: pathwidth.o $(ENGINE_OBJS)
	$(CC) $(CFLAGS) $(ARCH) -o $@ $^ -lm

pathwidth.o: pathwidth.c engine.h
	$(CC) $(CFLAGS) $(ARCH) $(WARN) -c -o $@ pathwidth.c

engine_w%.o: engine.c closing_search_w.c
	$(CC) $(CFLAGS) $(ARCH) $(WARN) -DWORDS=$* -Dcsw_decide=csw_decide_$* -Dcsw_words=csw_words_$* -c -o $@ engine.c

test: pathwidth
	sh tests/unit.sh

check-engine:
	cmp closing_search_w.c ../pathwidth/closing_search_w.c && echo "engine identical to ../pathwidth/closing_search_w.c"

clean:
	rm -f pathwidth pathwidth.o $(ENGINE_OBJS)

.PHONY: all test check-engine clean
