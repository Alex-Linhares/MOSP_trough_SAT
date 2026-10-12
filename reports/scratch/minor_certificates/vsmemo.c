/* vsmemo: rule-free exact decision "vertex separation (= pathwidth) <= w?".
   Written from scratch 2026-10-12; shares no code with the project's searches.

   Search over layout prefixes S (vertex sets). A prefix is admissible iff its
   inner boundary {v in S : v has a neighbour outside S} has at most w vertices.
   pw <= w iff the full set is reachable from the empty set through admissible
   sets adding one vertex at a time. Depth-first search; every set found not to
   reach the full set is stored in a hash table (the only pruning: whether the
   full set is reachable from S depends on S alone). No dominance rule, no bound.

   Optional -f (off by default): add at once a vertex v outside S with N(v)
   contained in S. Sound: moving such a v to directly after S in any layout
   does not enlarge any later prefix boundary (v contributes nothing to it and
   leaving it outside could only add its neighbours to the boundary).

   Optional -o: use the outer boundary |N(S) - S| of each prefix instead. The
   maximum over a layout's prefixes of the outer boundary equals the maximum of
   the inner boundary over the reversed layout's prefixes (the outer boundary of
   P is the inner boundary of V - P), so both decide the same question; they
   differ only in which sets the search visits. -f also holds under -o (v leaves the outer boundary, N(v) adds nothing).

   -w FILE (with UNSAT, without -f): write every stored prefix. They form a
   family F with the empty set in F, the full set not in F, and every admissible
   one-vertex extension of a member again a member, which is what checkF verifies.

   usage: vsmemo EDGES.txt W [-f] [-o] [-t SECONDS] [-m MAXSTATES] [-w FILE]
   EDGES.txt: first line "n m", then m lines "u v" (0-based).
   prints "SAT order ..." / "UNSAT" / "UNKNOWN" and the number of states. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define W 3
typedef struct { uint64_t w[W]; } set_t;
static int n, wmax, forced = 0;
static set_t nb[192], full;
static uint64_t states = 0, maxstates = 2000000000ULL;
static double deadline = 1e18;
static int order[192], timeout = 0;
static const char *dump = 0;

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static inline int has(const set_t *s, int v) { return (s->w[v >> 6] >> (v & 63)) & 1; }
static inline void add(set_t *s, int v) { s->w[v >> 6] |= 1ULL << (v & 63); }
static inline int sub(const set_t *a, const set_t *b) { for (int i = 0; i < W; i++) if (a->w[i] & ~b->w[i]) return 0; return 1; }
static inline int eq(const set_t *a, const set_t *b) { return !memcmp(a, b, sizeof(set_t)); }
static int outer = 0;
static int boundary(const set_t *s) {
    int c = 0;
    if (outer) {   /* |N(S) minus S|: vertices outside S with a neighbour in S */
        for (int v = 0; v < n; v++) if (!has(s, v)) { for (int i = 0; i < W; i++) if (nb[v].w[i] & s->w[i]) { c++; break; } }
        return c;
    }
    for (int v = 0; v < n; v++) if (has(s, v) && !sub(&nb[v], s)) c++;
    return c;
}
/* open-addressing hash set of failed prefixes */
static set_t *tab; static uint8_t *used; static uint64_t cap, cnt;
static uint64_t hsh(const set_t *s) { uint64_t h = 0x9e3779b97f4a7c15ULL; for (int i = 0; i < W; i++) { h ^= s->w[i]; h *= 0xff51afd7ed558ccdULL; h ^= h >> 33; } return h; }
static void grow(void);
static int lookup(const set_t *s) { uint64_t i = hsh(s) & (cap - 1); while (used[i]) { if (eq(&tab[i], s)) return 1; i = (i + 1) & (cap - 1); } return 0; }
static void insert(const set_t *s) {
    if (2 * (cnt + 1) > cap) grow();
    uint64_t i = hsh(s) & (cap - 1); while (used[i]) i = (i + 1) & (cap - 1);
    used[i] = 1; tab[i] = *s; cnt++;
}
static void grow(void) {
    set_t *ot = tab; uint8_t *ou = used; uint64_t oc = cap;
    cap = oc ? 2 * oc : (1ULL << 20);
    tab = malloc(cap * sizeof(set_t)); used = calloc(cap, 1);
    if (!tab || !used) { fprintf(stderr, "out of memory at %llu states\n", (unsigned long long)cnt); exit(3); }
    cnt = 0;
    for (uint64_t i = 0; i < oc; i++) if (ou[i]) insert(&ot[i]);
    free(ot); free(ou);
}

