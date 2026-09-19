/* Complete search over customer closing orders -- the C port.
 *
 * A faithful translation of `decide()` in customer_search.py, which is the
 * reference: where the two could differ, the Python is right and this is
 * wrong. `tests/test_native.py` checks them against each other exhaustively,
 * because a search that disagrees with its reference produces refutations that
 * are confidently false, and a refutation is the half of an optimality claim
 * nobody can check by inspection.
 *
 * Why it exists: Chu & Stuckey (2009) close 125-125-2 in about 19 minutes with
 * this algorithm in C++. The Python here does not close it at all, and the gap
 * is very largely the language.
 *
 * Customer sets are 128-bit words, which covers the whole benchmark tree (125
 * customers is the largest). Above that the caller must stay on the Python.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 mask_t;

#define BIT(i)        (((mask_t) 1) << (i))
#define LOWEST(x)     ((x) & -(x))

static inline int popcount128(mask_t x) {
    return __builtin_popcountll((uint64_t) x) +
           __builtin_popcountll((uint64_t) (x >> 64));
}

static inline int lowest_index(mask_t x) {
    uint64_t low = (uint64_t) x;
    return low ? __builtin_ctzll(low) : 64 + __builtin_ctzll((uint64_t)(x >> 64));
}

/* Open-addressing set of refuted states. The Python uses a Python set with a
 * cap; this is the same idea with linear probing. Zero marks an empty slot,
 * which is safe because the empty closed-set is never refuted: it is the root,
 * and reaching it again would mean the whole search had already failed. */
typedef struct {
    mask_t  *slots;
    size_t   capacity;      /* a power of two, or 0 when memoisation is off */
    size_t   used;
    size_t   limit;
} memo_t;

static int memo_init(memo_t *m, size_t capacity, size_t limit) {
    m->slots = calloc(capacity, sizeof(mask_t));
    if (!m->slots) return 0;
    m->capacity = capacity;
    m->used = 0;
    m->limit = limit;
    return 1;
}

static inline size_t memo_hash(mask_t key, size_t capacity) {
    uint64_t h = (uint64_t) key ^ ((uint64_t)(key >> 64) * 0x9E3779B97F4A7C15ULL);
    h ^= h >> 29; h *= 0xBF58476D1CE4E5B9ULL; h ^= h >> 32;
    return (size_t) h & (capacity - 1);
}

static int memo_has(const memo_t *m, mask_t key) {
    if (!m->capacity) return 0;
    size_t i = memo_hash(key, m->capacity);
    while (m->slots[i]) {
        if (m->slots[i] == key) return 1;
        i = (i + 1) & (m->capacity - 1);
    }
    return 0;
}

static void memo_add(memo_t *m, mask_t key) {
    /* Stop filling past the limit, and never past 70% load: linear probing
     * degrades badly when full, and an unbounded table on a multi-day run is
     * how a machine dies. */
    if (!m->capacity || m->used >= m->limit ||
        m->used * 10 >= m->capacity * 7) return;
    size_t i = memo_hash(key, m->capacity);
    while (m->slots[i]) {
        if (m->slots[i] == key) return;
        i = (i + 1) & (m->capacity - 1);
    }
    m->slots[i] = key;
    m->used++;
}

typedef struct {
    int      n;                 /* active customers */
    int      k;                 /* the budget on open stacks */
    mask_t   full;
    mask_t  *neighbour;         /* self-inclusive neighbourhoods */
    memo_t   memo;
    int      subset_rule;
    int      definite_move;
    int      use_memo;
    int      restrict_frontier;
    long long nodes;
    long long max_nodes;        /* < 0 for unlimited */
    double   deadline;          /* <= 0 for none, else CLOCK_MONOTONIC seconds */
    int      aborted;
    int     *path;
    int      depth;
} search_t;

static double monotonic_now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double) ts.tv_sec + (double) ts.tv_nsec * 1e-9;
}

static int search(search_t *s, mask_t closed, mask_t opened, mask_t seen);

/* Candidates surviving the dominance relations, written into `order` as
 * (cost, customer) pairs sorted by cost. Returns how many. */
static int dominance_filter(search_t *s, mask_t remaining, mask_t candidates,
                            mask_t closed, mask_t opened,
                            int *costs, int *who) {
    mask_t opens[128];
    int    ids[128];
    int    n_remaining = 0;

    for (mask_t bits = remaining; bits; ) {
        mask_t bit = LOWEST(bits); bits ^= bit;
        int c = lowest_index(bit);
        ids[n_remaining] = c;
        opens[n_remaining] = s->neighbour[c] & ~opened;
        n_remaining++;
    }

    int count = 0;
    for (mask_t bits = candidates; bits; ) {
        mask_t bit = LOWEST(bits); bits ^= bit;
        int c = lowest_index(bit);
        int cost = popcount128((opened | s->neighbour[c]) & ~closed);
        if (cost <= s->k) { costs[count] = cost; who[count] = c; count++; }
    }
    if (!count || (!s->subset_rule && !s->definite_move)) goto sorted;

    if (s->definite_move) {
        for (int i = 0; i < count; i++) {
            int c = who[i];
            mask_t own = s->neighbour[c] & ~opened;
            int opened_by = popcount128(own);
            int closed_by = 0;
            for (int j = 0; j < n_remaining; j++)
                if ((opens[j] & ~own) == 0) closed_by++;
            if (closed_by >= opened_by) {
                /* q is at least as good as anything else here. */
                costs[0] = costs[i]; who[0] = c;
                count = 1;
                goto sorted;
            }
        }
    }

    if (s->subset_rule) {
        int kept = 0;
        for (int i = 0; i < count; i++) {
            int c = who[i];
            mask_t own = s->neighbour[c] & ~opened;
            int dominated = 0;
            for (int j = 0; j < n_remaining && !dominated; j++) {
                int d = ids[j];
                if (d == c) continue;
                mask_t other = opens[j];
                if ((other & ~own) == 0 && (other != own || d < c)) dominated = 1;
            }
            if (!dominated) { costs[kept] = costs[i]; who[kept] = c; kept++; }
        }
        /* Every candidate dominated by a non-candidate would empty the list;
         * keep the original in that case, as the Python does. */
        if (kept) count = kept;
    }

sorted:
    /* Insertion sort by cost: the list is short and nearly sorted already. */
    for (int i = 1; i < count; i++) {
        int ci = costs[i], wi = who[i], j = i - 1;
        while (j >= 0 && (costs[j] > ci || (costs[j] == ci && who[j] > wi))) {
            costs[j + 1] = costs[j]; who[j + 1] = who[j]; j--;
        }
        costs[j + 1] = ci; who[j + 1] = wi;
    }
    return count;
}

