/* Closing-order search -- the C port, generalised to any number of vertices.
 *
 * A translation of `closing_search.c` (itself a verbatim copy of the MOSP
 * project's 128-bit C) from `unsigned __int128` vertex sets to fixed-width
 * multiword sets of WORDS x 64 bits, WORDS being a compile-time constant. The
 * wrapper builds one shared library per WORDS in {2, 4, 8, 16} and loads the
 * smallest that fits the graph, so up to 1024 vertices run in C.
 *
 * The search itself -- free moves, cost, the subset rule, definite move,
 * better move, old move, memo, fan orders, budgets -- is unchanged line for
 * line except for the set operations, and `tests/test_native.py` checks it
 * against the Python reference node for node. Per-node scratch (the arrays
 * indexed by remaining vertex) lives in a heap pool indexed by depth rather
 * than on the stack: a frame for 1024 vertices is ~160 KB and the recursion
 * is as deep as the graph.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef WORDS
#define WORDS 2
#endif
#define MAXN (64 * WORDS)

typedef struct { uint64_t w[WORDS]; } set_t;

#define FAN_ORDER_INDEX  0
#define FAN_ORDER_DEGREE 1
#define BM_OLD_CLOSE_COUNT   1
#define BM_OLD_RULE_ORDER    2
#define BM_SUBSET_RESTRICTED 4

/* ---- set operations ---------------------------------------------------- */

static inline set_t set_empty(void) { set_t s; memset(&s, 0, sizeof s); return s; }
static inline set_t set_full(int n) {
    set_t s = set_empty();
    for (int i = 0; i < n; i++) s.w[i >> 6] |= (uint64_t) 1 << (i & 63);
    return s;
}
static inline set_t set_bit(int i) { set_t s = set_empty(); s.w[i >> 6] = (uint64_t) 1 << (i & 63); return s; }
static inline int  set_test(const set_t *s, int i) { return (int) ((s->w[i >> 6] >> (i & 63)) & 1); }
static inline void set_add(set_t *s, int i) { s->w[i >> 6] |= (uint64_t) 1 << (i & 63); }
static inline set_t set_or(set_t a, set_t b)     { for (int i = 0; i < WORDS; i++) a.w[i] |= b.w[i]; return a; }
static inline set_t set_and(set_t a, set_t b)    { for (int i = 0; i < WORDS; i++) a.w[i] &= b.w[i]; return a; }
static inline set_t set_andnot(set_t a, set_t b) { for (int i = 0; i < WORDS; i++) a.w[i] &= ~b.w[i]; return a; }
static inline int set_is_empty(const set_t *a) { uint64_t x = 0; for (int i = 0; i < WORDS; i++) x |= a->w[i]; return x == 0; }
static inline int set_eq(const set_t *a, const set_t *b) { for (int i = 0; i < WORDS; i++) if (a->w[i] != b->w[i]) return 0; return 1; }
/* a subset of b */
static inline int set_subset(const set_t *a, const set_t *b) { for (int i = 0; i < WORDS; i++) if (a->w[i] & ~b->w[i]) return 0; return 1; }
static inline int set_popcount(const set_t *a) { int c = 0; for (int i = 0; i < WORDS; i++) c += __builtin_popcountll(a->w[i]); return c; }
/* remove and return the lowest set bit's index, -1 if empty */
static inline int set_next(set_t *a) {
    for (int i = 0; i < WORDS; i++)
        if (a->w[i]) { int b = __builtin_ctzll(a->w[i]); a->w[i] &= a->w[i] - 1; return 64 * i + b; }
    return -1;
}

/* ---- memo -------------------------------------------------------------- */

typedef struct {
    set_t   *slots;
    size_t   capacity;      /* a power of two, or 0 when memoisation is off */
    size_t   used;
    size_t   limit;
} memo_t;

static int memo_init(memo_t *m, size_t capacity, size_t limit) {
    m->slots = calloc(capacity, sizeof(set_t));
    if (!m->slots) return 0;
    m->capacity = capacity; m->used = 0; m->limit = limit;
    return 1;
}

static inline size_t memo_hash(const set_t *key, size_t capacity) {
    uint64_t h = 0x9E3779B97F4A7C15ULL;
    for (int i = 0; i < WORDS; i++) {
        h ^= key->w[i];
        h ^= h >> 29; h *= 0xBF58476D1CE4E5B9ULL; h ^= h >> 32;
    }
    return (size_t) h & (capacity - 1);
}

static int memo_has(const memo_t *m, const set_t *key) {
    if (!m->capacity) return 0;
    size_t i = memo_hash(key, m->capacity);
    while (!set_is_empty(&m->slots[i])) {
        if (set_eq(&m->slots[i], key)) return 1;
        i = (i + 1) & (m->capacity - 1);
    }
    return 0;
}

