/* Exact treewidth for small graphs, two ways.
 *
 * 1. tw_dp: the O(2^n * n * poly) subset recurrence of Bodlaender, Fomin,
 *    Koster, Kratsch & Thilikos ("On exact algorithms for treewidth", 2012):
 *
 *        TW(S) = min_{v in S} max( TW(S \ {v}), |Q(S \ {v}, v)| ),   TW({}) = 0,
 *
 *    where Q(S, v) is the set of vertices w outside S u {v} reachable from v
 *    by a path whose interior lies in S -- the degree of v in the graph with
 *    S eliminated. tw(G) = TW(V). One byte per subset, so n <= 26 is 64 MB.
 *    Also returns an elimination ordering of that width (the upper-bound
 *    witness a third party can check by eliminating along it).
 *
 * 2. tw_decide: "is tw(G) <= k?" by depth-first search over elimination
 *    prefixes S with a hash set of prefixes shown infeasible, for the sizes
 *    the DP cannot hold in memory (n <= 64). Two safe reductions are applied
 *    at every node: a vertex whose neighbourhood in the eliminated graph is a
 *    clique (simplicial) or a clique plus one vertex (almost simplicial) with
 *    degree <= k is eliminated at once -- eliminating it yields a minor, so
 *    the answer is unchanged; a simplicial vertex of degree > k refutes the
 *    node outright (it sits in a clique of size > k + 1). Branching then
 *    tries the remaining vertices of degree <= k, smallest degree first. The
 *    search stops at a node budget and reports "unknown"; every answer it
 *    gives is exact.
 *
 * Neither routine is a bound on MOSP and nothing here touches the solver.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef uint64_t mask_t;

static inline int popcnt(mask_t x) { return __builtin_popcountll(x); }
static inline int ctz(mask_t x) { return __builtin_ctzll(x); }

/* Q(S, v): the neighbourhood of v in the graph with S eliminated. */
static inline mask_t q_set(const mask_t *adj, mask_t S, int v) {
    mask_t nb = adj[v];
    mask_t reach = nb & S;
    mask_t seen = 0;
    while (reach != seen) {
        mask_t fresh = reach & ~seen;
        seen = reach;
        while (fresh) {
            int u = ctz(fresh);
            fresh &= fresh - 1;
            nb |= adj[u];
        }
        reach = nb & S;
    }
    return nb & ~S & ~((mask_t)1 << v);
}

/* ---------------------------------------------------------------------- */
/* 1. the subset DP                                                        */
/* ---------------------------------------------------------------------- */

/* Returns the treewidth, writes an elimination ordering of that width into
 * `order` (length n, first eliminated first). Returns -1 on allocation
 * failure, -2 if n is out of range. */
int tw_dp(int n, const mask_t *adj, int *order) {
    if (n <= 0) return 0;
    if (n > 26) return -2;
    size_t count = (size_t)1 << n;
    uint8_t *tw = (uint8_t *)malloc(count);
    if (!tw) return -1;
    tw[0] = 0;
    for (mask_t S = 1; S < (mask_t)count; ++S) {
        int best = n;
        mask_t rest = S;
        while (rest) {
            int v = ctz(rest);
            rest &= rest - 1;
            mask_t T = S & ~((mask_t)1 << v);
            int prior = tw[T];
            if (prior >= best) continue;
            int q = popcnt(q_set(adj, T, v));
            int w = prior > q ? prior : q;
            if (w < best) best = w;
        }
        tw[S] = (uint8_t)best;
    }
    mask_t full = (count - 1);
    int width = tw[full];
    /* reconstruct: v is the last vertex eliminated among S */
    mask_t S = full;
    for (int pos = n - 1; pos >= 0; --pos) {
        mask_t rest = S;
        int chosen = -1;
        while (rest) {
            int v = ctz(rest);
            rest &= rest - 1;
            mask_t T = S & ~((mask_t)1 << v);
            int q = popcnt(q_set(adj, T, v));
            int w = tw[T] > q ? tw[T] : q;
            if (w == tw[S]) { chosen = v; break; }
        }
        order[pos] = chosen;
        S &= ~((mask_t)1 << chosen);
    }
    free(tw);
    return width;
}

