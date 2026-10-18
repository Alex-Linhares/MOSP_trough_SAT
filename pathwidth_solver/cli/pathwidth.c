/* pathwidth -- exact pathwidth of graphs in graph6 format.
 *
 * MIT License
 *
 * Copyright (c) 2026 Alexandre Linhares
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * A port of the Python solver in ../pathwidth/ (solve.py, bounds.py,
 * minor.py) around its C search engine (closing_search_w.c, included
 * verbatim through engine.c). Each function below names the Python function
 * it ports; the bit-level semantics (tie-breaks, rounding, budgets) are the
 * Python's, so the descent visits the same widths in the same order.
 *
 * Conventions, as in the Python. A *closing order* is a sequence of vertices;
 * for a prefix U its boundary is |N(U) \ U|, and the order's width is the
 * largest boundary. The engine's decide(masks, k) answers "is there a closing
 * order of width <= k - 1?". The printed layout is the closing order
 * reversed, which is a layout in the textbook sense (the number of vertices
 * at or before position i with a neighbour after i is at most the width).
 */

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "engine.h"

#define ENGINE_MAX_VERTICES 1024     /* 16 x 64-bit words, as native.py */

/* ---- utilities --------------------------------------------------------- */

static void fatal(const char *msg) {
    fprintf(stderr, "pathwidth: internal error: %s\n", msg);
    exit(2);
}

static void *xmalloc(size_t size) {
    void *p = malloc(size ? size : 1);
    if (!p) fatal("out of memory");
    return p;
}

static void *xcalloc(size_t count, size_t size) {
    void *p = calloc(count ? count : 1, size ? size : 1);
    if (!p) fatal("out of memory");
    return p;
}

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double) ts.tv_sec + (double) ts.tv_nsec * 1e-9;
}

#define NO_DEADLINE (-1.0)
#define NO_LIMIT (-1LL)

/* ---- bitsets ----------------------------------------------------------- */

/* A graph on vertices 0..n-1 as self-inclusive neighbourhood masks, nw words
 * each (masks_from_graph). */
typedef struct {
    int n, nw;
    uint64_t *m;                 /* m[v * nw .. v * nw + nw - 1] = N[v] */
} graph;

static inline uint64_t *row(const graph *g, int v) { return g->m + (size_t) v * (size_t) g->nw; }
static inline int bs_test(const uint64_t *a, int i) { return (int) ((a[i >> 6] >> (i & 63)) & 1); }
static inline void bs_set(uint64_t *a, int i) { a[i >> 6] |= (uint64_t) 1 << (i & 63); }
static inline void bs_clear(uint64_t *a, int i) { a[i >> 6] &= ~((uint64_t) 1 << (i & 63)); }
static inline int bs_count(const uint64_t *a, int nw) {
    int c = 0;
    for (int i = 0; i < nw; i++) c += __builtin_popcountll(a[i]);
    return c;
}
static inline int bs_any(const uint64_t *a, int nw) {
    for (int i = 0; i < nw; i++) if (a[i]) return 1;
    return 0;
}
/* lowest set bit at or after `from`, or -1 */
static inline int bs_next(const uint64_t *a, int nw, int from) {
    if (from < 0) from = 0;
    int i = from >> 6;
    if (i >= nw) return -1;
    uint64_t w = a[i] & (~(uint64_t) 0 << (from & 63));
    while (1) {
        if (w) return 64 * i + __builtin_ctzll(w);
        if (++i >= nw) return -1;
        w = a[i];
    }
}
#define BS_FOR(v, a, nw) for (int v = bs_next((a), (nw), 0); v >= 0; v = bs_next((a), (nw), v + 1))

static graph graph_new(int n) {
    graph g;
    g.n = n;
    g.nw = n > 0 ? (n + 63) / 64 : 1;
    g.m = xcalloc((size_t) (n > 0 ? n : 1) * (size_t) g.nw, sizeof(uint64_t));
    return g;
}

static void graph_free(graph *g) { free(g->m); g->m = NULL; }

/* ---- the engine -------------------------------------------------------- */

#define SAT 1
#define UNSAT 0
#define UNKNOWN (-1)

static long long engine_calls = 0;

/* search.decide -> native.decide_native with the solver's default flags:
 * subset rule, definite move, old move and memo on, better move off,
 * dominators 4, fan order "index", memo_limit 4,000,000, repaired rules on.
 * `order` receives the closing order on SAT (n entries). */
static int decide(const graph *g, int k, int restrict_frontier, long long max_nodes,
                  double deadline, int *order, long long *nodes) {
    *nodes = 0;
    int n = g->n;
    if (n <= 0) return SAT;
    int words = n <= 128 ? 2 : n <= 256 ? 4 : n <= 512 ? 8 : n <= 1024 ? 16 : 0;
    if (!words) fatal("decide called on more than 1024 vertices");
    uint64_t *packed = xcalloc((size_t) n * (size_t) words, sizeof(uint64_t));
    for (int v = 0; v < n; v++)
        for (int w = 0; w < g->nw; w++) packed[(size_t) v * words + w] = row(g, v)[w];
    /* The Python passes max(0, deadline - now) seconds, and the engine reads
     * 0 as "no deadline", so a call made after its deadline would run without
     * one. The smallest positive budget is used instead: the engine then
     * stops at its first clock check (every 4,096 nodes), which is what the
     * deadline means. */
    double seconds = 0.0;
    if (deadline != NO_DEADLINE) {
        seconds = deadline - now();
        if (seconds < 1e-9) seconds = 1e-9;
    }
    int len = 0, status;
    int *path = xmalloc(sizeof(int) * (size_t) n);
    switch (words) {
#define CALL(W) status = csw_decide_##W(n, k, packed, max_nodes, seconds, 1, 1, 1, restrict_frontier, \
                                        4000000, 0, 4, 1, 0, 0, 1, path, nodes, &len); break
    case 2: CALL(2);
    case 4: CALL(4);
    case 8: CALL(8);
    default: CALL(16);
#undef CALL
    }
    free(packed);
    engine_calls++;
    if (status == -2 || status == -3) fatal("search engine: allocation failure");
    int answer;
    if (status == 1) {
        if (len != n) fatal("search engine returned a partial order");
        memcpy(order, path, sizeof(int) * (size_t) n);
        answer = SAT;
    } else if (status == 0) {
        answer = restrict_frontier ? UNKNOWN : UNSAT;
    } else {
        answer = UNKNOWN;
    }
    free(path);
    return answer;
}