static void memo_add(memo_t *m, const set_t *key) {
    if (!m->capacity || m->used >= m->limit || m->used * 10 >= m->capacity * 7) return;
    size_t i = memo_hash(key, m->capacity);
    while (!set_is_empty(&m->slots[i])) {
        if (set_eq(&m->slots[i], key)) return;
        i = (i + 1) & (m->capacity - 1);
    }
    m->slots[i] = *key;
    m->used++;
}

/* ---- search state ------------------------------------------------------ */

/* Per-depth scratch: one frame per recursion level, sized by n. */
typedef struct {
    set_t *opens;
    int *ids, *sizes, *costs, *who, *index_of, *survives, *deg;
} frame_t;

typedef struct {
    int      n, k;
    set_t    full;
    set_t   *neighbour;
    memo_t   memo;
    int      subset_rule, definite_move, better_move, better_move_dominators,
             better_move_variant, old_move, fan_order, use_memo, restrict_frontier;
    long long nodes, max_nodes;
    double   deadline;
    int      aborted;
    int     *path;
    int      depth;
    frame_t *frames;
    int      level;             /* recursion level, indexes frames */
} search_t;

static double monotonic_now(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double) ts.tv_sec + (double) ts.tv_nsec * 1e-9;
}

static int search(search_t *s, set_t closed, set_t opened, set_t seen);

static int subset_pass(const search_t *s, const int *ids, const set_t *opens,
                       const int *sizes, int n_remaining, const set_t *exclude,
                       int *costs, int *who, int *index_of, int count) {
    int kept = 0;
    for (int i = 0; i < count; i++) {
        int c = who[i], at = index_of[i];
        const set_t *own = &opens[at];
        int own_size = sizes[at], dominated = 0;
        for (int j = 0; j < n_remaining && !dominated; j++) {
            if (sizes[j] > own_size) continue;
            int d = ids[j];
            if (d == c) continue;
            if (exclude && set_test(exclude, d)) continue;
            const set_t *other = &opens[j];
            if (set_subset(other, own) && (!set_eq(other, own) || d < c)) dominated = 1;
        }
        if (!dominated) { costs[kept] = costs[i]; who[kept] = c; index_of[kept] = index_of[i]; kept++; }
    }
    return kept ? kept : count;
}

static int better_move_pass(const search_t *s, set_t closed, set_t opened,
                            int *costs, int *who, int *index_of, int count,
                            int *survives, set_t *discarded) {
    if (count > 1) {
        int limit = s->better_move_dominators > 0 && s->better_move_dominators < count
                    ? s->better_move_dominators : count;
        const int count_finished = s->better_move_variant & BM_OLD_CLOSE_COUNT;
        for (int i = 0; i < count; i++) survives[i] = 1;
        for (int ri = 0; ri < count; ri++) {
            int r = who[ri];
            set_t closed_r = set_or(closed, set_bit(r));
            set_t opened_r = set_or(opened, s->neighbour[r]);
            set_t remaining_r = set_andnot(s->full, closed_r);
            int pruned = 0;
            for (int qi = 0; qi < limit && qi < ri && !pruned; qi++) {
                int q = who[qi];
                if (q == r) continue;
                set_t t = set_andnot(set_or(opened_r, s->neighbour[q]), closed_r);
                if (set_popcount(&t) > s->k) continue;
                set_t own = set_andnot(s->neighbour[q], opened_r);
                int opened_by = set_popcount(&own), closed_by = 0;
                set_t bits = remaining_r;
                for (int v; (v = set_next(&bits)) >= 0; ) {
                    set_t left = set_andnot(s->neighbour[v], opened_r);
                    if ((!set_is_empty(&left) || count_finished) && set_subset(&left, &own)) closed_by++;
                }
                if (closed_by >= opened_by) pruned = 1;
            }
            survives[ri] = !pruned;
        }
        int kept = 0;
        set_t gone = set_empty();
        for (int i = 0; i < count; i++)
            if (survives[i]) { costs[kept] = costs[i]; who[kept] = who[i]; index_of[kept] = index_of[i]; kept++; }
            else set_add(&gone, who[i]);
        if (kept) { count = kept; if (discarded) *discarded = gone; }
    }
    return count;
}

