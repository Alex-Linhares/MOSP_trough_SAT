/* C helper for paper2/false_refutation_hunt.py: one candidate graph, evaluated.
 *
 * The production search is included verbatim, so every decide call, the
 * instrumented walk and the judge run the very `dominance_filter`,
 * `inherit_old_moves`, `search` and memo the solver runs.
 *
 * - fr_decide: cs_decide_rules itself, published (repaired = 0) or repaired (1).
 * - fr_walk: the published search replayed line for line, with the *repaired*
 *   search as the judge of whether a state has a solution. The judge is
 *   consulted only where the published search failed (and on the root's
 *   children), so it is off the path of a search that succeeds at once.
 *   Its verdicts steer the fitness only; a hit is certified by a witness.
 * - fr_oracle: an exact subset DP sharing no code with the search, for
 *   cross-checks on small graphs only (n <= 22), never on the hot path.
 *
 *   gcc -O3 -march=native -shared -fPIC -o paper2/_false_refutation_hunt.so \
 *       paper2/false_refutation_hunt.c
 *
 * Graphs are closed-neighbourhood masks of n <= 64 customers.
 */

#include <malloc.h>
#include "../satisfiability/customer_search.c"

#define FR_MAXN 64
#define FR_ORACLE_MAXN 22

int fr_init(void) {
    /* Without a fixed threshold glibc raises it after the first free of a
     * mapped block, and every 16 MB memo calloc would then memset. */
    mallopt(M_MMAP_THRESHOLD, 1 << 20);
    return 0;
}

/* ---------------------------------------------------------------------- */
/* One production decide call: cs_decide_rules itself.                    */
/* cfg = {definite, subset, better, dominators, old, memo, fan}           */

int fr_decide(int n, const uint64_t *m, int k, const int *cfg, int repaired,
              long long max_nodes, int *path, long long *nodes, int *len) {
    uint64_t packed[2 * FR_MAXN];
    if (n < 1 || n > FR_MAXN) return -3;
    for (int i = 0; i < n; i++) { packed[2 * i] = m[i]; packed[2 * i + 1] = 0; }
    return cs_decide_rules(n, k, packed, max_nodes, 0.0,
                           cfg[1], cfg[0], cfg[5], 0, 1 << 19,
                           cfg[2], cfg[3], cfg[4], cfg[6], 0, repaired,
                           path, nodes, len);
}

/* ---------------------------------------------------------------------- */
/* The judge: the repaired search (definite + subset, old move, memo)     */
/* from a state, sound and complete. Its memo is shared within one walk:  */
/* every state the repaired search refutes at this k has no solution.     */

typedef struct {
    search_t  s;
    memo_t    yes, no;          /* verdict caches, keyed closed | bit 127 */
    long long nodes_left;
    long long per_call;
    long long calls, aborts;
    int       path[128];
} judge_t;

static __thread judge_t J;

static int judge_open(int n, int k, mask_t *nb, long long per_call, long long total) {
    memset(&J, 0, sizeof J);
    J.s.n = n; J.s.k = k;
    J.s.definite_move = 1; J.s.subset_rule = 1; J.s.better_move = 0;
    J.s.better_move_dominators = 4; J.s.old_move = 1; J.s.use_memo = 1;
    J.s.repaired_rules = 1;
    J.s.neighbour = nb;
    J.s.full = n == 128 ? ~(mask_t) 0 : (BIT(n) - 1);
    J.s.path = J.path;
    J.per_call = per_call;
    J.nodes_left = total;
    if (!memo_init(&J.s.memo, 1u << 20, 1u << 19)) return 0;
    if (!memo_init(&J.yes, 1u << 16, 1u << 15)) return 0;
    if (!memo_init(&J.no, 1u << 16, 1u << 15)) return 0;
    return 1;
}

static void judge_close(void) {
    free(J.s.memo.slots); free(J.yes.slots); free(J.no.slots);
    memset(&J.s.memo, 0, sizeof J.s.memo);
}

/* 1 the state has a solution, 0 it has none, -1 the budget ran out. */
static int judge(mask_t closed) {
    mask_t key = closed | BIT(127);
    if (memo_has(&J.yes, key)) return 1;
    if (memo_has(&J.no, key)) return 0;
    if (J.nodes_left <= 0) { J.aborts++; return -1; }
    mask_t opened = 0;
    for (mask_t b = closed; b; ) { mask_t bit = LOWEST(b); b ^= bit; opened |= J.s.neighbour[lowest_index(bit)]; }
    if (popcount128(opened & ~closed) > J.s.k) { memo_add(&J.no, key); return 0; }
    J.s.nodes = 0; J.s.aborted = 0; J.s.depth = 0;
    J.s.max_nodes = J.per_call < J.nodes_left ? J.per_call : J.nodes_left;
    J.calls++;
    int r = search(&J.s, closed, opened, 0);
    J.nodes_left -= J.s.nodes;
    if (J.s.aborted) { J.aborts++; return -1; }
    memo_add(r ? &J.yes : &J.no, key);
    return r;
}