/* ---- measures (graph.py) ----------------------------------------------- */

/* vertex_separation_masks: the largest prefix boundary of a closing order.
 * Also checks that `order` is a permutation of 0..n-1. */
static int vertex_separation(const graph *g, const int *order) {
    int nw = g->nw, peak = 0;
    uint64_t *opened = xcalloc((size_t) nw, sizeof(uint64_t));
    uint64_t *closed = xcalloc((size_t) nw, sizeof(uint64_t));
    for (int i = 0; i < g->n; i++) {
        int v = order[i];
        if (v < 0 || v >= g->n || bs_test(closed, v)) fatal("order is not a permutation");
        const uint64_t *r = row(g, v);
        for (int w = 0; w < nw; w++) opened[w] |= r[w];
        bs_set(closed, v);
        int width = 0;
        for (int w = 0; w < nw; w++) width += __builtin_popcountll(opened[w] & ~closed[w]);
        if (width > peak) peak = width;
    }
    free(opened);
    free(closed);
    return peak;
}

/* ---- bounds (bounds.py) ------------------------------------------------ */

/* greedy_order: close the vertex leaving the smallest boundary, ties by index. */
static void greedy_order(const graph *g, int *order) {
    int n = g->n, nw = g->nw;
    uint64_t *opened = xcalloc((size_t) nw, sizeof(uint64_t));
    uint64_t *closed = xcalloc((size_t) nw, sizeof(uint64_t));
    for (int step = 0; step < n; step++) {
        int best_v = -1, best_w = n + 1;
        for (int v = 0; v < n; v++) {
            if (bs_test(closed, v)) continue;
            const uint64_t *r = row(g, v);
            int w = 0;
            for (int i = 0; i < nw; i++) w += __builtin_popcountll((opened[i] | r[i]) & ~closed[i]);
            w -= 1;                          /* v itself: in N[v], not yet closed */
            if (w < best_w) { best_w = w; best_v = v; }
        }
        order[step] = best_v;
        bs_set(closed, best_v);
        const uint64_t *r = row(g, best_v);
        for (int i = 0; i < nw; i++) opened[i] |= r[i];
    }
    free(opened);
    free(closed);
}

/* degeneracy: repeatedly delete a minimum-degree vertex (ties by index). */
static int degeneracy(const graph *g) {
    int n = g->n, nw = g->nw, best = 0;
    uint64_t *alive = xcalloc((size_t) nw, sizeof(uint64_t));
    for (int v = 0; v < n; v++) if (bs_any(row(g, v), nw)) bs_set(alive, v);
    while (bs_any(alive, nw)) {
        int best_v = -1, best_d = n + 1;
        BS_FOR(v, alive, nw) {
            const uint64_t *r = row(g, v);
            int d = 0;
            for (int i = 0; i < nw; i++) d += __builtin_popcountll(r[i] & alive[i]);
            d -= 1;                          /* masks are self-inclusive */
            if (d < best_d) { best_d = d; best_v = v; }
        }
        if (best_d > best) best = best_d;
        bs_clear(alive, best_v);
    }
    free(alive);
    return best;
}

/* contraction_degeneracy (MMD+, least-c), degeneracy above 400 vertices. */
static int contraction_degeneracy(const graph *g) {
    int n = g->n, nw = g->nw;
    if (n > 400) return degeneracy(g);
    uint64_t *adj = xmalloc(sizeof(uint64_t) * (size_t) n * (size_t) nw);
    memcpy(adj, g->m, sizeof(uint64_t) * (size_t) n * (size_t) nw);
    uint64_t *alive = xcalloc((size_t) nw, sizeof(uint64_t));
    uint64_t *nbrs = xcalloc((size_t) nw, sizeof(uint64_t));
    for (int v = 0; v < n; v++) {
        if (bs_any(row(g, v), nw)) bs_set(alive, v);
        bs_clear(adj + (size_t) v * nw, v);
    }
    int best = 0;
    while (bs_count(alive, nw) > 1) {
        int best_v = -1, best_d = n + 1;
        BS_FOR(v, alive, nw) {
            const uint64_t *a = adj + (size_t) v * nw;
            int d = 0;
            for (int i = 0; i < nw; i++) d += __builtin_popcountll(a[i] & alive[i]);
            if (d < best_d) { best_d = d; best_v = v; }
        }
        if (best_d > best) best = best_d;
        int v = best_v;
        uint64_t *av = adj + (size_t) v * nw;
        for (int i = 0; i < nw; i++) nbrs[i] = av[i] & alive[i];
        if (!bs_any(nbrs, nw)) { bs_clear(alive, v); continue; }
        int u = -1, fewest = n + 1;
        BS_FOR(c, nbrs, nw) {
            const uint64_t *ac = adj + (size_t) c * nw;
            int common = 0;
            for (int i = 0; i < nw; i++) common += __builtin_popcountll(ac[i] & nbrs[i]);
            if (common < fewest) { fewest = common; u = c; }
        }
        uint64_t *au = adj + (size_t) u * nw;
        for (int i = 0; i < nw; i++) au[i] |= av[i];
        bs_clear(au, u);
        bs_clear(au, v);
        BS_FOR(w, au, nw) {
            if (!bs_test(alive, w)) continue;
            uint64_t *aw = adj + (size_t) w * nw;
            bs_set(aw, u);
            bs_clear(aw, v);
        }
        bs_clear(alive, v);
    }
    free(adj);
    free(alive);
    free(nbrs);
    return best;
}

