/* loop0013 item 02: the vertex-isoperimetric profile f(t) = min_{|C|=t} |N[C]|.
 *
 * Two routines, reached through ctypes from learning/obstruction_expansion.py:
 *
 *   exact_profile   every subset of an n <= 22 vertex graph, by the recurrence
 *                   cover(S) = cover(S - low(S)) | N[low(S)]; gives f(t) and
 *                   one minimiser per t exactly.
 *   search_profile  tabu search on swaps per level t, restarted from external
 *                   seeds (cliques, witness prefix sets), BFS balls of radius
 *                   1 and 2 around every vertex, and the best set at t -/+ 1;
 *                   gives incumbents fhat(t) >= f(t) with the set attaining
 *                   each. An incumbent proves f(t) <= |N[C]| and nothing more.
 *
 * Graphs are closed neighbourhoods as bit masks, W 64-bit words per vertex.
 * Nothing here is a bound: the exact routine is exact, the search is a search.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXW 12         /* up to 768 vertices (raised from 4 = 256 for item 07; the open classes have up to 712) */
#define TOPK 6          /* candidate shortlist per side of a swap */

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static inline int popw(const uint64_t *a, int W) {
    int c = 0;
    for (int i = 0; i < W; i++) c += __builtin_popcountll(a[i]);
    return c;
}

static uint64_t rng_state = 88172645463325252ULL;
static inline uint64_t rng_next(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return rng_state;
}

/* ------------------------------------------------------------------------ */
/* exact at n <= 22                                                          */
/* ------------------------------------------------------------------------ */

int exact_profile(int n, const uint32_t *nbr, int *f_out, uint32_t *set_out) {
    if (n < 1 || n > 24) return -1;
    uint32_t total = 1u << n;
    uint32_t *cover = (uint32_t *)malloc((size_t)total * sizeof(uint32_t));
    if (!cover) return -2;
    for (int t = 0; t <= n; t++) { f_out[t] = n + 1; set_out[t] = 0; }
    cover[0] = 0;
    f_out[0] = 0;
    for (uint32_t mask = 1; mask < total; mask++) {
        uint32_t low = mask & (0u - mask);
        uint32_t c = cover[mask ^ low] | nbr[__builtin_ctz(low)];
        cover[mask] = c;
        int t = __builtin_popcount(mask);
        int cc = __builtin_popcount(c);
        if (cc < f_out[t]) { f_out[t] = cc; set_out[t] = mask; }
    }
    free(cover);
    return 0;
}

/* ------------------------------------------------------------------------ */
/* the search                                                                */
/* ------------------------------------------------------------------------ */

typedef struct {
    int n, W, t;
    const uint64_t *nbr;        /* n * W closed neighbourhoods */
    uint64_t C[MAXW];           /* the current set */
    int cnt[64 * MAXW];         /* cover multiplicity per vertex */
    uint64_t Z[MAXW], O[MAXW];  /* cnt == 0, cnt == 1 */
    int size, value;            /* |C|, |N[C]| */
} State;

static void recompute(State *s) {
    memset(s->cnt, 0, sizeof(int) * s->n);
    s->size = 0;
    for (int v = 0; v < s->n; v++) {
        if (s->C[v >> 6] >> (v & 63) & 1) {
            s->size++;
            const uint64_t *nv = s->nbr + (size_t)v * s->W;
            for (int i = 0; i < s->W; i++) {
                uint64_t bits = nv[i];
                while (bits) { int b = __builtin_ctzll(bits); bits &= bits - 1; s->cnt[(i << 6) | b]++; }
            }
        }
    }
    memset(s->Z, 0, sizeof(uint64_t) * s->W);
    memset(s->O, 0, sizeof(uint64_t) * s->W);
    s->value = 0;
    for (int v = 0; v < s->n; v++) {
        if (s->cnt[v] == 0) s->Z[v >> 6] |= 1ULL << (v & 63);
        else { s->value++; if (s->cnt[v] == 1) s->O[v >> 6] |= 1ULL << (v & 63); }
    }
}

static void refresh_zo(State *s) {
    memset(s->Z, 0, sizeof(uint64_t) * s->W);
    memset(s->O, 0, sizeof(uint64_t) * s->W);
    s->value = 0;
    for (int v = 0; v < s->n; v++) {
        if (s->cnt[v] == 0) s->Z[v >> 6] |= 1ULL << (v & 63);
        else { s->value++; if (s->cnt[v] == 1) s->O[v >> 6] |= 1ULL << (v & 63); }
    }
}