static int search(search_t *s, mask_t closed, mask_t opened, mask_t seen) {
    int mark = s->depth;

    /* Free moves: customers whose neighbourhood is wholly opened. */
    mask_t free_now = 0;
    for (mask_t bits = s->full & ~closed; bits; ) {
        mask_t bit = LOWEST(bits); bits ^= bit;
        if ((s->neighbour[lowest_index(bit)] & ~opened) == 0) free_now |= bit;
    }
    if (free_now) {
        for (mask_t bits = free_now; bits; ) {
            mask_t bit = LOWEST(bits); bits ^= bit;
            s->path[s->depth++] = lowest_index(bit);
        }
        closed |= free_now;
    }

    if (closed == s->full) return 1;
    if (s->use_memo && memo_has(&s->memo, closed)) { s->depth = mark; return 0; }

    mask_t remaining = s->full & ~closed;
    mask_t candidates = remaining;
    if (s->restrict_frontier) {
        mask_t narrowed = remaining & opened;
        if (narrowed) candidates = narrowed;
    }

    int costs[128], who[128];
    int count = dominance_filter(s, remaining, candidates, closed, opened,
                                 costs, who);

    for (int i = 0; i < count; i++) {
        int c = who[i];
        s->nodes++;
        if (s->max_nodes >= 0 && s->nodes > s->max_nodes) {
            s->aborted = 1; s->depth = mark; return 0;
        }
        if (s->deadline > 0 && (s->nodes & 4095) == 0 &&
            monotonic_now() > s->deadline) {
            s->aborted = 1; s->depth = mark; return 0;
        }

        int here = s->depth;
        s->path[s->depth++] = c;
        if (search(s, closed | BIT(c), opened | s->neighbour[c], 0)) return 1;
        s->depth = here;
        if (s->aborted) { s->depth = mark; return 0; }
        seen |= BIT(c);
    }

    if (s->use_memo && !s->aborted) memo_add(&s->memo, closed);
    s->depth = mark;
    return 0;
}

/* Entry point.
 *
 *   neighbours : n self-inclusive neighbourhood masks, as pairs of uint64
 *                (low, high) so the caller need not know about __int128
 *   out_path   : filled with the closing order when the answer is "sat"
 *   out_nodes  : branches visited
 *
 * Returns 1 for sat, 0 for unsat, -1 for "budget exhausted, nothing proved",
 * and -2 if the memo could not be allocated. The closing order's length goes
 * to *out_len, never the return value: a satisfiable answer on an empty
 * instance has length zero, which would be indistinguishable from unsat.
 *
 * `old_move` is not implemented here. The caller falls back to the Python for
 * it rather than this returning a wrong answer under a flag it ignores.
 */
int cs_decide(int n, int k,
              const uint64_t *neighbours,
              long long max_nodes, double seconds,
              int subset_rule, int definite_move, int use_memo,
              int restrict_frontier, long long memo_limit,
              int *out_path, long long *out_nodes, int *out_len) {
    *out_nodes = 0;
    *out_len = 0;
    if (n <= 0) return 1;

    search_t s;
    memset(&s, 0, sizeof s);
    s.n = n;
    s.k = k;
    s.subset_rule = subset_rule;
    s.definite_move = definite_move;
    s.use_memo = use_memo;
    s.restrict_frontier = restrict_frontier;
    s.max_nodes = max_nodes;
    s.deadline = seconds > 0 ? monotonic_now() + seconds : 0;
    s.path = out_path;

    s.neighbour = malloc(sizeof(mask_t) * (size_t) n);
    if (!s.neighbour) return -2;
    for (int i = 0; i < n; i++)
        s.neighbour[i] = ((mask_t) neighbours[2 * i + 1] << 64) |
                         (mask_t) neighbours[2 * i];
    s.full = n == 128 ? ~(mask_t) 0 : (BIT(n) - 1);

    if (use_memo) {
        size_t capacity = 1u << 20;         /* grows nothing; sized once */
        while (capacity < (size_t) memo_limit * 2 && capacity < (1u << 26))
            capacity <<= 1;
        if (!memo_init(&s.memo, capacity, (size_t) memo_limit)) {
            free(s.neighbour);
            return -2;
        }
    }

    int found = search(&s, 0, 0, 0);
    *out_nodes = s.nodes;
    *out_len = found ? s.depth : 0;

    free(s.neighbour);
    free(s.memo.slots);
    return found ? 1 : (s.aborted ? -1 : 0);
}