/* lower_bound */
static int lower_bound(const graph *g) {
    int any = 0;
    for (int v = 0; v < g->n && !any; v++) any = bs_any(row(g, v), g->nw);
    if (!any) return 0;
    int a = degeneracy(g), b = contraction_degeneracy(g);
    return a > b ? a : b;
}

/* solve.initial_upper_bound: greedy, then the restricted search (ub_MOSP)
 * with 20,000 nodes per call while it improves. */
static long long upper_nodes = 0;
static int initial_upper_bound(const graph *g, int *order) {
    int n = g->n;
    greedy_order(g, order);
    int width = vertex_separation(g, order);
    int *found_order = xmalloc(sizeof(int) * (size_t) n);
    while (width > 0) {
        long long nodes;
        int st = decide(g, width, 1, 20000, NO_DEADLINE, found_order, &nodes);
        upper_nodes += nodes;
        if (st != SAT) break;
        int found = vertex_separation(g, found_order);
        if (found >= width) break;
        width = found;
        memcpy(order, found_order, sizeof(int) * (size_t) n);
    }
    free(found_order);
    return width;
}

/* ---- the contraction-minor step (minor.py) ----------------------------- */

/* MinorConfig() defaults */
#define CFG_MIN_VERTICES 40
#define CFG_START_FRACTION 0.5
#define CFG_STEP_FRACTION 0.05
#define CFG_MAX_FRACTION 0.85
#define CFG_FIRST_NODES 100000.0
#define CFG_GROWTH 3.0
#define CFG_TOTAL_NODES 20000000LL
#define CFG_TIME_FRACTION 0.25
#define CFG_PROBE_NODES 100000LL
#define CFG_SHARE 0.5
#define CFG_RESTRICT_NODES 20000LL
/* on_stall = "retry"; rules = ("min-d", "least-c") */
#define RULE_MIN_D 0
#define RULE_LEAST_C 1

/* MinorConfig.sizes: Python's round() is round-half-even on the double,
 * which is what nearbyint does in the default rounding mode. */
static int config_sizes(int n, int w, int *out) {
    int lo = (int) ceil(CFG_START_FRACTION * n);
    if (w + 2 > lo) lo = w + 2;
    int hi = (int) (CFG_MAX_FRACTION * n);
    int step = (int) nearbyint(CFG_STEP_FRACTION * n);
    if (step < 2) step = 2;
    int count = 0;
    for (int m = lo; m <= hi && m < n; m += step) out[count++] = m;
    return count;
}

/* _contract: v into u, or delete v when u == -1, on open neighbourhoods. */
static void contract(uint64_t *adj, int nw, uint64_t *alive, int v, int u) {
    uint64_t *av = adj + (size_t) v * nw;
    if (u >= 0) {
        uint64_t *au = adj + (size_t) u * nw;
        for (int i = 0; i < nw; i++) au[i] |= av[i];
        bs_clear(au, u);
        bs_clear(au, v);
        BS_FOR(w, au, nw) {
            uint64_t *aw = adj + (size_t) w * nw;
            bs_set(aw, u);
            bs_clear(aw, v);
        }
    } else {
        BS_FOR(w, av, nw) bs_clear(adj + (size_t) w * nw, v);
    }
    memset(av, 0, sizeof(uint64_t) * (size_t) nw);
    bs_clear(alive, v);
}

static uint64_t *open_neighbourhoods(const graph *g, uint64_t *alive) {
    int n = g->n, nw = g->nw;
    uint64_t *adj = xmalloc(sizeof(uint64_t) * (size_t) n * (size_t) nw);
    memcpy(adj, g->m, sizeof(uint64_t) * (size_t) n * (size_t) nw);
    memset(alive, 0, sizeof(uint64_t) * (size_t) nw);
    for (int v = 0; v < n; v++) {
        bs_clear(adj + (size_t) v * nw, v);
        if (bs_any(row(g, v), nw)) bs_set(alive, v);
    }
    return adj;
}

/* contraction_sequence: greedy contractions down to `size` active vertices.
 * Writes (v, u) pairs into seq (2 ints each); returns the number of pairs. */
static int contraction_sequence(const graph *g, int size, int rule, int *seq) {
    int n = g->n, nw = g->nw, len = 0;
    uint64_t *alive = xcalloc((size_t) nw, sizeof(uint64_t));
    uint64_t *adj = open_neighbourhoods(g, alive);
    if (size < 0) size = 0;
    while (bs_count(alive, nw) > size) {
        int best_v = -1, best_d = n + 1;
        BS_FOR(x, alive, nw) {
            int d = bs_count(adj + (size_t) x * nw, nw);
            if (d < best_d) { best_d = d; best_v = x; }
        }
        int v = best_v;
        const uint64_t *nb = adj + (size_t) v * nw;
        int u = -1, best = 0, have = 0;
        BS_FOR(c, nb, nw) {
            const uint64_t *ac = adj + (size_t) c * nw;
            int score = 0;
            if (rule == RULE_MIN_D) score = bs_count(ac, nw);
            else for (int i = 0; i < nw; i++) score += __builtin_popcountll(ac[i] & nb[i]);
            if (!have || score < best) { have = 1; best = score; u = c; }
        }
        seq[2 * len] = v;
        seq[2 * len + 1] = u;
        len++;
        contract(adj, nw, alive, v, u);
    }
    free(adj);
    free(alive);
    return len;
}

/* replay: apply a contraction sequence, checking each pair is an edge (or an
 * isolated deletion) of the current graph, and return the minor over
 * 0..m-1, labels[i] = the graph vertex minor vertex i kept, and root[x] = the
 * minor vertex whose branch set holds x (-1 if x was deleted). */
