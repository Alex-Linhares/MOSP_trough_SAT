/* The search engine, compiled once per word count.
 *
 * closing_search_w.c is a verbatim copy of ../pathwidth/closing_search_w.c,
 * the C engine the Python solver loads through ctypes (pathwidth/native.py);
 * `make check-engine` diffs the two. It is included here, not edited: the
 * Makefile builds this file with -DWORDS=W and renames the two exported
 * functions to csw_decide_W / csw_words_W, once for each W in {2, 4, 8, 16}.
 * Its one -Wextra complaint (an unused parameter of subset_pass) is silenced
 * here rather than by changing the engine.
 */
#if defined(__GNUC__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#endif
#include "closing_search_w.c"