static int dominance_filter(search_t *s, const set_t *candidates,
                            set_t closed, set_t opened,
                            const int *ids, const set_t *opens, const int *sizes,
                            int n_remaining, int open_now,
                            int *costs, int *who, int *index_of, int *survives, int *deg) {
    int count = 0;
    for (int j = 0; j < n_remaining; j++) {
        int c = ids[j];
        if (!set_test(candidates, c)) continue;
        int cost = open_now + sizes[j];
        if (cost <= s->k) { costs[count] = cost; who[count] = c; index_of[count] = j; count++; }
    }
    if (!count || (!s->subset_rule && !s->definite_move && !s->better_move)) goto sorted;

    if (s->definite_move) {
        for (int i = 0; i < count; i++) {
            int c = who[i], at = index_of[i];
            const set_t *own = &opens[at];
            int opened_by = sizes[at], closed_by = 0;
            for (int j = 0; j < n_remaining; j++)
                if (sizes[j] <= opened_by && set_subset(&opens[j], own)) closed_by++;
            if (closed_by >= opened_by) { costs[0] = costs[i]; who[0] = c; count = 1; goto sorted; }
        }
    }
    if (s->better_move_variant & BM_SUBSET_RESTRICTED) {
        set_t gone = set_empty();
        if (s->better_move) count = better_move_pass(s, closed, opened, costs, who, index_of, count, survives, &gone);
        if (s->subset_rule) count = subset_pass(s, ids, opens, sizes, n_remaining, &gone, costs, who, index_of, count);
    } else if (s->better_move_variant & BM_OLD_RULE_ORDER) {
        if (s->better_move) count = better_move_pass(s, closed, opened, costs, who, index_of, count, survives, NULL);
        if (s->subset_rule) count = subset_pass(s, ids, opens, sizes, n_remaining, NULL, costs, who, index_of, count);
    } else {
        if (s->subset_rule) count = subset_pass(s, ids, opens, sizes, n_remaining, NULL, costs, who, index_of, count);
        if (s->better_move) count = better_move_pass(s, closed, opened, costs, who, index_of, count, survives, NULL);
    }

sorted:
    if (s->fan_order == FAN_ORDER_DEGREE) {
        set_t remaining = set_andnot(s->full, closed);
        for (int i = 0; i < count; i++) { set_t t = set_and(s->neighbour[who[i]], remaining); deg[i] = set_popcount(&t) - 1; }
        for (int i = 1; i < count; i++) {
            int ci = costs[i], wi = who[i], di = deg[i], j = i - 1;
            while (j >= 0 && (costs[j] > ci || (costs[j] == ci && (deg[j] < di || (deg[j] == di && who[j] > wi))))) {
                costs[j + 1] = costs[j]; who[j + 1] = who[j]; deg[j + 1] = deg[j]; j--;
            }
            costs[j + 1] = ci; who[j + 1] = wi; deg[j + 1] = di;
        }
        return count;
    }
    for (int i = 1; i < count; i++) {
        int ci = costs[i], wi = who[i], j = i - 1;
        while (j >= 0 && (costs[j] > ci || (costs[j] == ci && who[j] > wi))) { costs[j + 1] = costs[j]; who[j + 1] = who[j]; j--; }
        costs[j + 1] = ci; who[j + 1] = wi;
    }
    return count;
}

static set_t inherit_old_moves(search_t *s, set_t seen, set_t closed, set_t opened, int vertex) {
    set_t kept = set_empty();
    set_t bits = seen;
    for (int other; (other = set_next(&bits)) >= 0; ) {
        set_t t = set_or(set_or(opened, s->neighbour[other]), s->neighbour[vertex]);
        t = set_andnot(t, set_or(closed, set_bit(other)));
        if (set_popcount(&t) <= s->k) set_add(&kept, other);
    }
    return kept;
}

static int search(search_t *s, set_t closed, set_t opened, set_t seen) {
    int mark = s->depth;
    frame_t *f = &s->frames[s->level];
    set_t *opens = f->opens; int *ids = f->ids, *sizes = f->sizes;
    int n_remaining = 0;
    set_t free_now = set_empty();
    set_t bits = set_andnot(s->full, closed);
    for (int c; (c = set_next(&bits)) >= 0; ) {
        set_t own = set_andnot(s->neighbour[c], opened);
        int size = set_popcount(&own);
        if (!size) { set_add(&free_now, c); continue; }
        ids[n_remaining] = c; opens[n_remaining] = own; sizes[n_remaining] = size; n_remaining++;
    }
    if (!set_is_empty(&free_now)) {
        set_t fb = free_now;
        for (int c; (c = set_next(&fb)) >= 0; ) s->path[s->depth++] = c;
        closed = set_or(closed, free_now);
    }

    if (set_eq(&closed, &s->full)) return 1;
    if (s->use_memo && memo_has(&s->memo, &closed)) { s->depth = mark; return 0; }

    set_t remaining = set_andnot(s->full, closed);
    seen = set_and(seen, remaining);
    set_t candidates = s->old_move ? set_andnot(remaining, seen) : remaining;
    if (s->restrict_frontier) {
        set_t narrowed = set_and(remaining, opened);
        if (!set_is_empty(&narrowed)) candidates = narrowed;
    }

    set_t on = set_andnot(opened, closed);
    int open_now = set_popcount(&on);
    int count = dominance_filter(s, &candidates, closed, opened, ids, opens, sizes, n_remaining, open_now,
                                 f->costs, f->who, f->index_of, f->survives, f->deg);
    int *costs = f->costs, *who = f->who; (void) costs;

    for (int i = 0; i < count; i++) {
        int c = who[i];
        s->nodes++;
        if (s->max_nodes >= 0 && s->nodes > s->max_nodes) { s->aborted = 1; s->depth = mark; return 0; }
        if (s->deadline > 0 && (s->nodes & 4095) == 0 && monotonic_now() > s->deadline) { s->aborted = 1; s->depth = mark; return 0; }

        int here = s->depth;
        s->path[s->depth++] = c;
        set_t inherited = (s->old_move && !set_is_empty(&seen)) ? inherit_old_moves(s, seen, closed, opened, c) : set_empty();
        s->level++;
        int found = search(s, set_or(closed, set_bit(c)), set_or(opened, s->neighbour[c]), inherited);
        s->level--;
        if (found) return 1;
        s->depth = here;
        if (s->aborted) { s->depth = mark; return 0; }
        set_add(&seen, c);
    }

    if (s->use_memo && !s->aborted) memo_add(&s->memo, &closed);
    s->depth = mark;
    return 0;
}