static graph replay(const graph *g, const int *seq, int len, int **labels_out, int **root_out) {
    int n = g->n, nw = g->nw;
    uint64_t *alive = xcalloc((size_t) nw, sizeof(uint64_t));
    uint64_t *adj = open_neighbourhoods(g, alive);
    int *owner = xmalloc(sizeof(int) * (size_t) n);           /* branch-set representative */
    for (int x = 0; x < n; x++) owner[x] = bs_test(alive, x) ? x : -1;
    for (int s = 0; s < len; s++) {
        int v = seq[2 * s], u = seq[2 * s + 1];
        if (v < 0 || v >= n || !bs_test(alive, v)) fatal("replay: a contracted vertex is not in the graph");
        if (u == -1) {
            if (bs_any(adj + (size_t) v * nw, nw)) fatal("replay: deleting a vertex that is not isolated");
            for (int x = 0; x < n; x++) if (owner[x] == v) owner[x] = -1;
        } else {
            if (u < 0 || u >= n || !bs_test(alive, u) || !bs_test(adj + (size_t) v * nw, u))
                fatal("replay: a contraction is not an edge of the current graph");
            for (int x = 0; x < n; x++) if (owner[x] == v) owner[x] = u;
        }
        contract(adj, nw, alive, v, u);
    }
    int m = bs_count(alive, nw);
    int *labels = xmalloc(sizeof(int) * (size_t) (m ? m : 1));
    int *index = xmalloc(sizeof(int) * (size_t) n);
    int i = 0;
    for (int x = 0; x < n; x++) index[x] = -1;
    BS_FOR(x, alive, nw) { labels[i] = x; index[x] = i; i++; }
    graph minor = graph_new(m);
    for (i = 0; i < m; i++) {
        uint64_t *r = row(&minor, i);
        bs_set(r, i);
        BS_FOR(y, adj + (size_t) labels[i] * nw, nw) bs_set(r, index[y]);
    }
    int *root = xmalloc(sizeof(int) * (size_t) n);
    for (int x = 0; x < n; x++) root[x] = owner[x] >= 0 ? index[owner[x]] : -1;
    free(adj);
    free(alive);
    free(owner);
    free(index);
    *labels_out = labels;
    *root_out = root;
    return minor;
}

/* One (rule, size) entry of the ladder's dictionaries. */
typedef struct {
    int rule, size;
    int has_upper, upper;        /* _upper */
    int refuted;                 /* _refuted, -1 when absent */
    int restricted;              /* _restricted, n + 1 when absent */
    int cheap_done;
    graph minor;
    int *labels, *root;
} entry;

typedef struct {
    const graph *g;
    int n;
    long long nodes;
    double seconds;
    int *seq[2];
    int seq_len[2];
    entry *entries;
    int count, capacity;
    int best_refuted;            /* best.refuted, -1 when best is None */
    int best_size, best_rule;
} ladder;

static void ladder_init(ladder *L, const graph *g) {
    memset(L, 0, sizeof *L);
    L->g = g;
    L->n = g->n;                 /* every vertex of a component is active */
    L->best_refuted = -1;
    L->seq_len[0] = L->seq_len[1] = -1;
}

static void ladder_free(ladder *L) {
    for (int i = 0; i < L->count; i++) {
        graph_free(&L->entries[i].minor);
        free(L->entries[i].labels);
        free(L->entries[i].root);
    }
    free(L->entries);
    free(L->seq[0]);
    free(L->seq[1]);
}

static int ladder_applies(const ladder *L) { return L->n >= CFG_MIN_VERTICES; }

/* MinorLadder.minor (with _sequence): the minor of `size` vertices. */
static entry *ladder_minor(ladder *L, int rule, int size) {
    for (int i = 0; i < L->count; i++)
        if (L->entries[i].rule == rule && L->entries[i].size == size) return &L->entries[i];
    int need = L->n - size;
    if (L->seq_len[rule] < need) {
        /* min(size, min(sizes(n, 0) or [size])) */
        int sizes[64], c = config_sizes(L->n, 0, sizes), smallest = size;
        for (int i = 0; i < c; i++) if (sizes[i] < smallest) smallest = sizes[i];
        free(L->seq[rule]);
        L->seq[rule] = xmalloc(sizeof(int) * 2 * (size_t) (L->n + 1));
        L->seq_len[rule] = contraction_sequence(L->g, smallest, rule, L->seq[rule]);
    }
    if (need > L->seq_len[rule]) need = L->seq_len[rule];
    if (L->count == L->capacity) {
        L->capacity = L->capacity ? 2 * L->capacity : 16;
        L->entries = realloc(L->entries, sizeof(entry) * (size_t) L->capacity);
        if (!L->entries) fatal("out of memory");
    }
    entry *e = &L->entries[L->count++];
    memset(e, 0, sizeof *e);
    e->rule = rule;
    e->size = size;
    e->refuted = -1;
    e->restricted = L->n + 1;
    e->minor = replay(L->g, L->seq[rule], need, &e->labels, &e->root);
    return e;
}

static int graph_equal(const graph *a, const graph *b) {
    return a->n == b->n && a->nw == b->nw &&
           memcmp(a->m, b->m, sizeof(uint64_t) * (size_t) a->n * (size_t) a->nw) == 0;
}

/* MinorLadder._decide (and the inline decide of try_refute): one engine call
 * on a minor, its nodes counted. */
static int ladder_decide(ladder *L, entry *e, int k, long long budget, double deadline,
                         int restrict_frontier, int *order) {
    long long nodes;
    double t0 = now();
    int st = decide(&e->minor, k, restrict_frontier, budget, deadline, order, &nodes);
    L->nodes += nodes;
    L->seconds += now() - t0;
    return st;
}