static void add_vertex(State *s, int w) {
    s->C[w >> 6] |= 1ULL << (w & 63);
    s->size++;
    const uint64_t *nw = s->nbr + (size_t)w * s->W;
    for (int i = 0; i < s->W; i++) {
        uint64_t bits = nw[i];
        while (bits) { int b = __builtin_ctzll(bits); bits &= bits - 1; s->cnt[(i << 6) | b]++; }
    }
    refresh_zo(s);
}

static void remove_vertex(State *s, int u) {
    s->C[u >> 6] &= ~(1ULL << (u & 63));
    s->size--;
    const uint64_t *nu = s->nbr + (size_t)u * s->W;
    for (int i = 0; i < s->W; i++) {
        uint64_t bits = nu[i];
        while (bits) { int b = __builtin_ctzll(bits); bits &= bits - 1; s->cnt[(i << 6) | b]--; }
    }
    refresh_zo(s);
}

static inline int gain_of(const State *s, int w) {       /* new cover if w enters */
    const uint64_t *nw = s->nbr + (size_t)w * s->W;
    int g = 0;
    for (int i = 0; i < s->W; i++) g += __builtin_popcountll(nw[i] & s->Z[i]);
    return g;
}

static inline int loss_of(const State *s, int u) {       /* cover lost if u leaves */
    const uint64_t *nu = s->nbr + (size_t)u * s->W;
    int l = 0;
    for (int i = 0; i < s->W; i++) l += __builtin_popcountll(nu[i] & s->O[i]);
    return l;
}

static inline int swap_delta(const State *s, int u, int w) {
    /* remove u then add w: + |N[w] & Z| - |N[u] & O & ~N[w]| */
    const uint64_t *nu = s->nbr + (size_t)u * s->W;
    const uint64_t *nw = s->nbr + (size_t)w * s->W;
    int d = 0;
    for (int i = 0; i < s->W; i++) {
        d += __builtin_popcountll(nw[i] & s->Z[i]);
        d -= __builtin_popcountll(nu[i] & s->O[i] & ~nw[i]);
    }
    return d;
}

/* grow or shrink C greedily to size t */
static void adjust(State *s, int t) {
    while (s->size < t) {
        int best = -1, bg = 1 << 30, ties = 0;
        for (int w = 0; w < s->n; w++) {
            if (s->C[w >> 6] >> (w & 63) & 1) continue;
            int g = gain_of(s, w);
            if (g < bg) { bg = g; best = w; ties = 1; }
            else if (g == bg && (rng_next() % (uint64_t)(++ties)) == 0) best = w;
        }
        add_vertex(s, best);
    }
    while (s->size > t) {
        int best = -1, bl = -1, ties = 0;
        for (int u = 0; u < s->n; u++) {
            if (!(s->C[u >> 6] >> (u & 63) & 1)) continue;
            int l = loss_of(s, u);
            if (l > bl) { bl = l; best = u; ties = 1; }
            else if (l == bl && (rng_next() % (uint64_t)(++ties)) == 0) best = u;
        }
        remove_vertex(s, best);
    }
}