/* Entry point. `neighbours` holds n sets of WORDS little-endian uint64 words.
 * Returns 1 sat, 0 unsat, -1 budget exhausted, -2 allocation failure, -3 n too
 * large for this build (MAXN). `csw_words()` reports WORDS. */
int csw_words(void) { return WORDS; }

int csw_decide(int n, int k,
               const uint64_t *neighbours,
               long long max_nodes, double seconds,
               int subset_rule, int definite_move, int use_memo,
               int restrict_frontier, long long memo_limit,
               int better_move, int better_move_dominators, int old_move,
               int fan_order, int better_move_variant,
               int *out_path, long long *out_nodes, int *out_len) {
    *out_nodes = 0; *out_len = 0;
    if (n <= 0) return 1;
    if (n > MAXN) return -3;

    search_t s; memset(&s, 0, sizeof s);
    s.n = n; s.k = k;
    s.subset_rule = subset_rule; s.definite_move = definite_move; s.better_move = better_move;
    s.better_move_dominators = better_move_dominators; s.better_move_variant = better_move_variant;
    s.old_move = old_move; s.fan_order = fan_order; s.use_memo = use_memo; s.restrict_frontier = restrict_frontier;
    s.max_nodes = max_nodes; s.deadline = seconds > 0 ? monotonic_now() + seconds : 0;
    s.path = out_path;

    s.neighbour = malloc(sizeof(set_t) * (size_t) n);
    if (!s.neighbour) return -2;
    for (int i = 0; i < n; i++) for (int w = 0; w < WORDS; w++) s.neighbour[i].w[w] = neighbours[(size_t) i * WORDS + w];
    s.full = set_full(n);

    /* scratch pool: n+1 frames of n entries each */
    size_t per = (size_t) n;
    s.frames = malloc(sizeof(frame_t) * (size_t) (n + 1));
    set_t *opens_pool = malloc(sizeof(set_t) * per * (size_t) (n + 1));
    int *int_pool = malloc(sizeof(int) * per * 7 * (size_t) (n + 1));
    if (!s.frames || !opens_pool || !int_pool) { free(s.neighbour); free(s.frames); free(opens_pool); free(int_pool); return -2; }
    for (int d = 0; d <= n; d++) {
        frame_t *f = &s.frames[d];
        f->opens = opens_pool + per * (size_t) d;
        int *base = int_pool + per * 7 * (size_t) d;
        f->ids = base; f->sizes = base + per; f->costs = base + 2 * per; f->who = base + 3 * per;
        f->index_of = base + 4 * per; f->survives = base + 5 * per; f->deg = base + 6 * per;
    }

    if (use_memo) {
        /* sized as the 128-bit version, then capped so the table stays under
         * ~512 MB whatever the word count */
        size_t capacity = 1u << 20;
        while (capacity < (size_t) memo_limit * 2 && capacity < (1u << 26)) capacity <<= 1;
        size_t max_slots = ((size_t) 512 << 20) / sizeof(set_t);
        while (capacity > max_slots && capacity > (1u << 16)) capacity >>= 1;
        size_t limit = (size_t) memo_limit;
        if (limit * 10 > capacity * 7) limit = capacity * 7 / 10;
        if (!memo_init(&s.memo, capacity, limit)) {
            free(s.neighbour); free(s.frames); free(opens_pool); free(int_pool); return -2;
        }
    }

    int found = search(&s, set_empty(), set_empty(), set_empty());
    *out_nodes = s.nodes;
    *out_len = found ? s.depth : 0;

    free(s.neighbour); free(s.memo.slots); free(s.frames); free(opens_pool); free(int_pool);
    return found ? 1 : (s.aborted ? -1 : 0);
}