/* ---------------------------------------------------------------------- */
/* The walk: `search` of customer_search.c line for line, instrumented.   */

enum {
    W_NODES,          /* children visited, as `nodes` of the production search */
    W_EXPANDED,       /* nodes expanded */
    W_FILTER_LOSS,    /* a falsely refuted node where no kept child had a solution but a candidate did */
    W_DEF_LOSS,       /* ... of which the definite move fired */
    W_SEEN_LOSS,      /* ... where only candidates barred by old move had one */
    W_MEMO_POISON,    /* memo hit on a state with a solution */
    W_FALSE_REF,      /* nodes that returned false and have a solution */
    W_LOSS_MIN_DEPTH, /* depth of the shallowest filter loss, or 99 */
    W_ANSWER,         /* 1 sat, 0 unsat, -1 aborted */
    W_ROOT_KEPT_SOLV, /* root children kept with a solution */
    W_ROOT_REFUTED,   /* ... falsely refuted */
    W_AUDIT_FAIL,     /* nodes failing CodeNodeRepaired (published rules only) */
    W_JUDGE_CALLS,
    W_JUDGE_ABORTS,
    W_COUNT
};

static __thread long long W[W_COUNT];
static __thread double W_path;
static __thread mask_t W_first_loss;
static __thread int W_have_loss;

static int wsearch(search_t *s, mask_t closed, mask_t opened, mask_t seen, int depth) {
    int mark = s->depth;
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
    if (s->use_memo && memo_has(&s->memo, closed)) {
        if (judge(closed) == 1) W[W_MEMO_POISON]++;
        s->depth = mark;
        return 0;
    }

    mask_t remaining = s->full & ~closed;
    seen &= remaining;
    mask_t seen_here = seen;
    mask_t candidates = s->old_move ? (remaining & ~seen) : remaining;

    int costs[128], who[128];
    int open_now = popcount128(opened & ~closed);
    long long fires = rule_counts[RC_DEF_FIRES];
    long long audit = rule_counts[RC_AUDIT_NODE_FAIL];
    int count = dominance_filter(s, candidates, closed, opened,
                                 ids, opens, sizes, n_remaining, open_now,
                                 costs, who);
    int fired = rule_counts[RC_DEF_FIRES] > fires;
    if (rule_counts[RC_AUDIT_NODE_FAIL] > audit) W[W_AUDIT_FAIL]++;
    W[W_EXPANDED]++;

    int refuted = 0;          /* kept children tried, failed, and with a solution */
    for (int i = 0; i < count; i++) {
        int c = who[i];
        s->nodes++;
        if (s->max_nodes >= 0 && s->nodes > s->max_nodes) {
            s->aborted = 1; s->depth = mark; return 0;
        }
        int here = s->depth;
        s->path[s->depth++] = c;
        mask_t inherited = (s->old_move && seen)
                         ? inherit_old_moves(s, seen, closed, opened, c) : 0;
        if (wsearch(s, closed | BIT(c), opened | s->neighbour[c], inherited, depth + 1)) {
            W_path += (double) refuted / (refuted + 1.0) / (1.0 + depth);
            if (depth == 0) {
                int untried = 0;
                for (int j = i + 1; j < count; j++)
                    if (judge(closed | BIT(who[j])) == 1) untried++;
                W[W_ROOT_KEPT_SOLV] = refuted + 1 + untried;
                W[W_ROOT_REFUTED] = refuted;
            }
            return 1;
        }
        s->depth = here;
        if (s->aborted) { s->depth = mark; return 0; }
        if (judge(closed | BIT(c)) == 1) refuted++;
        seen |= BIT(c);
    }

    /* The node failed. Does it have a solution? */
    if (judge(closed) == 1) {
        W[W_FALSE_REF]++;
        if (!refuted) {
            int cand_solv = 0, seen_solv = 0;
            for (int j = 0; j < n_remaining && !cand_solv; j++) {
                int c = ids[j];
                if (open_now + sizes[j] > s->k) continue;
                int kept = 0;
                for (int i = 0; i < count; i++) if (who[i] == c) kept = 1;
                if (kept) continue;
                if ((candidates >> c) & 1) {
                    if (judge(closed | BIT(c)) == 1) cand_solv++;
                } else if (((seen_here >> c) & 1) && !seen_solv) {
                    if (judge(closed | BIT(c)) == 1) seen_solv++;
                }
            }
            if (cand_solv) {
                W[W_FILTER_LOSS]++;
                if (fired) W[W_DEF_LOSS]++;
                if (depth < W[W_LOSS_MIN_DEPTH]) W[W_LOSS_MIN_DEPTH] = depth;
                if (!W_have_loss) { W_have_loss = 1; W_first_loss = closed; }
            } else if (seen_solv) {
                W[W_SEEN_LOSS]++;
            }
        }
    }
    if (depth == 0) { W[W_ROOT_KEPT_SOLV] = refuted; W[W_ROOT_REFUTED] = refuted; }
    if (s->use_memo && !s->aborted) memo_add(&s->memo, closed);
    s->depth = mark;
    return 0;
}