/* MinorLadder.cheap_width: greedy on the minor, and the descent's order lifted. */
static int cheap_width(entry *e, const int *order, int n) {
    int m = e->minor.n;
    int *o = xmalloc(sizeof(int) * (size_t) (m ? m : 1));
    greedy_order(&e->minor, o);
    int best = vertex_separation(&e->minor, o);
    if (order) {
        int *last = xmalloc(sizeof(int) * (size_t) (m ? m : 1));
        for (int i = 0; i < m; i++) last[i] = -1;
        for (int p = 0; p < n; p++) {
            int r = e->root[order[p]];
            if (r >= 0 && p > last[r]) last[r] = p;
        }
        /* sorted(range(m), key=last): stable insertion sort */
        for (int i = 0; i < m; i++) o[i] = i;
        for (int i = 1; i < m; i++) {
            int x = o[i], j = i - 1;
            while (j >= 0 && last[o[j]] > last[x]) { o[j + 1] = o[j]; j--; }
            o[j + 1] = x;
        }
        int lifted = vertex_separation(&e->minor, o);
        if (lifted < best) best = lifted;
        free(last);
    }
    free(o);
    return best;
}

static int deadline_passed(double deadline) { return deadline != NO_DEADLINE && now() >= deadline; }

/* MinorLadder.try_refute: 1 if some minor refutes width w (pw(G) >= w + 1). */
static int try_refute(ladder *L, int w, double deadline, long long max_nodes, const int *order) {
    int n = L->n;
    if (n < CFG_MIN_VERTICES) return 0;
    double budget = CFG_FIRST_NODES;
    long long left = CFG_TOTAL_NODES - L->nodes;
    long long cap = L->nodes + (long long) (CFG_SHARE * (double) (left > 0 ? left : 0));
    int sizes[64], nsizes = config_sizes(n, w, sizes);
    int *scratch = xmalloc(sizeof(int) * (size_t) n);
    int i = 0, result = 0;
    while (i < nsizes) {
        int size = sizes[i], stalled = 0, asked = 0;
        int first = -1;          /* index, not pointer: ladder_minor may realloc */
        for (int rule = 0; rule < 2; rule++) {
            entry *e = ladder_minor(L, rule, size);
            if (first >= 0 && graph_equal(&L->entries[first].minor, &e->minor)) continue;   /* same minor */
            if (first < 0) first = (int) (e - L->entries);
            if ((e->has_upper ? e->upper : n) <= w) continue;
            if (!e->cheap_done) {
                e->cheap_done = 1;
                int cheap = cheap_width(e, order, n);
                int up = e->has_upper ? e->upper : n;
                e->upper = cheap < up ? cheap : up;
                e->has_upper = 1;
                if (cheap <= w) continue;
            }
            long long remaining = cap - L->nodes;
            if (max_nodes != NO_LIMIT && max_nodes < remaining) remaining = max_nodes;
            if (remaining <= 0 || deadline_passed(deadline)) goto done;
            if (CFG_RESTRICT_NODES && e->restricted > w) {
                e->restricted = w;
                long long b = CFG_RESTRICT_NODES < remaining ? CFG_RESTRICT_NODES : remaining;
                if (ladder_decide(L, e, w + 1, b, deadline, 1, scratch) == SAT) {
                    e->upper = vertex_separation(&e->minor, scratch);
                    e->has_upper = 1;
                    continue;
                }
            }
            asked++;
            double cut = budget < (double) remaining ? budget : (double) remaining;
            int st = ladder_decide(L, e, w + 1, (long long) cut, deadline, 0, scratch);
            if (st == UNSAT) {
                if (w > e->refuted) e->refuted = w;
                if (L->best_refuted < 0 || w > L->best_refuted) {
                    L->best_refuted = w;
                    L->best_size = size;
                    L->best_rule = rule;
                }
                result = 1;
                goto done;
            }
            if (st == SAT) {
                e->upper = vertex_separation(&e->minor, scratch);
                e->has_upper = 1;
            } else {
                stalled++;
            }
        }
        budget *= CFG_GROWTH;
        if (asked && stalled == asked) continue;    /* on_stall = "retry": same size, bigger budget */
        i++;
    }
done:
    free(scratch);
    return result;
}

/* MinorLadder.raise_lower: prove minors' exact pathwidth. Returns best.refuted
 * if best.refuted + 1 > lower, else -1. */
static int raise_lower(ladder *L, int lower, double deadline, long long max_nodes) {
    long long left = CFG_TOTAL_NODES - L->nodes;
    long long cap = L->nodes + (long long) (CFG_SHARE * (double) (left > 0 ? left : 0));
    int best = L->best_refuted;
    int floor_ = best >= 0 && best + 1 > lower ? best + 1 : lower;
    /* sorted((size, rule) for (rule, size) in _upper): by size, then by the
     * rule's name, "least-c" < "min-d" */
    int count = 0;
    int *keys = xmalloc(sizeof(int) * (size_t) (L->count ? L->count : 1));
    for (int i = 0; i < L->count; i++) if (L->entries[i].has_upper) keys[count++] = i;
    for (int i = 1; i < count; i++) {
        int x = keys[i], j = i - 1;
        while (j >= 0) {
            entry *a = &L->entries[keys[j]], *b = &L->entries[x];
            int ra = a->rule == RULE_LEAST_C ? 0 : 1, rb = b->rule == RULE_LEAST_C ? 0 : 1;
            if (a->size > b->size || (a->size == b->size && ra > rb)) { keys[j + 1] = keys[j]; j--; }
            else break;
        }
        keys[j + 1] = x;
    }
    int *scratch = xmalloc(sizeof(int) * (size_t) L->n);
    for (int t = 0; t < count; t++) {
        entry *e = &L->entries[keys[t]];
        int p = e->upper, stop = 0;
        while (p > floor_) {
            if (e->refuted >= p - 1) {
                best = p - 1; L->best_size = e->size; L->best_rule = e->rule; floor_ = p;
                break;
            }
            long long remaining = cap - L->nodes;
            if (max_nodes != NO_LIMIT && max_nodes < remaining) remaining = max_nodes;
            if (remaining <= 0 || deadline_passed(deadline)) { stop = 1; break; }
            if (CFG_RESTRICT_NODES) {
                long long b = CFG_RESTRICT_NODES < remaining ? CFG_RESTRICT_NODES : remaining;
                if (ladder_decide(L, e, p, b, deadline, 1, scratch) == SAT) {
                    int vs = vertex_separation(&e->minor, scratch);
                    p = p - 1 < vs ? p - 1 : vs;
                    e->upper = p;
                    continue;
                }
                remaining = cap - L->nodes;
                if (max_nodes != NO_LIMIT && max_nodes < remaining) remaining = max_nodes;
                if (remaining <= 0) { stop = 1; break; }
            }
            int st = ladder_decide(L, e, p, remaining, deadline, 0, scratch);
            if (st == UNSAT) {
                e->refuted = p - 1;
                best = p - 1; L->best_size = e->size; L->best_rule = e->rule; floor_ = p;
                break;
            }
            if (st != SAT) { stop = 1; break; }
            int vs = vertex_separation(&e->minor, scratch);
            p = p - 1 < vs ? p - 1 : vs;
            e->upper = p;
        }
        if (stop) break;
    }
    free(scratch);
    free(keys);
    L->best_refuted = best;
    return best >= 0 && best + 1 > lower ? best : -1;
}