static int dfs(set_t S, set_t NS, int depth) {  /* NS = union of N(v), v in S (used by -o) */
    if (eq(&S, &full)) return 1;
    int d0 = depth;
    if (forced) {   /* add every vertex whose neighbourhood is already inside S */
        int again = 1;
        while (again) {
            again = 0;
            for (int v = 0; v < n; v++)
                if (!has(&S, v) && sub(&nb[v], &S)) { add(&S, v); for (int j = 0; j < W; j++) NS.w[j] |= nb[v].w[j]; order[depth++] = v; again = 1; }
        }
        if (eq(&S, &full)) return 1;
    }
    if (lookup(&S)) return 0;
    if (++states % 65536 == 0 && now() > deadline) timeout = 1;
    if (timeout || states > maxstates) { timeout = 1; return 0; }
    int cand[192], bd[192], nc = 0;
    for (int v = 0; v < n; v++) if (!has(&S, v)) {
        set_t T = S; add(&T, v); int b;
        if (outer) { b = 0; for (int i = 0; i < W; i++) b += __builtin_popcountll((NS.w[i] | nb[v].w[i]) & ~T.w[i]); }
        else b = boundary(&T);
        if (b <= wmax) { cand[nc] = v; bd[nc] = b; nc++; }
    }
    for (int i = 1; i < nc; i++) { int c = cand[i], b = bd[i], j = i; while (j > 0 && bd[j-1] > b) { cand[j] = cand[j-1]; bd[j] = bd[j-1]; j--; } cand[j] = c; bd[j] = b; }
    for (int i = 0; i < nc; i++) {
        set_t T = S, NT = NS; add(&T, cand[i]); order[depth] = cand[i];
        for (int j = 0; j < W; j++) NT.w[j] |= nb[cand[i]].w[j];
        if (dfs(T, NT, depth + 1)) return 1;
        if (timeout) return 0;
    }
    (void)d0;
    insert(&S);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: vsmemo EDGES W [-f] [-t SEC] [-m MAXSTATES]\n"); return 2; }
    FILE *f = fopen(argv[1], "r"); int m;
    if (!f || fscanf(f, "%d %d", &n, &m) != 2 || n > 64 * W) { fprintf(stderr, "bad input\n"); return 2; }
    for (int i = 0; i < m; i++) { int u, v; if (fscanf(f, "%d %d", &u, &v) != 2) return 2; if (u != v) { add(&nb[u], v); add(&nb[v], u); } }
    wmax = atoi(argv[2]);
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i], "-f")) forced = 1;
        else if (!strcmp(argv[i], "-o")) outer = 1;
        else if (!strcmp(argv[i], "-t")) deadline = now() + atof(argv[++i]);
        else if (!strcmp(argv[i], "-m")) maxstates = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "-w")) dump = argv[++i];
    }
    grow();
    for (int v = 0; v < n; v++) add(&full, v);
    double t0 = now(); set_t E; memset(&E, 0, sizeof E);
    int r = dfs(E, E, 0);
    printf("%s n=%d w=%d outer=%d forced=%d states=%llu stored=%llu secs=%.1f\n", r ? "SAT" : timeout ? "UNKNOWN" : "UNSAT",
           n, wmax, outer, forced, (unsigned long long)states, (unsigned long long)cnt, now() - t0);
    if (!r && !timeout && dump) {   /* the refutation certificate: every stored prefix, ceil(n/8) bytes each, little-endian */
        FILE *o = fopen(dump, "wb"); int nb8 = (n + 7) / 8;
        for (uint64_t i = 0; i < cap; i++) if (used[i]) fwrite(tab[i].w, 1, nb8, o);
        fclose(o);
    }
    if (r) {   /* re-verify the layout found */
        set_t S; memset(&S, 0, sizeof S); int worst = 0, seen[192] = {0};
        for (int i = 0; i < n; i++) { int v = order[i]; if (seen[v]) { printf("BAD ORDER\n"); return 4; } seen[v] = 1; add(&S, v); int b = boundary(&S); if (b > worst) worst = b; }
        printf("order vs=%d:", worst); for (int i = 0; i < n; i++) printf(" %d", order[i]); printf("\n");
        if (worst > wmax) { printf("BAD ORDER\n"); return 4; }
    }
    return r ? 10 : timeout ? 0 : 20;
}
