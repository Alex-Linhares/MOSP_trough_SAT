/* Exhaustive census of pathwidth − treewidth over all graphs on n vertices.
 *
 * Reads graphs in graph6 format (one per line, as nauty's geng writes them)
 * from stdin and, for each, computes
 *
 *   pw(G)  by the vertex-separation subset DP
 *            VS(S) = max( cut(S), min_{v in S} VS(S \ {v}) ),  VS({}) = 0,
 *          where cut(S) is the number of vertices of S with a neighbour
 *          outside S; pw = VS(V) by Kinnersley (1992);
 *
 *   tw(G)  by the subset recurrence of Bodlaender, Fomin, Koster, Kratsch &
 *          Thilikos (2012), the same recurrence as learning/treewidth.c:
 *            TW(S) = min_{v in S} max( TW(S \ {v}), |Q(S \ {v}, v)| ).
 *
 * Every graph with pw − tw ≥ k (k = --min-diff, default 2) is written out as
 * "FOUND <graph6> <n> <pw> <tw> <edges>". At the end a histogram
 * "HIST <n> <pw> <tw> <count>" and a "TOTAL ..." line summarise the stream.
 *
 * Levels (--level):
 *   2  exact pw and tw for every graph (the joint histogram is complete);
 *   1  exact pw for every graph; tw only when pw − MMD(G) ≥ k, where the
 *      contraction-degeneracy bound MMD ≤ tw makes the skip sound
 *      (pw − tw ≤ pw − MMD < k); skipped graphs are tallied with tw = −1;
 *   0  as 1, but first a greedy layout gives ub ≥ pw and the graph is skipped
 *      with pw = tw = −1 when ub − MMD < k (sound for the same reason).
 *
 * Neither number is a bound on MOSP and nothing here touches the solver.
 *
 * Build:  gcc -O3 -march=native -o learning/_pwtw_exhaust learning/pwtw_exhaust.c
 * Run:    nauty-geng -q 9 | learning/_pwtw_exhaust --min-diff 2 --level 2
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint64_t mask_t;
#define MAXN 16

static inline int popcnt(mask_t x) { return __builtin_popcountll(x); }
static inline int ctz(mask_t x) { return __builtin_ctzll(x); }

/* ---------------------------------------------------------------------- */
/* graph6                                                                  */
/* ---------------------------------------------------------------------- */

/* Parses one graph6 line (no header) into neighbour masks; returns n or -1. */
static int parse_graph6(const char *line, mask_t *adj) {
    if (line[0] == '>') return -1;                  /* header line, skip */
    int n = (unsigned char)line[0] - 63;
    if (n < 0 || n > MAXN) return -1;
    for (int i = 0; i < n; ++i) adj[i] = 0;
    const unsigned char *p = (const unsigned char *)line + 1;
    int bit = 0;                                      /* bit index within the stream */
    int cur = 0;                                      /* current 6-bit word */
    for (int j = 1; j < n; ++j) {
        for (int i = 0; i < j; ++i) {
            if (bit % 6 == 0) {
                if (*p < 63) return -1;
                cur = *p++ - 63;
            }
            int b = (cur >> (5 - bit % 6)) & 1;
            ++bit;
            if (b) {
                adj[i] |= (mask_t)1 << j;
                adj[j] |= (mask_t)1 << i;
            }
        }
    }
    return n;
}

/* ---------------------------------------------------------------------- */
/* pathwidth: vertex separation DP                                         */
/* ---------------------------------------------------------------------- */

static int pw_dp(int n, const mask_t *adj, uint8_t *f) {
    if (n <= 1) return 0;
    mask_t count = (mask_t)1 << n;
    f[0] = 0;
    for (mask_t S = 1; S < count; ++S) {
        mask_t out = ~S;
        int cut = 0;
        int best = n;
        mask_t rest = S;
        while (rest) {
            int u = ctz(rest);
            rest &= rest - 1;
            if (adj[u] & out) ++cut;
            int prior = f[S & ~((mask_t)1 << u)];
            if (prior < best) best = prior;
        }
        f[S] = (uint8_t)(cut > best ? cut : best);
    }
    return f[count - 1];
}

/* Greedy layout: always append the vertex that leaves the smallest cut.
 * Its vertex separation is an upper bound on pw. */
static int pw_greedy_ub(int n, const mask_t *adj) {
    if (n <= 1) return 0;
    mask_t S = 0;
    mask_t all = ((mask_t)1 << n) - 1;
    int width = 0;
    for (int step = 0; step < n; ++step) {
        int best_v = -1, best_cut = n + 1;
        mask_t rest = all & ~S;
        while (rest) {
            int v = ctz(rest);
            rest &= rest - 1;
            mask_t T = S | ((mask_t)1 << v);
            mask_t out = ~T;
            int cut = 0;
            mask_t r2 = T;
            while (r2) {
                int u = ctz(r2);
                r2 &= r2 - 1;
                if (adj[u] & out) ++cut;
            }
            if (cut < best_cut) { best_cut = cut; best_v = v; }
        }
        S |= (mask_t)1 << best_v;
        if (best_cut > width) width = best_cut;
    }
    return width;
}