/* ---------------------------------------------------------------------- */
/* 2. the decision search                                                  */
/* ---------------------------------------------------------------------- */

typedef struct {
    mask_t *keys;
    uint8_t *used;
    size_t cap;
    size_t size;
} hset_t;

static int hset_init(hset_t *h, size_t cap) {
    h->cap = cap;
    h->size = 0;
    h->keys = (mask_t *)malloc(cap * sizeof(mask_t));
    h->used = (uint8_t *)calloc(cap, 1);
    return h->keys && h->used;
}

static void hset_free(hset_t *h) { free(h->keys); free(h->used); }

static inline size_t hmix(mask_t x, size_t cap) {
    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33;
    return (size_t)(x & (cap - 1));
}

static int hset_has(const hset_t *h, mask_t k) {
    size_t i = hmix(k, h->cap);
    while (h->used[i]) {
        if (h->keys[i] == k) return 1;
        i = (i + 1) & (h->cap - 1);
    }
    return 0;
}

/* returns 0 when the set is full (caller stops memoising) */
static int hset_add(hset_t *h, mask_t k) {
    if (h->size * 2 >= h->cap) return 0;
    size_t i = hmix(k, h->cap);
    while (h->used[i]) {
        if (h->keys[i] == k) return 1;
        i = (i + 1) & (h->cap - 1);
    }
    h->used[i] = 1;
    h->keys[i] = k;
    h->size++;
    return 1;
}

typedef struct {
    int n;
    int k;
    const mask_t *adj;
    mask_t full;
    hset_t failed;
    long long nodes;
    long long budget;
    int aborted;
    int memo_ok;
    int *order;      /* elimination ordering found, first eliminated first */
} ctx_t;

/* Is Q a clique in the eliminated graph (all pairs adjacent through S)? With
 * `allow_one`, is it a clique plus at most one vertex? Returns 1 / 0. */
static int is_clique_after(const mask_t *adj, mask_t S, mask_t Q, int allow_one) {
    int misses = 0;
    mask_t rest = Q;
    mask_t bad = 0;
    while (rest) {
        int u = ctz(rest);
        rest &= rest - 1;
        mask_t nu = q_set(adj, S, u);
        mask_t need = Q & ~((mask_t)1 << u);
        if ((need & ~nu) != 0) {
            misses++;
            bad |= (mask_t)1 << u;
        }
    }
    if (misses == 0) return 1;
    if (!allow_one) return 0;
    /* almost simplicial: one vertex w such that Q \ {w} is a clique */
    rest = bad;
    while (rest) {
        int w = ctz(rest);
        rest &= rest - 1;
        mask_t Qw = Q & ~((mask_t)1 << w);
        mask_t r2 = Qw;
        int ok = 1;
        while (r2 && ok) {
            int u = ctz(r2);
            r2 &= r2 - 1;
            mask_t nu = q_set(adj, S, u);
            if (((Qw & ~((mask_t)1 << u)) & ~nu) != 0) ok = 0;
        }
        if (ok) return 1;
    }
    return 0;
}

/* Greedy minimum-degree lower bound (MMD) of the eliminated graph: a lower
 * bound on its treewidth, so > k refutes the node. */
static int mmd_after(const mask_t *adj, int n, mask_t S, mask_t full) {
    mask_t alive = full & ~S;
    mask_t deg_adj[64];
    int cnt = popcnt(alive);
    mask_t rest = alive;
    while (rest) {
        int u = ctz(rest);
        rest &= rest - 1;
        deg_adj[u] = q_set(adj, S, u);
    }
    int best = 0;
    while (cnt > 1) {
        int vmin = -1, dmin = n + 1;
        rest = alive;
        while (rest) {
            int u = ctz(rest);
            rest &= rest - 1;
            int d = popcnt(deg_adj[u] & alive);
            if (d < dmin) { dmin = d; vmin = u; }
        }
        if (dmin > best) best = dmin;
        alive &= ~((mask_t)1 << vmin);
        cnt--;
    }
    return best;
}

