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

/* Fan order among equal-cost candidates. INDEX is what every run before
 * 2026-09-26 used and stays the default; DEGREE is the flag of plan 2 §2.5a. */
#define FAN_ORDER_INDEX  0
#define FAN_ORDER_DEGREE 1

/* Variants of the 2026-09-26 `better_move` fix (0eb33915), for measuring
 * which of its two changes carries its cost (reports/ml_nature.md §31). Each
 * bit *reverts* one change; 0 is today's rule, 3 is the rule as it stood
 * before the fix under the `csearch` configuration. Both reverted forms are
 * unsound (reports/better_move_bug.md §7) and exist only to be measured. */
#define BM_OLD_CLOSE_COUNT 1   /* count customers r finishes alone as stacks q closes */
#define BM_OLD_RULE_ORDER  2   /* better move before the subset rule, which then cites discarded candidates */
/* Not a revert: a candidate composition. Better move first over every
 * candidate, then the subset rule over its survivors citing only customers
 * better move did not discard, so no chain of coverings can point back at a
 * discarded candidate. Measured as `bm-first`; today's rule is unchanged. */
#define BM_SUBSET_RESTRICTED 4

/* How often each rule's prefilter and its repaired test pass, for measuring
 * what the repair costs (loop0007 item 04). Per thread, reset by every call
 * to `cs_decide_rules` and read back with `cs_last_rule_counts`. Counting
 * never changes the search. */
enum {
    RC_FILTER_CALLS,    /* dominance_filter calls with a candidate left */
    RC_DEF_PREFILTER,   /* definite: candidates passing close >= open */
    RC_DEF_MATCH_FAIL,  /* ... of which the matching test fails (repaired) */
    RC_DEF_FIRES,       /* nodes where the definite move fires */
    RC_DEF_LOST,        /* nodes with a prefilter pass where none fires */
    RC_BM_PREFILTER,    /* better: (r, q) pairs passing premises 3 and 4 */
    RC_BM_MATCH_FAIL,   /* ... of which the matching test fails (repaired) */
    RC_BM_PRUNED,       /* candidates r the better move drops */
    /* The audit of the published rules (`repaired_rules = 2`, loop0007 item
     * 07): the search is the published one, and at every node it expands the
     * check `CodeNodeRepaired` of lean/MOSPFormalization/Search/Decide.lean is
     * evaluated. A run with no failing node is sound by
     * `codeExec_mospValue_of_repaired`. */
    RC_AUDIT_DEF_FAIL,  /* nodes whose definite pick is not hereditarily definite */
    RC_AUDIT_BM_FAIL,   /* nodes with a better-move drop no repaired citation covers */
    RC_AUDIT_NODE_FAIL, /* nodes failing either */
    RC_COUNT
};
static __thread long long rule_counts[RC_COUNT];
static __thread int audit_node_bad;    /* the current node failed the audit */

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
    int      better_move;
    int      better_move_dominators;   /* how many q to try; 0 for all */
    int      better_move_variant;      /* BM_OLD_* bits; 0 is today's rule */
    int      old_move;
    int      repaired_rules;    /* the repaired definite and better moves (loop0007) */
    int      audit_repaired;    /* published rules, CodeNodeRepaired counted (item 07) */
    int      fan_order;         /* 0: ties by customer index; 1: by remaining degree, highest first */
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

/* Kuhn's augmenting path from freed set `i`, stacks as bit indices. */
static int augment(const mask_t *sets, int i, int *owner, mask_t *visited) {
    for (mask_t bits = sets[i]; bits; ) {
        mask_t bit = LOWEST(bits); bits ^= bit;
        if (*visited & bit) continue;
        *visited |= bit;
        int stack = lowest_index(bit);
        if (owner[stack] < 0 || augment(sets, owner[stack], owner, visited)) {
            owner[stack] = i;
            return 1;
        }
    }
    return 0;
}

/* The matching test of the repaired rules, `_has_definite_matching` in the
 * Python: whether `need` of the `count` sets in `sets` can be matched to
 * distinct members. `sets` holds o(d, S) for each customer d != q that closing
 * q frees and `need` is open(q, S) - 1; by Theorem 4.8
 * (`isHereditarilyDefinite_iff_hasDefiniteMatching`) a matching of that size
 * is exactly q being hereditarily definite at S. Only the yes/no answer is
 * used, so the augmenting order need not follow the Python's. */