/* one tabu run from the current state; updates best_val / best_set */
static void tabu_run(State *s, int max_swaps, int stall, int tenure, double deadline,
                     int *best_val, uint64_t *best_set) {
    int n = s->n, W = s->W;
    int *tabu_until = (int *)calloc((size_t)n, sizeof(int));
    int run_best = s->value, since = 0;
    if (s->value < *best_val) { *best_val = s->value; memcpy(best_set, s->C, sizeof(uint64_t) * W); }
    int ins[TOPK], ing[TOPK], outs[TOPK], outl[TOPK];
    for (int it = 1; it <= max_swaps; it++) {
        if ((it & 63) == 0 && now_sec() > deadline) break;
        if (s->size == 0 || s->size == n) break;
        /* shortlist entering vertices by gain (smallest), leaving by loss (largest) */
        int ni = 0, no = 0;
        for (int w = 0; w < n; w++) {
            int inC = s->C[w >> 6] >> (w & 63) & 1;
            if (!inC) {
                if (tabu_until[w] > it) continue;
                int g = gain_of(s, w) * 4 + (int)(rng_next() & 3);
                if (ni < TOPK) { ins[ni] = w; ing[ni] = g; ni++; }
                else {
                    int worst = 0;
                    for (int k = 1; k < TOPK; k++) if (ing[k] > ing[worst]) worst = k;
                    if (g < ing[worst]) { ins[worst] = w; ing[worst] = g; }
                }
            } else {
                if (tabu_until[w] > it) continue;
                int l = loss_of(s, w) * 4 + (int)(rng_next() & 3);
                if (no < TOPK) { outs[no] = w; outl[no] = l; no++; }
                else {
                    int worst = 0;
                    for (int k = 1; k < TOPK; k++) if (outl[k] < outl[worst]) worst = k;
                    if (l > outl[worst]) { outs[worst] = w; outl[worst] = l; }
                }
            }
        }
        /* aspiration: any tabu vertex whose swap would beat the global best */
        int bu = -1, bw = -1, bd = 1 << 30;
        for (int a = 0; a < no; a++)
            for (int b = 0; b < ni; b++) {
                int d = swap_delta(s, outs[a], ins[b]);
                if (d < bd || (d == bd && (rng_next() & 1))) { bd = d; bu = outs[a]; bw = ins[b]; }
            }
        if (ni == 0 || no == 0) {
            /* everything tabu: pick a random non-tabu-agnostic swap to keep moving */
            int u = -1, w = -1, tries = 0;
            while ((u < 0 || w < 0) && tries++ < 4 * n) {
                int v = (int)(rng_next() % (uint64_t)n);
                if (s->C[v >> 6] >> (v & 63) & 1) u = v; else w = v;
            }
            if (u < 0 || w < 0) break;
            bu = u; bw = w; bd = swap_delta(s, u, w);
        }
        remove_vertex(s, bu);
        add_vertex(s, bw);
        tabu_until[bu] = it + tenure + (int)(rng_next() % 3);
        tabu_until[bw] = it + tenure + (int)(rng_next() % 3);
        if (s->value < run_best) { run_best = s->value; since = 0; } else since++;
        if (s->value < *best_val) { *best_val = s->value; memcpy(best_set, s->C, sizeof(uint64_t) * W); }
        if (since > stall) break;
    }
    free(tabu_until);
}

static void run_from(State *s, const uint64_t *seed, int t, int max_swaps, int stall, int tenure,
                     double deadline, int *best_val, uint64_t *best_set) {
    memcpy(s->C, seed, sizeof(uint64_t) * s->W);
    s->t = t;
    recompute(s);
    adjust(s, t);
    tabu_run(s, max_swaps, stall, tenure, deadline, best_val, best_set);
}

/* The whole profile. fhat_out[0..n], sets_out[(n+1)*W]; returns rounds done.
 * budget_sec is the wall budget; stall_a/stall_c the non-improving swap
 * limits of the sweep and the focus rounds; seeds are nseeds masks of any size.
 * level_seconds_out[t] accumulates the seconds spent on level t. */