/* Walk the published search (audited) at k on the graph. out[W_COUNT] gets
 * the counters, *path_score the success-path score, *first_loss the first
 * filter-loss state (low 64 bits, or -1). Returns the answer. */
int fr_walk(int n, const uint64_t *m, int k, const int *cfg, long long max_nodes,
            long long judge_per_call, long long judge_total,
            long long *out, double *path_score, long long *first_loss) {
    if (n < 1 || n > FR_MAXN) return -3;
    search_t s;
    memset(&s, 0, sizeof s);
    memset(rule_counts, 0, sizeof rule_counts);
    memset(W, 0, sizeof W);
    W[W_LOSS_MIN_DEPTH] = 99;
    W_path = 0.0; W_have_loss = 0; W_first_loss = 0;
    int path[128];
    mask_t nb[FR_MAXN];
    for (int i = 0; i < n; i++) nb[i] = m[i];
    s.n = n; s.k = k;
    s.subset_rule = cfg[1]; s.definite_move = cfg[0]; s.better_move = cfg[2];
    s.better_move_dominators = cfg[3]; s.better_move_variant = 0; s.old_move = cfg[4];
    s.repaired_rules = 0; s.audit_repaired = 1;
    s.fan_order = cfg[6]; s.use_memo = cfg[5]; s.restrict_frontier = 0;
    s.max_nodes = max_nodes; s.deadline = 0; s.path = path;
    s.neighbour = nb;
    s.full = n == 128 ? ~(mask_t) 0 : (BIT(n) - 1);
    if (s.use_memo && !memo_init(&s.memo, 1u << 20, 1u << 19)) return -2;
    if (!judge_open(n, k, nb, judge_per_call, judge_total)) { free(s.memo.slots); return -2; }
    int found = wsearch(&s, 0, 0, 0, 0);
    W[W_JUDGE_CALLS] = J.calls;
    W[W_JUDGE_ABORTS] = J.aborts;
    judge_close();
    free(s.memo.slots);
    W[W_ANSWER] = found ? 1 : (s.aborted ? -1 : 0);
    W[W_NODES] = s.nodes;
    for (int i = 0; i < W_COUNT; i++) out[i] = W[i];
    *path_score = W_path;
    *first_loss = W_have_loss ? (long long) (uint64_t) W_first_loss : -1;
    return (int) W[W_ANSWER];
}

/* ---------------------------------------------------------------------- */
/* The oracle, for cross-checks only: best[T] = min over c not in T of    */
/* max(|O(T + c) - T|, best[T + c]); the optimum is best[0].              */

int fr_oracle(int n, const uint64_t *m64) {
    if (n < 1 || n > FR_ORACLE_MAXN) return -1;
    uint32_t m[FR_ORACLE_MAXN];
    for (int i = 0; i < n; i++) m[i] = (uint32_t) m64[i];
    uint32_t full = (1u << n) - 1;
    uint32_t *O = malloc(sizeof(uint32_t) << n);
    uint8_t *best = malloc((size_t) 1 << n);
    if (!O || !best) { free(O); free(best); return -1; }
    O[0] = 0;
    for (uint32_t T = 1; T <= full; T++) {
        uint32_t low = T & -T;
        O[T] = O[T ^ low] | m[__builtin_ctz(T)];
    }
    best[full] = 0;
    for (int64_t t = (int64_t) full - 1; t >= 0; t--) {
        uint32_t T = (uint32_t) t;
        int b = 255;
        for (uint32_t rem = full & ~T; rem; ) {
            uint32_t low = rem & -rem; rem ^= low;
            int cost = __builtin_popcount(O[T | low] & ~T);
            int v = best[T | low];
            if (cost > v) v = cost;
            if (v < b) b = v;
        }
        best[T] = (uint8_t) b;
    }
    int r = best[0];
    free(O); free(best);
    return r;
}