static int has_definite_matching(const mask_t *sets, int count, int need) {
    if (need <= 0) return 1;
    if (count < need) return 0;
    int owner[128];
    for (int i = 0; i < 128; i++) owner[i] = -1;
    int matched = 0;
    for (int i = 0; i < count; i++) {
        mask_t visited = 0;
        if (augment(sets, i, owner, &visited) && ++matched >= need) return 1;
    }
    return 0;
}

/* The audit's `IsRepairedBetter G k S r q`, at the child state given by
 * `closed_r = S u {r}` and `opened_r = O(S u {r})`: S ++ [r, q] playable in the
 * paper's measure, and q hereditarily definite at cl(S u {r}) by the matching
 * test over the customers q frees there (q excluded, finished ones gone). */
static int audit_repaired_better(const search_t *s, mask_t closed_r, mask_t opened_r, int q) {
    if (popcount128((opened_r | s->neighbour[q]) & ~closed_r) > s->k) return 0;
    mask_t own = s->neighbour[q] & ~opened_r;
    mask_t freed[128];
    int n_freed = 0;
    for (mask_t bits = s->full & ~closed_r; bits; ) {
        mask_t bit = LOWEST(bits); bits ^= bit;
        mask_t left = s->neighbour[lowest_index(bit)] & ~opened_r;
        if (left && (left & ~own) == 0 && bit != BIT(q)) freed[n_freed++] = left;
    }
    return has_definite_matching(freed, n_freed, popcount128(own) - 1);
}

/* The subset rule over the candidates in `costs`/`who`/`index_of`, measured
 * against every remaining customer not in `exclude` (0 in today's rule).
 * Returns the surviving count. */
static int subset_pass(const search_t *s, const int *ids, const mask_t *opens,
                       const int *sizes, int n_remaining, mask_t exclude,
                       int *costs, int *who, int *index_of, int count) {
    int kept = 0;
    for (int i = 0; i < count; i++) {
        int c = who[i];
        int at = index_of[i];
        mask_t own = opens[at];
        int own_size = sizes[at];
        int dominated = 0;
        for (int j = 0; j < n_remaining && !dominated; j++) {
            if (sizes[j] > own_size) continue;      /* cannot be a subset */
            int d = ids[j];
            if (d == c) continue;
            if (exclude && ((exclude >> d) & 1)) continue;   /* BM_SUBSET_RESTRICTED */
            mask_t other = opens[j];
            if ((other & ~own) == 0 && (other != own || d < c)) dominated = 1;
        }
        if (!dominated) { costs[kept] = costs[i]; who[kept] = c;
                          index_of[kept] = index_of[i]; kept++; }
    }
    /* Every candidate dominated by a non-candidate would empty the list;
     * keep the original in that case, as the Python does. */
    return kept ? kept : count;
}

/* Theorem 2 over the candidates in `costs`/`who`/`index_of`. Returns the
 * surviving count. */