/* ---- the descent (solve.py) -------------------------------------------- */

#define PROOF_NONE 0
#define PROOF_REFUTATION 1
#define PROOF_MINOR 2
#define PROOF_BOUND 3
static const char *PROOF_NAMES[] = {"upper", "refutation", "minor", "bound"};

typedef struct {
    int width, lower, upper_start, proof;
    int *order;                  /* closing order over the component's indices */
    long long nodes, minor_nodes;
    double seconds;
} solution;

/* solve_masks: descend from the upper bound with the complete search.
 * time_budget < 0 means none; max_nodes is the per-call node budget. */
static solution solve_masks(const graph *g, double time_budget, long long max_nodes) {
    double started = now();
    solution sol;
    memset(&sol, 0, sizeof sol);
    int n = g->n;
    sol.order = xmalloc(sizeof(int) * (size_t) (n ? n : 1));
    if (n == 0) { sol.width = -1; sol.proof = PROOF_BOUND; return sol; }

    int lower = lower_bound(g);
    int width = initial_upper_bound(g, sol.order);
    sol.upper_start = width;
    if (width <= lower) {
        sol.width = width; sol.lower = lower; sol.proof = PROOF_BOUND;
        sol.seconds = now() - started;
        return sol;
    }

    ladder L;
    ladder_init(&L, g);
    int lower_proof = PROOF_BOUND, proof = -1;
    long long nodes = 0;
    int *answer = xmalloc(sizeof(int) * (size_t) n);
    int *probe_order = xmalloc(sizeof(int) * (size_t) n);
    int w = width - 1;
    while (w >= lower) {
        double deadline = time_budget < 0 ? NO_DEADLINE : started + time_budget;
        int have_probe = 0, probe_status = UNKNOWN;
        if (CFG_PROBE_NODES && ladder_applies(&L)) {
            long long budget = max_nodes != NO_LIMIT && max_nodes != 0 ? max_nodes : (1LL << 62);
            if (CFG_PROBE_NODES < budget) budget = CFG_PROBE_NODES;
            long long pn;
            probe_status = decide(g, w + 1, 0, budget, deadline, probe_order, &pn);
            nodes += pn;
            have_probe = probe_status != UNKNOWN;
        }
        if (!have_probe && ladder_applies(&L)) {
            long long before = L.nodes;
            double cutoff = time_budget < 0 ? NO_DEADLINE : started + CFG_TIME_FRACTION * time_budget;
            if (try_refute(&L, w, cutoff, max_nodes, sol.order)) {
                lower = w + 1;
                lower_proof = PROOF_MINOR;
                nodes += L.nodes - before;
                break;
            }
            int raised = raise_lower(&L, lower, cutoff, max_nodes);
            if (raised >= 0 && raised + 1 > lower) {
                lower = raised + 1;
                lower_proof = PROOF_MINOR;
            }
            nodes += L.nodes - before;
            if (w < lower) break;
        }
        int status;
        if (have_probe) {
            status = probe_status;
            memcpy(answer, probe_order, sizeof(int) * (size_t) n);
        } else {
            long long an;
            status = decide(g, w + 1, 0, max_nodes, deadline, answer, &an);
            nodes += an;
        }
        if (status == UNSAT) { proof = width == w + 1 ? PROOF_REFUTATION : PROOF_NONE; break; }
        if (status == UNKNOWN) { proof = PROOF_NONE; break; }
        int achieved = vertex_separation(g, answer);
        if (achieved < width) {
            width = achieved;
            memcpy(sol.order, answer, sizeof(int) * (size_t) n);
        }
        w = (w < achieved ? w : achieved) - 1;
    }
    if (proof < 0) proof = width <= lower ? lower_proof : PROOF_NONE;
    sol.width = width;
    sol.lower = lower;
    sol.proof = proof;
    sol.nodes = nodes;
    sol.minor_nodes = L.nodes;
    sol.seconds = now() - started;
    free(answer);
    free(probe_order);
    ladder_free(&L);
    return sol;
}

/* Components above the engine's 1024 vertices: the bounds alone (the Python
 * would run its pure-Python search here). Sound either way: the greedy width
 * is achieved, and proved when it meets the lower bound. */
static solution solve_bounds_only(const graph *g) {
    double started = now();
    solution sol;
    memset(&sol, 0, sizeof sol);
    sol.order = xmalloc(sizeof(int) * (size_t) g->n);
    greedy_order(g, sol.order);
    sol.width = sol.upper_start = vertex_separation(g, sol.order);
    sol.lower = lower_bound(g);
    sol.proof = sol.width <= sol.lower ? PROOF_BOUND : PROOF_NONE;
    sol.seconds = now() - started;
    return sol;
}

/* solve: component by component, widest first; the width is the maximum and
 * the proof that of the widest component, provided every component is
 * proved. `order` receives the closing order over the whole graph. */
