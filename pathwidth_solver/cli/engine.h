/* Entry points of engine.c, one per word count (see the Makefile). The
 * arguments are those of csw_decide in closing_search_w.c. */
#ifndef PATHWIDTH_ENGINE_H
#define PATHWIDTH_ENGINE_H
#include <stdint.h>

#define ENGINE_ARGS int n, int k, const uint64_t *neighbours, long long max_nodes, double seconds, \
    int subset_rule, int definite_move, int use_memo, int restrict_frontier, long long memo_limit, \
    int better_move, int better_move_dominators, int old_move, int fan_order, \
    int better_move_variant, int repaired_rules, int *out_path, long long *out_nodes, int *out_len

int csw_decide_2(ENGINE_ARGS);
int csw_decide_4(ENGINE_ARGS);
int csw_decide_8(ENGINE_ARGS);
int csw_decide_16(ENGINE_ARGS);
int csw_words_2(void);
int csw_words_4(void);
int csw_words_8(void);
int csw_words_16(void);

#endif