static int better_move_pass(const search_t *s, mask_t closed, mask_t opened,
                            int *costs, int *who, int *index_of, int count,
                            mask_t *discarded) {
    /* Theorem 2, "better move". If S ++ [q] and S ++ [r, q] are both playable
     * and close(q, S u {r}) >= open(q, S u {r}), then any solution extending
     * S ++ [r] has one extending S ++ [q], so r can go. Theorem 1 is the case
     * where one q beats every r at once, which is why it runs first as a fast
     * path: it is O(R^2) where this is O(R^3).
     *
     * Only the cheapest few q are tried as dominators. Using a subset prunes
     * less but never wrongly -- the theorem justifies each pruning on its own,
     * so leaving some unfound costs nodes, not correctness. */
    if (count > 1) {
        int limit = s->better_move_dominators > 0 &&
                    s->better_move_dominators < count
                    ? s->better_move_dominators : count;
        /* Survivors are marked, not compacted in place. The dominator loop
         * below reads `who[qi]` across the candidate list while the compaction
         * writes survivors back into the same array: once anything is pruned,
         * `kept < ri`, and `who[kept] = who[ri]` clobbers a slot the loop has
         * yet to read. With `better_move_dominators = 0` the limit is `count`,
         * so later candidates were compared against whatever had been written
         * over their dominators -- pruning branches that held solutions and
         * returning **false refutations**. Found on `Warwick 1730`, which it
         * refuted at k = 9 against a true optimum of 9. */
        /* BM_OLD_CLOSE_COUNT restores the over-count, for measurement only. */
        const int count_finished = s->better_move_variant & BM_OLD_CLOSE_COUNT;
        int survives[128];
        mask_t freed[128];
        for (int i = 0; i < count; i++) survives[i] = 1;
        for (int ri = 0; ri < count; ri++) {
            int r = who[ri];
            mask_t closed_r = closed | BIT(r);
            mask_t opened_r = opened | s->neighbour[r];
            mask_t remaining_r = s->full & ~closed_r;
            int pruned = 0;

            /* Only an *earlier* candidate may dominate a later one. Without
             * that the relation can cycle -- q dominates r while r dominates q
             * -- and both are discarded together, taking the solution with
             * them. Ordering it makes the relation a forest: the first
             * candidate is never pruned, and whatever covers r is itself
             * covered by something earlier, transitively. That is what
             * produced false refutations on `Warwick 1730`, which was refuted
             * at k = 9 against a true optimum of 9. */
            for (int qi = 0; qi < limit && qi < ri && !pruned; qi++) {
                int q = who[qi];
                if (q == r) continue;

                /* S ++ [r, q] playable: q's cost once r has been played,
                 * measured as the paper measures it, with r closed and
                 * nothing else -- *not* the cheaper cost this search would
                 * charge q in the child, after r's free moves have closed.
                 * The theorem's proof plays q first and r second, and the
                 * paper's cost of r after q is this same number, so it is
                 * this check that keeps S ++ [q, r] playable. Brute force
                 * on 320 sparse instances at 12-15 customers found 726
                 * false prunings in 125M applications with the exact cost
                 * here, and none in 124M with this one. */
                if (popcount128((opened_r | s->neighbour[q]) & ~closed_r) > s->k)
                    continue;

                mask_t own = s->neighbour[q] & ~opened_r;
                int opened_by = popcount128(own);
                int closed_by = 0;
                int n_freed = 0;
                for (mask_t bits = remaining_r; bits; ) {
                    mask_t bit = LOWEST(bits); bits ^= bit;
                    mask_t left = s->neighbour[lowest_index(bit)] & ~opened_r;
                    /* close(q, S u {r}) counts the stacks q closes that r has
                     * not closed already. A customer with nothing left to
                     * open once r is played is finished by r alone -- a free
                     * move in the child, gone before q is played -- and the
                     * proof of Theorem 1 needs stacks closed *in addition* to
                     * those. Counting them made close(q, S u {r}) come out one
                     * too high and pruned r wrongly: the same brute force
                     * found 57 false prunings in 126M applications of the
                     * old count, every one an over-count of exactly this
                     * kind, and none in 124M once they are left out.
                     * `definite_move` and `subset_rule` never counted them:
                     * their `ids` skip size-0 customers. */
                    if ((left || count_finished) && (left & ~own) == 0) closed_by++;
                    /* The customers q frees at the child, q excluded, for
                     * the matching test of the repaired rule below. */
                    if (s->repaired_rules && left && (left & ~own) == 0 &&
                        bit != BIT(q))
                        freed[n_freed++] = left;
                }
                /* IsRepairedBetter: premises 3 and 4, and q hereditarily
                 * definite at cl(S u {r}) by the matching test there. */
                if (closed_by >= opened_by) rule_counts[RC_BM_PREFILTER]++;
                if (s->repaired_rules && closed_by >= opened_by &&
                    !has_definite_matching(freed, n_freed, opened_by - 1)) {
                    rule_counts[RC_BM_MATCH_FAIL]++;
                    continue;
                }
                if (closed_by >= opened_by) pruned = 1;
                /* The audit: some earlier survivor must meet the repaired
                 * premise, the citing q or any other (CodeNodeRepaired). */
                if (pruned && s->audit_repaired) {
                    if (!audit_repaired_better(s, closed_r, opened_r, q)) {
                        int covered = 0;
                        for (int qj = 0; qj < ri && !covered; qj++)
                            if (qj != qi && who[qj] != r &&
                                audit_repaired_better(s, closed_r, opened_r, who[qj]))
                                covered = 1;
                        if (!covered && !audit_node_bad) {
                            audit_node_bad = 1;
                            rule_counts[RC_AUDIT_BM_FAIL]++;
                        }
                    }
                }
            }
            survives[ri] = !pruned;
            if (pruned) rule_counts[RC_BM_PRUNED]++;
        }
        int kept = 0;
        mask_t gone = 0;
        for (int i = 0; i < count; i++)
            if (survives[i]) {
                costs[kept] = costs[i]; who[kept] = who[i];
                index_of[kept] = index_of[i]; kept++;
            } else {
                gone |= BIT(who[i]);
            }
        if (kept) { count = kept; if (discarded) *discarded = gone; }
    }
    return count;
}