static int feasible(ctx_t *c, mask_t S, int depth) {
    if (S == c->full) return 1;
    if (c->aborted) return 0;
    if (++c->nodes > c->budget) { c->aborted = 1; return 0; }
    if (c->memo_ok && hset_has(&c->failed, S)) return 0;

    /* reductions */
    mask_t S0 = S;
    int depth0 = depth;
    int changed = 1;
    while (changed && S != c->full) {
        changed = 0;
        mask_t rest = c->full & ~S;
        while (rest) {
            int v = ctz(rest);
            rest &= rest - 1;
            mask_t Q = q_set(c->adj, S, v);
            int d = popcnt(Q);
            if (d <= 1) {                         /* isolated or pendant: simplicial */
                if (d > c->k) { goto fail; }      /* an edge needs width 1 */
                c->order[depth++] = v; S |= (mask_t)1 << v; changed = 1; continue;
            }
            if (is_clique_after(c->adj, S, Q, 0)) {
                if (d > c->k) { goto fail; }      /* clique of size d + 1 */
                c->order[depth++] = v; S |= (mask_t)1 << v; changed = 1; continue;
            }
            if (d <= c->k && is_clique_after(c->adj, S, Q, 1)) {
                c->order[depth++] = v; S |= (mask_t)1 << v; changed = 1; continue;
            }
        }
    }
    if (S == c->full) return 1;
    if (mmd_after(c->adj, c->n, S, c->full) > c->k) goto fail;

    /* branch: candidates of degree <= k, smallest degree first */
    {
        int cand[64], deg[64], m = 0;
        mask_t rest = c->full & ~S;
        while (rest) {
            int v = ctz(rest);
            rest &= rest - 1;
            int d = popcnt(q_set(c->adj, S, v));
            if (d <= c->k) { cand[m] = v; deg[m] = d; m++; }
        }
        for (int i = 1; i < m; ++i) {           /* insertion sort by degree */
            int cv = cand[i], cd = deg[i], j = i - 1;
            while (j >= 0 && deg[j] > cd) { cand[j + 1] = cand[j]; deg[j + 1] = deg[j]; j--; }
            cand[j + 1] = cv; deg[j + 1] = cd;
        }
        for (int i = 0; i < m; ++i) {
            c->order[depth] = cand[i];
            if (feasible(c, S | ((mask_t)1 << cand[i]), depth + 1)) return 1;
            if (c->aborted) return 0;
        }
    }
fail:
    if (c->memo_ok) {
        if (!hset_add(&c->failed, S0)) c->memo_ok = 0;
        else if (S != S0 && !hset_add(&c->failed, S)) c->memo_ok = 0;
    }
    (void)depth0;
    return 0;
}

/* Returns 1 (tw <= k, `order` holds an elimination ordering of width <= k),
 * 0 (tw > k), or 2 (budget exhausted). `nodes_out` receives the node count. */
int tw_decide(int n, const mask_t *adj, int k, long long budget,
              long long memo_capacity, int *order, long long *nodes_out) {
    if (n > 64) return -2;
    ctx_t c;
    c.n = n; c.k = k; c.adj = adj;
    c.full = (n == 64) ? ~(mask_t)0 : (((mask_t)1 << n) - 1);
    c.nodes = 0; c.budget = budget; c.aborted = 0; c.order = order;
    size_t cap = 1 << 16;
    while ((long long)cap < memo_capacity * 2 && cap < ((size_t)1 << 30)) cap <<= 1;
    c.memo_ok = hset_init(&c.failed, cap);
    int result = feasible(&c, 0, 0);
    *nodes_out = c.nodes;
    hset_free(&c.failed);
    if (c.aborted) return 2;
    return result;
}