/* ---------------------------------------------------------------------- */
/* treewidth: MMD lower bound and the subset DP                            */
/* ---------------------------------------------------------------------- */

/* Contraction degeneracy (MMD+): repeatedly take a minimum-degree vertex,
 * record its degree, contract it into the neighbour sharing the fewest
 * neighbours. Every graph produced is a minor, so max recorded degree ≤ tw. */
static int mmd_lower_bound(int n, const mask_t *adj0) {
    mask_t adj[MAXN];
    memcpy(adj, adj0, sizeof(mask_t) * n);
    mask_t alive = ((mask_t)1 << n) - 1;
    int best = 0;
    while (alive) {
        int v = -1, dv = n + 1;
        mask_t rest = alive;
        while (rest) {
            int u = ctz(rest);
            rest &= rest - 1;
            int d = popcnt(adj[u] & alive);
            if (d < dv) { dv = d; v = u; }
        }
        if (dv > best) best = dv;
        mask_t nb = adj[v] & alive;
        if (nb) {
            int w = -1, cw = n + 1;
            mask_t r2 = nb;
            while (r2) {
                int u = ctz(r2);
                r2 &= r2 - 1;
                int c = popcnt(adj[u] & nb);
                if (c < cw) { cw = c; w = u; }
            }
            adj[w] |= adj[v];
            adj[w] &= ~((mask_t)1 << w);
            mask_t r3 = adj[v];
            while (r3) {
                int u = ctz(r3);
                r3 &= r3 - 1;
                adj[u] |= (mask_t)1 << w;
                adj[u] &= ~((mask_t)1 << u);
            }
        }
        alive &= ~((mask_t)1 << v);
        mask_t r4 = alive;
        while (r4) {
            int u = ctz(r4);
            r4 &= r4 - 1;
            adj[u] &= ~((mask_t)1 << v);
        }
    }
    return best;
}

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

static int tw_dp(int n, const mask_t *adj, uint8_t *tw) {
    if (n <= 0) return 0;
    mask_t count = (mask_t)1 << n;
    tw[0] = 0;
    for (mask_t S = 1; S < count; ++S) {
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
    return tw[count - 1];
}

/* ---------------------------------------------------------------------- */
/* main                                                                    */
/* ---------------------------------------------------------------------- */

int main(int argc, char **argv) {
    int min_diff = 2, level = 2;
    for (int a = 1; a < argc; ++a) {
        if (!strcmp(argv[a], "--min-diff") && a + 1 < argc) min_diff = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--level") && a + 1 < argc) level = atoi(argv[++a]);
        else { fprintf(stderr, "usage: %s [--min-diff k] [--level 0|1|2] < graphs.g6\n", argv[0]); return 2; }
    }
    uint8_t *f = (uint8_t *)malloc((size_t)1 << MAXN);
    uint8_t *t = (uint8_t *)malloc((size_t)1 << MAXN);
    if (!f || !t) return 1;
    /* hist[n][pw+1][tw+1]: index 0 means "not computed" (−1) */
    static uint64_t hist[MAXN + 1][MAXN + 2][MAXN + 2];
    static uint64_t seen[MAXN + 1], dp_runs[MAXN + 1], found[MAXN + 1], pw_runs[MAXN + 1];
    memset(hist, 0, sizeof hist);
    char line[256];
    mask_t adj[MAXN];
    while (fgets(line, sizeof line, stdin)) {
        size_t len = strlen(line);
        while (len && (line[len - 1] == '\n' || line[len - 1] == '\r')) line[--len] = 0;
        if (!len) continue;
        int n = parse_graph6(line, adj);
        if (n < 0) continue;
        seen[n]++;
        int pw = -1, tw = -1;
        int mmd = 0;
        if (level <= 1) mmd = mmd_lower_bound(n, adj);
        if (level == 0) {
            int ub = pw_greedy_ub(n, adj);
            if (ub - mmd < min_diff) { hist[n][0][0]++; continue; }
        }
        pw = pw_dp(n, adj, f);
        pw_runs[n]++;
        if (level == 2 || pw - mmd >= min_diff) {
            tw = tw_dp(n, adj, t);
            dp_runs[n]++;
        }
        hist[n][pw + 1][tw + 1]++;
        if (tw >= 0 && pw - tw >= min_diff) {
            int edges = 0;
            for (int i = 0; i < n; ++i) edges += popcnt(adj[i]);
            found[n]++;
            printf("FOUND %s %d %d %d %d\n", line, n, pw, tw, edges / 2);
        }
    }
    for (int n = 0; n <= MAXN; ++n) {
        if (!seen[n]) continue;
        for (int p = 0; p < MAXN + 2; ++p)
            for (int q = 0; q < MAXN + 2; ++q)
                if (hist[n][p][q])
                    printf("HIST %d %d %d %llu\n", n, p - 1, q - 1, (unsigned long long)hist[n][p][q]);
        printf("TOTAL %d %llu %llu %llu %llu %d %d\n", n, (unsigned long long)seen[n],
               (unsigned long long)pw_runs[n], (unsigned long long)dp_runs[n],
               (unsigned long long)found[n], min_diff, level);
    }
    fflush(stdout);
    free(f);
    free(t);
    return 0;
}
