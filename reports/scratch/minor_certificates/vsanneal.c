/* vsanneal: simulated annealing for a layout of small vertex separation
   (outer-boundary form: prefix P has cost |N(P) - P|; the maximum over prefixes
   is the vertex separation of the reversed layout, so it is pathwidth-valid).
   Objective, lexicographic: (max cost, number of prefixes at the max, number at max-1).
   Move: take one vertex and reinsert it within distance D. Upper bounds only.
   usage: vsanneal EDGES.txt SEED SECONDS [START_ORDER_FILE]  -> prints best order */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
static int n, m, *eu, *ev, *adjs, *adjo, *p, *pos, *cnt;
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static unsigned long long rs; static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }
static long long cost(int *mx) {
    memset(cnt, 0, (n + 1) * sizeof(int));
    for (int u = 0; u < n; u++) {               /* u is open on prefixes [first nbr pos, pos[u]) */
        int f = pos[u];
        for (int k = adjo[u]; k < adjo[u + 1]; k++) if (pos[adjs[k]] < f) f = pos[adjs[k]];
        if (f < pos[u]) { cnt[f]++; cnt[pos[u]]--; }
    }
    int run = 0, best = 0, a = 0, b = 0;
    int *bd = malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) { run += cnt[i]; bd[i] = run; if (run > best) best = run; }
    for (int i = 0; i < n; i++) { if (bd[i] == best) a++; else if (bd[i] == best - 1) b++; }
    free(bd); *mx = best;
    return (long long)best * n * n + (long long)a * n + b;
}
static void move(int from, int to) {           /* reinsert p[from] at index to */
    int v = p[from];
    if (from < to) for (int i = from; i < to; i++) { p[i] = p[i + 1]; pos[p[i]] = i; }
    else for (int i = from; i > to; i--) { p[i] = p[i - 1]; pos[p[i]] = i; }
    p[to] = v; pos[v] = to;
}
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); if (fscanf(f, "%d %d", &n, &m) != 2) return 2;
    eu = malloc(m * sizeof(int)); ev = malloc(m * sizeof(int)); adjo = calloc(n + 1, sizeof(int)); adjs = malloc(2 * m * sizeof(int));
    for (int i = 0; i < m; i++) { if (fscanf(f, "%d %d", &eu[i], &ev[i]) != 2) return 2; adjo[eu[i] + 1]++; adjo[ev[i] + 1]++; }
    for (int i = 0; i < n; i++) adjo[i + 1] += adjo[i];
    int *fill = calloc(n, sizeof(int));
    for (int i = 0; i < m; i++) { adjs[adjo[eu[i]] + fill[eu[i]]++] = ev[i]; adjs[adjo[ev[i]] + fill[ev[i]]++] = eu[i]; }
    rs = 88172645463325252ULL ^ (unsigned long long)atoll(argv[2]) * 2654435761ULL; for (int i = 0; i < 10; i++) rnd();
    double secs = atof(argv[3]);
    p = malloc(n * sizeof(int)); pos = malloc(n * sizeof(int)); cnt = malloc((n + 1) * sizeof(int));
    if (argc > 4) { FILE *g = fopen(argv[4], "r"); for (int i = 0; i < n; i++) if (fscanf(g, "%d", &p[i]) != 1) return 2; }
    else { for (int i = 0; i < n; i++) p[i] = i; for (int i = n - 1; i > 0; i--) { int j = rnd() % (i + 1), t = p[i]; p[i] = p[j]; p[j] = t; } }
    for (int i = 0; i < n; i++) pos[p[i]] = i;
    int mx; long long c = cost(&mx), bc = c; int bmx = mx;
    int *bp = malloc(n * sizeof(int)); memcpy(bp, p, n * sizeof(int));
    double t0 = now(), T0 = 2.0 * n, T = T0; long long it = 0;
    while (1) {
        if ((it & 1023) == 0) { double e = (now() - t0) / secs; if (e >= 1) break; T = T0 * pow(0.002, e); }
        it++;
        int from = rnd() % n, D = 1 + rnd() % 12, to = from + (int)(rnd() % (2 * D + 1)) - D;
        if (to < 0 || to >= n || to == from) continue;
        move(from, to);
        int nm; long long nc = cost(&nm);
        if (nc <= c || rnd() / 4294967296.0 < exp((double)(c - nc) / T)) {
            c = nc; mx = nm;
            if (c < bc) { bc = c; bmx = mx; memcpy(bp, p, n * sizeof(int)); }
        } else move(to, from);
    }
    memcpy(p, bp, n * sizeof(int)); for (int i = 0; i < n; i++) pos[p[i]] = i; cost(&mx);
    printf("best vs=%d (cost %lld) after %lld moves\norder:", mx, bc, it);
    for (int i = 0; i < n; i++) printf(" %d", p[i]); printf("\n");
    return 0;
}
