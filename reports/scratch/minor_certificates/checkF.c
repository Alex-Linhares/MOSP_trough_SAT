/* checkF: checks a refutation certificate of "vertex separation <= w"
   (outer-boundary form), independently of the search that produced it.
   Input: EDGES.txt ("n m" then m lines "u v", 0-based), w, and a file of
   vertex sets, ceil(n/8) bytes each (bit v of byte v/8 = vertex v).
   Checks: (1) the empty set is in F; (2) the full vertex set is not in F;
   (3) for every S in F and every v not in S with |N(S+v) - (S+v)| <= w,
   S+v is in F. Then no layout has every prefix boundary <= w: its prefixes
   start in F (1), stay in F (3), and would end at the full set, contradicting (2).
   Prints VERIFIED or the first failure.  usage: checkF EDGES.txt W FILE */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n, B;
static unsigned char *F; static size_t cnt;
static int cmp(const void *a, const void *b) { return memcmp(a, b, B); }
static int in(const unsigned char *s) { return bsearch(s, F, cnt, B, cmp) != NULL; }
static int bit(const unsigned char *s, int v) { return s[v >> 3] >> (v & 7) & 1; }
int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "usage: checkF EDGES W FILE\n"); return 2; }
    FILE *f = fopen(argv[1], "r"); int m; if (fscanf(f, "%d %d", &n, &m) != 2) return 2;
    B = (n + 7) / 8;
    unsigned char (*adj)[256] = calloc(n, 256);
    for (int i = 0; i < m; i++) { int u, v; if (fscanf(f, "%d %d", &u, &v) != 2) return 2; if (u != v) adj[u][v] = adj[v][u] = 1; }
    int w = atoi(argv[2]);
    FILE *g = fopen(argv[3], "rb"); fseek(g, 0, SEEK_END); long sz = ftell(g); fseek(g, 0, SEEK_SET);
    if (sz % B) { printf("bad file size\n"); return 1; }
    cnt = sz / B; F = malloc(sz); if (fread(F, 1, sz, g) != (size_t)sz) return 2;
    qsort(F, cnt, B, cmp);
    for (size_t i = 0; i + 1 < cnt; i++) if (!memcmp(F + i * B, F + (i + 1) * B, B)) { printf("duplicate set\n"); return 1; }
    unsigned char *T = calloc(B, 1), *full = calloc(B, 1);
    for (int v = 0; v < n; v++) full[v >> 3] |= 1 << (v & 7);
    if (!in(T)) { printf("FAIL: empty set not in F\n"); return 1; }
    if (in(full)) { printf("FAIL: full set in F\n"); return 1; }
    uint64_t (*nb)[4] = calloc(n, sizeof *nb);        /* adjacency as 4 x 64-bit words */
    for (int u = 0; u < n; u++) for (int x = 0; x < n; x++) if (adj[u][x]) nb[u][x >> 6] |= 1ULL << (x & 63);
    unsigned long long checked = 0;
    for (size_t i = 0; i < cnt; i++) {
        const unsigned char *S = F + i * B;
        uint64_t s[4] = {0}, NS[4] = {0};
        for (int v = 0; v < n; v++) if (bit(S, v)) { s[v >> 6] |= 1ULL << (v & 63); for (int j = 0; j < 4; j++) NS[j] |= nb[v][j]; }
        for (int v = 0; v < n; v++) if (!bit(S, v)) {
            int b = 0;     /* |N(S+v) - (S+v)| */
            for (int j = 0; j < 4; j++) {
                uint64_t t = s[j] | (j == (v >> 6) ? 1ULL << (v & 63) : 0);
                b += __builtin_popcountll((NS[j] | nb[v][j]) & ~t);
            }
            if (b <= w) {
                memcpy(T, S, B); T[v >> 3] |= 1 << (v & 7); checked++;
                if (!in(T)) { printf("FAIL: set %zu extended by %d (boundary %d) not in F\n", i, v, b); return 1; }
            }
        }
    }
    printf("VERIFIED: n=%d w=%d |F|=%zu, %llu admissible extensions checked\n", n, w, cnt, checked);
    return 0;
}