int search_profile(int n, int W, const uint64_t *nbr, int nseeds, const uint64_t *seeds,
                   int max_swaps, int stall_a, int stall_c, int tenure, uint64_t rng_seed,
                   double budget_sec, int max_rounds, int *fhat_out, uint64_t *sets_out,
                   double *level_seconds_out, int *rounds_out, int *improved_rounds_out) {
    if (n < 1 || W < 1 || W > MAXW || n > 64 * W) return -1;
    rng_state = rng_seed ? rng_seed * 0x9E3779B97F4A7C15ULL : 88172645463325252ULL;
    double t0 = now_sec(), deadline = t0 + budget_sec;
    State *s = (State *)calloc(1, sizeof(State));
    s->n = n; s->W = W; s->nbr = nbr;
    /* BFS balls of radius 1 and 2 around every vertex */
    uint64_t *balls = (uint64_t *)calloc((size_t)2 * n * W, sizeof(uint64_t));
    for (int v = 0; v < n; v++) {
        uint64_t *b1 = balls + (size_t)v * W, *b2 = balls + (size_t)(n + v) * W;
        memcpy(b1, nbr + (size_t)v * W, sizeof(uint64_t) * W);
        memcpy(b2, b1, sizeof(uint64_t) * W);
        for (int i = 0; i < W; i++) {
            uint64_t bits = b1[i];
            while (bits) {
                int b = __builtin_ctzll(bits); bits &= bits - 1;
                const uint64_t *nu = nbr + (size_t)((i << 6) | b) * W;
                for (int j = 0; j < W; j++) b2[j] |= nu[j];
            }
        }
    }
    for (int t = 0; t <= n; t++) { fhat_out[t] = n + 1; level_seconds_out[t] = 0.0; }
    memset(sets_out, 0, sizeof(uint64_t) * (size_t)(n + 1) * W);
    fhat_out[0] = 0;
    fhat_out[n] = n;
    for (int v = 0; v < n; v++) sets_out[(size_t)n * W + (v >> 6)] |= 1ULL << (v & 63);
    int rounds = 0, improved_rounds = 0;
    uint64_t *best_set = sets_out;
    /* phase A: ascending sweep, every seed family, cheap stall */
    for (int t = 1; t <= n - 1; t++) {
        double lt = now_sec();
        double remaining = deadline - lt;
        double level_deadline = lt + (remaining > 0 ? remaining / (double)(n - t + 1) * 0.6 : 0.0) ;
        if (level_deadline > deadline) level_deadline = deadline;
        if (level_deadline < lt + 0.002) level_deadline = lt + 0.002;
        int *bv = &fhat_out[t];
        uint64_t *bs = best_set + (size_t)t * W;
        /* previous level's best plus one vertex (adjust handles it) */
        run_from(s, best_set + (size_t)(t - 1) * W, t, max_swaps, stall_a, tenure, level_deadline, bv, bs);
        for (int k = 0; k < nseeds && now_sec() < level_deadline; k++)
            run_from(s, seeds + (size_t)k * W, t, max_swaps, stall_a, tenure, level_deadline, bv, bs);
        for (int k = 0; k < 2 * n && now_sec() < level_deadline; k++) {
            /* balls in a pseudo-random order so a deadline does not always cut the same vertices */
            int idx = (int)((rng_next() + (uint64_t)k * 7919ULL) % (uint64_t)(2 * n));
            run_from(s, balls + (size_t)idx * W, t, max_swaps, stall_a, tenure, level_deadline, bv, bs);
        }
        level_seconds_out[t] += now_sec() - lt;
    }
    rounds++;
    /* phase B: descending from t+1 minus one vertex */
    for (int t = n - 1; t >= 1 && now_sec() < deadline; t--) {
        double lt = now_sec();
        run_from(s, best_set + (size_t)(t + 1) * W, t, max_swaps, stall_a, tenure, deadline, &fhat_out[t], best_set + (size_t)t * W);
        level_seconds_out[t] += now_sec() - lt;
    }
    rounds++;
    /* phase C: focus rounds on the argmax levels of fhat(t) - t until a round improves nothing */
    for (int r = 0; r < max_rounds && now_sec() < deadline; r++) {
        int h = -1 << 30;
        for (int t = 1; t <= n; t++) if (fhat_out[t] - t > h) h = fhat_out[t] - t;
        int improved = 0, any = 0;
        for (int t = 1; t <= n - 1 && now_sec() < deadline; t++) {
            if (fhat_out[t] - t != h) continue;
            any = 1;
            double lt = now_sec();
            int before = fhat_out[t];
            int *bv = &fhat_out[t];
            uint64_t *bs = best_set + (size_t)t * W;
            run_from(s, bs, t, max_swaps, stall_c, tenure, deadline, bv, bs);
            run_from(s, best_set + (size_t)(t - 1) * W, t, max_swaps, stall_c, tenure, deadline, bv, bs);
            run_from(s, best_set + (size_t)(t + 1) * W, t, max_swaps, stall_c, tenure, deadline, bv, bs);
            for (int k = 0; k < nseeds && now_sec() < deadline; k++)
                run_from(s, seeds + (size_t)k * W, t, max_swaps, stall_c, tenure, deadline, bv, bs);
            for (int k = 0; k < 2 * n && now_sec() < deadline; k++)
                run_from(s, balls + (size_t)k * W, t, max_swaps, stall_c, tenure, deadline, bv, bs);
            level_seconds_out[t] += now_sec() - lt;
            if (fhat_out[t] < before) improved = 1;
        }
        rounds++;
        if (improved) improved_rounds++;
        if (!any || !improved) break;
    }
    *rounds_out = rounds;
    *improved_rounds_out = improved_rounds;
    free(balls);
    free(s);
    return 0;
}