/* Candidates surviving the dominance relations, written into `order` as
 * (cost, customer) pairs sorted by cost. Returns how many. */
static int dominance_filter(search_t *s, mask_t candidates,
                            mask_t closed, mask_t opened,
                            const int *ids, const mask_t *opens, const int *sizes,
                            int n_remaining, int open_now,
                            int *costs, int *who) {
    /* `closed` sits inside `opened`, so (opened | N[c]) & ~closed is the
     * disjoint union of (opened & ~closed) and (N[c] & ~opened): the cost is
     * `open_now` plus what the customer newly opens, which the caller counted
     * in the pass that found the free moves. Checked against the direct form on
     * 23,392 (state, candidate) pairs. */
    int index_of[128];
    int count = 0;
    for (int j = 0; j < n_remaining; j++) {
        int c = ids[j];
        if (!((candidates >> c) & 1)) continue;
        int cost = open_now + sizes[j];
        if (cost <= s->k) {
            costs[count] = cost; who[count] = c; index_of[count] = j; count++;
        }
    }
    if (!count || (!s->subset_rule && !s->definite_move && !s->better_move))
        goto sorted;
    rule_counts[RC_FILTER_CALLS]++;
    audit_node_bad = 0;

    /* Three dominance rules share this one list, and a rule is sound only
     * when every candidate it discards is *covered*: some candidate still
     * standing when the filter returns -- or a customer outside the candidate
     * set whose subtree an ancestor already searched, which is what `seen`
     * holds under old move -- admits a solution whenever the discarded one
     * does. Each rule is acyclic on its own input: definite move keeps one
     * candidate and stops; the subset relation with its index tie-break is a
     * strict partial order on the remaining customers; better move lets only
     * an earlier candidate cover a later one, so its first input survives.
     * Composition breaks that as soon as a later rule cites a candidate an
     * earlier rule has discarded. Better move used to run *before* the subset
     * rule: `r` went because `q` covered it, then `q` went because the subset
     * rule measured it against `r`, which it still saw among the remaining
     * customers -- a two-rule cycle, both gone and the solution with them,
     * 56 false refutations on sparse instances at 10-40 customers
     * (reports/ml_nature.md §15). So the subset rule now runs first, over the
     * remaining customers, none of which anything has discarded yet, and
     * better move runs last over the subset survivors alone. Every chain of
     * coverings then ends at a better-move survivor or at a `seen` customer,
     * and the answer cannot change -- only the cost. */
    if (s->definite_move) {
        int prefilter_passed = 0;
        for (int i = 0; i < count; i++) {
            int c = who[i];
            int at = index_of[i];
            mask_t own = opens[at];
            int opened_by = sizes[at];
            int closed_by = 0;
            for (int j = 0; j < n_remaining; j++)
                /* A larger set cannot sit inside a smaller one; the integer
                 * test skips most pairs before any 128-bit work. */
                if (sizes[j] <= opened_by && (opens[j] & ~own) == 0) closed_by++;
            if (closed_by >= opened_by) {
                rule_counts[RC_DEF_PREFILTER]++;
                prefilter_passed = 1;
            }
            if (closed_by >= opened_by && s->repaired_rules) {
                /* Chu & Stuckey's premise holds; the repaired rule also needs
                 * q hereditarily definite (the matching test over the
                 * customers q frees, q excluded). A q failing it may not
                 * stand for the others (Counterexample 4.5); a later q may. */
                mask_t freed[128];
                int n_freed = 0;
                for (int j = 0; j < n_remaining; j++)
                    if (ids[j] != c && sizes[j] <= opened_by && (opens[j] & ~own) == 0)
                        freed[n_freed++] = opens[j];
                if (!has_definite_matching(freed, n_freed, opened_by - 1)) {
                    rule_counts[RC_DEF_MATCH_FAIL]++;
                    continue;
                }
            }
            if (closed_by >= opened_by && s->audit_repaired) {
                /* The audit: the published rule fires on c; CodeNodeRepaired
                 * needs c hereditarily definite. */
                mask_t freed[128];
                int n_freed = 0;
                for (int j = 0; j < n_remaining; j++)
                    if (ids[j] != c && sizes[j] <= opened_by && (opens[j] & ~own) == 0)
                        freed[n_freed++] = opens[j];
                if (!has_definite_matching(freed, n_freed, opened_by - 1)) {
                    rule_counts[RC_AUDIT_DEF_FAIL]++;
                    rule_counts[RC_AUDIT_NODE_FAIL]++;
                }
            }
            if (closed_by >= opened_by) {
                /* q is at least as good as anything else here. */
                rule_counts[RC_DEF_FIRES]++;
                costs[0] = costs[i]; who[0] = c;
                count = 1;
                goto sorted;
            }
        }
        /* Reached only when no candidate fired: under the published rules a
         * prefilter pass always fires, so this counts the repair alone. */
        if (prefilter_passed) rule_counts[RC_DEF_LOST]++;
    }

    /* Today's order is subset rule then better move, for the reason above.
     * BM_OLD_RULE_ORDER runs them the other way round -- the pre-fix
     * composition, unsound -- so that the cost of the reordering can be
     * measured on its own (reports/ml_nature.md §31). */
    if (s->better_move_variant & BM_SUBSET_RESTRICTED) {
        /* Candidate composition, measured only: better move over every
         * candidate, then the subset rule over the survivors citing nothing
         * better move discarded. Better move's chains end at its survivors;
         * the subset rule's at a subset survivor or a `seen` customer; no
         * chain can re-enter the discarded set. */
        mask_t gone = 0;
        if (s->better_move)
            count = better_move_pass(s, closed, opened, costs, who, index_of, count, &gone);
        if (s->subset_rule)
            count = subset_pass(s, ids, opens, sizes, n_remaining, gone, costs, who, index_of, count);
    } else if (s->better_move_variant & BM_OLD_RULE_ORDER) {
        if (s->better_move)
            count = better_move_pass(s, closed, opened, costs, who, index_of, count, NULL);
        if (s->subset_rule)
            count = subset_pass(s, ids, opens, sizes, n_remaining, 0, costs, who, index_of, count);
    } else {
        if (s->subset_rule)
            count = subset_pass(s, ids, opens, sizes, n_remaining, 0, costs, who, index_of, count);
        if (s->better_move)
            count = better_move_pass(s, closed, opened, costs, who, index_of, count, NULL);
    }
    if (audit_node_bad) rule_counts[RC_AUDIT_NODE_FAIL]++;

sorted:
    if (s->fan_order == FAN_ORDER_DEGREE) {
        /* The fan order of reports/ml_nature.md §7's two-key rule: cheapest
         * first, ties to the candidate with the most neighbours not yet
         * closed, then index. `remaining` is the customers still open after
         * the free moves, so the degree is what the Python computes from
         * `masks[c] & remaining`. Measured behind this flag, never the
         * default (plan 2 §2.5a). */
        mask_t remaining = s->full & ~closed;
        int deg[128];
        for (int i = 0; i < count; i++)
            deg[i] = popcount128(s->neighbour[who[i]] & remaining) - 1;
        for (int i = 1; i < count; i++) {
            int ci = costs[i], wi = who[i], di = deg[i], j = i - 1;
            while (j >= 0 && (costs[j] > ci ||
                              (costs[j] == ci && (deg[j] < di ||
                                                  (deg[j] == di && who[j] > wi))))) {
                costs[j + 1] = costs[j]; who[j + 1] = who[j]; deg[j + 1] = deg[j]; j--;
            }
            costs[j + 1] = ci; who[j + 1] = wi; deg[j + 1] = di;
        }
        return count;
    }
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

/* Theorem 3, "old move": which of Q(S) survive into the child reached by
 * playing `customer`.
 *
 * q stays if the sequence with q reinserted at its ancestor remains playable,
 * and everything before the last move is playable already by q being in Q(S) --
 * so only the last move needs checking. Auto-closures can only lower that cost,
 * so checking the move alone is conservative in the safe direction. */
static mask_t inherit_old_moves(search_t *s, mask_t seen, mask_t closed,
                                mask_t opened, int customer) {
    mask_t kept = 0;
    for (mask_t bits = seen; bits; ) {
        mask_t bit = LOWEST(bits); bits ^= bit;
        int other = lowest_index(bit);
        int cost = popcount128((opened | s->neighbour[other] | s->neighbour[customer])
                               & ~(closed | bit));
        if (cost <= s->k) kept |= bit;
    }
    return kept;
}

static int search(search_t *s, mask_t closed, mask_t opened, mask_t seen) {
    int mark = s->depth;

    /* One pass over the remaining customers yields everything the node needs:
     * the stacks each would newly open, how many, and hence the free moves (the
     * ones that open nothing) and every candidate's cost. Three separate O(R)
     * passes over 128-bit words became one, and the arrays are built compacted
     * and in order so the dominance rules read them straight through.
     *
     * Closing a free move opens nothing by definition, so `opened` is unchanged
     * and these stay valid for whoever remains -- which is exactly the entries
     * kept here, since the free ones are the ones left out. */
    mask_t opens[128];
    int    ids[128];
    int    sizes[128];
    int    n_remaining = 0;
    mask_t free_now = 0;
    for (mask_t bits = s->full & ~closed; bits; ) {
        mask_t bit = LOWEST(bits); bits ^= bit;
        int c = lowest_index(bit);
        mask_t own = s->neighbour[c] & ~opened;
        int size = popcount128(own);
        if (!size) { free_now |= bit; continue; }
        ids[n_remaining] = c;
        opens[n_remaining] = own;
        sizes[n_remaining] = size;
        n_remaining++;
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
    seen &= remaining;
    mask_t candidates = s->old_move ? (remaining & ~seen) : remaining;
    if (s->restrict_frontier) {
        mask_t narrowed = remaining & opened;
        if (narrowed) candidates = narrowed;
    }

    int costs[128], who[128];
    int open_now = popcount128(opened & ~closed);
    int count = dominance_filter(s, candidates, closed, opened,
                                 ids, opens, sizes, n_remaining, open_now,
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
        mask_t inherited = (s->old_move && seen)
                         ? inherit_old_moves(s, seen, closed, opened, c) : 0;
        if (search(s, closed | BIT(c), opened | s->neighbour[c], inherited))
            return 1;
        s->depth = here;
        if (s->aborted) { s->depth = mark; return 0; }
        /* This branch is searched now, so a later sibling that could play it
         * instead would be repeating it. */
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
 * All four dominance rules are here, which is what Chu & Stuckey run: they
 * report "better move", "old move" and nogood recording all on together.
 *
 *   fan_order  : FAN_ORDER_INDEX (ties among equal-cost candidates by customer
 *                index, the default) or FAN_ORDER_DEGREE (by remaining degree,
 *                highest first, then index). Order changes which branches are
 *                visited first, never which are visited: the answer is the same.
 *   repaired_rules : 1 for the definite and better moves with the repaired
 *                premises proved sound in lean/MOSPFormalization/Search/
 *                (IsHereditarilyDefinite via HasDefiniteMatching, and
 *                IsRepairedBetter); 0 for the rules as Chu & Stuckey publish
 *                them, which can discard the last solution at a node
 *                (paper2/revised_algorithm.md, Counterexample 4.5);
 *                2 for the published rules with `CodeNodeRepaired` counted at
 *                every node (RC_AUDIT_*), which never changes the search.
 */
int cs_decide_rules(int n, int k,
                    const uint64_t *neighbours,
                    long long max_nodes, double seconds,
                    int subset_rule, int definite_move, int use_memo,
                    int restrict_frontier, long long memo_limit,
                    int better_move, int better_move_dominators, int old_move,
                    int fan_order, int better_move_variant, int repaired_rules,
                    int *out_path, long long *out_nodes, int *out_len) {
    *out_nodes = 0;
    *out_len = 0;
    memset(rule_counts, 0, sizeof rule_counts);
    if (n <= 0) return 1;

    search_t s;
    memset(&s, 0, sizeof s);
    s.n = n;
    s.k = k;
    s.subset_rule = subset_rule;
    s.definite_move = definite_move;
    s.better_move = better_move;
    s.better_move_dominators = better_move_dominators;
    s.better_move_variant = better_move_variant;
    s.old_move = old_move;
    /* 2 is the published rules with the audit counters (loop0007 item 07). */
    s.repaired_rules = repaired_rules == 1;
    s.audit_repaired = repaired_rules == 2;
    s.fan_order = fan_order;
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

/* The rule counters of this thread's last `cs_decide_rules` call, RC_COUNT
 * of them in the order of the enum above. Returns RC_COUNT. */
int cs_last_rule_counts(long long *out) {
    for (int i = 0; i < RC_COUNT; i++) out[i] = rule_counts[i];
    return RC_COUNT;
}

/* `cs_decide_rules` with the published definite and better moves, kept with
 * its signature for processes that loaded the library before
 * `repaired_rules` existed (loop0007 item 02). */
int cs_decide_variant(int n, int k,
                      const uint64_t *neighbours,
                      long long max_nodes, double seconds,
                      int subset_rule, int definite_move, int use_memo,
                      int restrict_frontier, long long memo_limit,
                      int better_move, int better_move_dominators, int old_move,
                      int fan_order, int better_move_variant,
                      int *out_path, long long *out_nodes, int *out_len) {
    return cs_decide_rules(n, k, neighbours, max_nodes, seconds,
                           subset_rule, definite_move, use_memo,
                           restrict_frontier, memo_limit,
                           better_move, better_move_dominators, old_move,
                           fan_order, better_move_variant, 0,
                           out_path, out_nodes, out_len);
}

/* `cs_decide` plus the fan-order flag; kept with its signature for the same
 * reason as `cs_decide`. Today's better-move rule, always. */
int cs_decide_fan(int n, int k,
                  const uint64_t *neighbours,
                  long long max_nodes, double seconds,
                  int subset_rule, int definite_move, int use_memo,
                  int restrict_frontier, long long memo_limit,
                  int better_move, int better_move_dominators, int old_move,
                  int fan_order,
                  int *out_path, long long *out_nodes, int *out_len) {
    return cs_decide_variant(n, k, neighbours, max_nodes, seconds,
                             subset_rule, definite_move, use_memo,
                             restrict_frontier, memo_limit,
                             better_move, better_move_dominators, old_move,
                             fan_order, 0, out_path, out_nodes, out_len);
}

/* The original entry point, kept with its signature so a process that loaded
 * the library before `fan_order` existed -- a multi-day `benchmarks.recertify`
 * run forks its workers late -- calls a function that still means what it
 * meant. Ties by customer index, as always. */
int cs_decide(int n, int k,
              const uint64_t *neighbours,
              long long max_nodes, double seconds,
              int subset_rule, int definite_move, int use_memo,
              int restrict_frontier, long long memo_limit,
              int better_move, int better_move_dominators, int old_move,
              int *out_path, long long *out_nodes, int *out_len) {
    return cs_decide_fan(n, k, neighbours, max_nodes, seconds,
                         subset_rule, definite_move, use_memo,
                         restrict_frontier, memo_limit,
                         better_move, better_move_dominators, old_move,
                         FAN_ORDER_INDEX, out_path, out_nodes, out_len);
}