static solution solve(const graph *g, double time_budget, long long max_nodes) {
    double started = now();
    int n = g->n, nw = g->nw;
    solution total;
    memset(&total, 0, sizeof total);
    total.order = xmalloc(sizeof(int) * (size_t) (n ? n : 1));
    if (n == 0) { total.width = -1; total.lower = -1; total.upper_start = -1; total.proof = PROOF_BOUND; return total; }

    /* connected components, in order of their smallest vertex, each listed in
     * increasing vertex order */
    int *comp = xmalloc(sizeof(int) * (size_t) n), *queue = xmalloc(sizeof(int) * (size_t) n);
    int ncomp = 0;
    for (int v = 0; v < n; v++) comp[v] = -1;
    for (int s = 0; s < n; s++) {
        if (comp[s] >= 0) continue;
        int head = 0, tail = 0;
        comp[s] = ncomp; queue[tail++] = s;
        while (head < tail) {
            int x = queue[head++];
            BS_FOR(y, row(g, x), nw) if (comp[y] < 0) { comp[y] = ncomp; queue[tail++] = y; }
        }
        ncomp++;
    }
    int *csize = xcalloc((size_t) ncomp, sizeof(int));
    for (int v = 0; v < n; v++) csize[comp[v]]++;
    /* widest (largest) first, stable */
    int *corder = xmalloc(sizeof(int) * (size_t) ncomp);
    for (int c = 0; c < ncomp; c++) corder[c] = c;
    for (int i = 1; i < ncomp; i++) {
        int x = corder[i], j = i - 1;
        while (j >= 0 && csize[corder[j]] < csize[x]) { corder[j + 1] = corder[j]; j--; }
        corder[j + 1] = x;
    }

    int *labels = xmalloc(sizeof(int) * (size_t) n), *local = xmalloc(sizeof(int) * (size_t) n);
    int pos = 0, all_proved = 1, width = -1, best_lower = -1, best_upper = -1;
    int widest_has[4] = {0, 0, 0, 0};
    int *proofs = xmalloc(sizeof(int) * (size_t) ncomp), *widths = xmalloc(sizeof(int) * (size_t) ncomp);
    for (int t = 0; t < ncomp; t++) {
        int c = corder[t], m = 0;
        for (int v = 0; v < n; v++) if (comp[v] == c) { local[v] = m; labels[m++] = v; }
        graph h = graph_new(m);
        for (int i = 0; i < m; i++) BS_FOR(y, row(g, labels[i]), nw) bs_set(row(&h, i), local[y]);
        double remaining = -1.0;
        if (time_budget >= 0) {
            remaining = (ncomp == 1) ? time_budget : started + time_budget - now();
            if (remaining < 0) remaining = 0.0;
        }
        solution sub = m > ENGINE_MAX_VERTICES ? solve_bounds_only(&h) : solve_masks(&h, remaining, max_nodes);
        for (int i = 0; i < m; i++) total.order[pos++] = labels[sub.order[i]];
        proofs[t] = sub.proof; widths[t] = sub.width;
        if (sub.width > width) width = sub.width;
        if (sub.lower > best_lower) best_lower = sub.lower;
        if (sub.upper_start > best_upper) best_upper = sub.upper_start;
        if (!sub.proof) all_proved = 0;
        total.nodes += sub.nodes;
        total.minor_nodes += sub.minor_nodes;
        free(sub.order);
        graph_free(&h);
    }
    for (int t = 0; t < ncomp; t++) if (widths[t] == width) widest_has[proofs[t]] = 1;
    total.proof = PROOF_NONE;
    if (all_proved) {
        if (widest_has[PROOF_REFUTATION]) total.proof = PROOF_REFUTATION;
        else if (widest_has[PROOF_MINOR]) total.proof = PROOF_MINOR;
        else total.proof = PROOF_BOUND;
    }
    total.width = width;
    total.lower = best_lower;
    total.upper_start = best_upper;
    total.seconds = now() - started;
    free(comp); free(queue); free(csize); free(corder); free(labels); free(local);
    free(proofs); free(widths);
    return total;
}

/* The independent check of a printed layout: the textbook vertex separation,
 * max over i of |{u : pos(u) <= i < max pos of a neighbour of u}|, computed
 * from the adjacency with no bitmask arithmetic shared with the search. */
static int layout_width(const graph *g, const int *layout) {
    int n = g->n;
    int *pos = xmalloc(sizeof(int) * (size_t) n), *delta = xcalloc((size_t) n + 1, sizeof(int));
    for (int i = 0; i < n; i++) pos[i] = -1;
    for (int i = 0; i < n; i++) {
        if (layout[i] < 0 || layout[i] >= n || pos[layout[i]] >= 0) fatal("layout is not a permutation");
        pos[layout[i]] = i;
    }
    for (int u = 0; u < n; u++) {
        int last = pos[u];
        BS_FOR(v, row(g, u), g->nw) if (pos[v] > last) last = pos[v];
        if (last > pos[u]) { delta[pos[u]]++; delta[last]--; }
    }
    int peak = 0, run = 0;
    for (int i = 0; i < n; i++) { run += delta[i]; if (run > peak) peak = run; }
    free(pos);
    free(delta);
    return peak;
}

/* ---- graph6 ------------------------------------------------------------ */

#define MAX_INPUT_VERTICES 32768

/* Parse one graph6 string (no newline). Returns 0 on success, else sets *err. */
static int parse_graph6(const char *s, size_t len, graph *out, const char **err) {
    if (len >= 10 && memcmp(s, ">>graph6<<", 10) == 0) { s += 10; len -= 10; }
    if (len && (s[0] == ':' || s[0] == ';')) { *err = "sparse6 is not supported"; return 1; }
    if (len && s[0] == '&') { *err = "digraph6 is not supported"; return 1; }
    for (size_t i = 0; i < len; i++)
        if ((unsigned char) s[i] < 63 || (unsigned char) s[i] > 126) { *err = "invalid graph6 character"; return 1; }
    if (len == 0) { *err = "empty graph6 string"; return 1; }
    size_t at;
    unsigned long long n;
    if (s[0] != 126) { n = (unsigned long long) (s[0] - 63); at = 1; }
    else if (len >= 2 && s[1] != 126) {
        if (len < 4) { *err = "truncated graph6 size"; return 1; }
        n = 0;
        for (int i = 1; i <= 3; i++) n = (n << 6) | (unsigned long long) (s[i] - 63);
        at = 4;
    } else {
        if (len < 8) { *err = "truncated graph6 size"; return 1; }
        n = 0;
        for (int i = 2; i <= 7; i++) n = (n << 6) | (unsigned long long) (s[i] - 63);
        at = 8;
    }
    if (n > MAX_INPUT_VERTICES) { *err = "graph too large (more than 32768 vertices)"; return 1; }
    unsigned long long pairs = n * (n ? n - 1 : 0) / 2, bytes = (pairs + 5) / 6;
    if (len - at != bytes) { *err = "graph6 length does not match its vertex count"; return 1; }
    *out = graph_new((int) n);
    for (int v = 0; v < (int) n; v++) bs_set(row(out, v), v);
    unsigned long long k = 0;
    for (int j = 1; j < (int) n; j++)
        for (int i = 0; i < j; i++, k++) {
            int byte = s[at + k / 6] - 63;
            if ((byte >> (5 - (int) (k % 6))) & 1) { bs_set(row(out, i), j); bs_set(row(out, j), i); }
        }
    return 0;
}

/* ---- main -------------------------------------------------------------- */

static void usage(FILE *f) {
    fprintf(f,
        "usage: pathwidth [-t seconds] [-n nodes] [-l] [-v] < graphs.g6\n"
        "  Reads graph6 strings, one per line, and prints for each graph\n"
        "    pathwidth <w> <status>\n"
        "  with status refutation | bound | minor (w is proved) or upper (budget ran\n"
        "  out: w is an upper bound only).\n"
        "  -t seconds  time budget per graph for the descent (default 300; 0 = none)\n"
        "  -n nodes    node budget per search call (default none)\n"
        "  -l          also print 'layout v1 ... vn', a vertex order (0-based) of\n"
        "              vertex separation w, checked before printing\n"
        "  -v          lower bound, starting upper bound, nodes and seconds on stderr\n");
}

int main(int argc, char **argv) {
    double time_budget = 300.0;
    long long max_nodes = NO_LIMIT;
    int print_layout = 0, verbose = 0;
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (!strcmp(a, "-t") && i + 1 < argc) {
            char *end;
            time_budget = strtod(argv[++i], &end);
            if (*end || time_budget < 0) { usage(stderr); return 1; }
            if (time_budget == 0) time_budget = -1.0;
        } else if (!strcmp(a, "-n") && i + 1 < argc) {
            char *end;
            max_nodes = strtoll(argv[++i], &end, 10);
            if (*end || max_nodes < 0) { usage(stderr); return 1; }
            if (max_nodes == 0) max_nodes = NO_LIMIT;
        } else if (!strcmp(a, "-l")) {
            print_layout = 1;
        } else if (!strcmp(a, "-v")) {
            verbose = 1;
        } else if (!strcmp(a, "-h") || !strcmp(a, "--help")) {
            usage(stdout);
            return 0;
        } else {
            usage(stderr);
            return 1;
        }
    }

    size_t capacity = 1 << 16, len;
    char *line = xmalloc(capacity);
    long long lineno = 0;
    int status = 0;
    while (1) {
        len = 0;
        int ch = 0;
        while ((ch = getchar()) != EOF && ch != '\n') {
            if (len + 1 >= capacity) {
                capacity *= 2;
                line = realloc(line, capacity);
                if (!line) fatal("out of memory");
            }
            line[len++] = (char) ch;
        }
        if (ch == EOF && len == 0) break;
        lineno++;
        while (len && (line[len - 1] == '\r' || line[len - 1] == ' ' || line[len - 1] == '\t')) len--;
        size_t start = 0;
        while (start < len && (line[start] == ' ' || line[start] == '\t')) start++;
        if (start == len) { if (ch == EOF) break; continue; }
        if (len - start == 10 && memcmp(line + start, ">>graph6<<", 10) == 0) { if (ch == EOF) break; continue; }
        line[len] = 0;

        graph g;
        const char *err = NULL;
        if (parse_graph6(line + start, len - start, &g, &err)) {
            printf("error %s\n", err);
            fflush(stdout);
            fprintf(stderr, "pathwidth: line %lld: %s\n", lineno, err);
            status = 1;
            if (ch == EOF) break;
            continue;
        }
        solution sol = solve(&g, time_budget, max_nodes);

        /* checked, not trusted: the closing order's width on the whole graph,
         * and the textbook width of the printed layout, both equal to w */
        int *layout = xmalloc(sizeof(int) * (size_t) (g.n ? g.n : 1));
        for (int i = 0; i < g.n; i++) layout[i] = sol.order[g.n - 1 - i];
        if (g.n > 0) {
            if (vertex_separation(&g, sol.order) != sol.width) fatal("closing order does not achieve the width");
            if (layout_width(&g, layout) != sol.width) fatal("layout does not achieve the width");
        }
        printf("pathwidth %d %s\n", sol.width, PROOF_NAMES[sol.proof]);
        if (print_layout) {
            fputs("layout", stdout);
            for (int i = 0; i < g.n; i++) printf(" %d", layout[i]);
            fputc('\n', stdout);
        }
        fflush(stdout);
        if (verbose)
            fprintf(stderr, "line %lld: n=%d width=%d status=%s lower=%d upper_start=%d nodes=%lld "
                    "minor_nodes=%lld upper_bound_nodes=%lld engine_calls=%lld seconds=%.3f\n",
                    lineno, g.n, sol.width, PROOF_NAMES[sol.proof], sol.lower, sol.upper_start,
                    sol.nodes, sol.minor_nodes, upper_nodes, engine_calls, sol.seconds);
        upper_nodes = engine_calls = 0;
        free(layout);
        free(sol.order);
        graph_free(&g);
        if (ch == EOF) break;
    }
    free(line);
    return status;
}
