# A whole-instance false refutation by the published rules (2026-10-09)

**The instance.** A 34-customer MOSP instance, given as its MOSP graph (34
vertices, 61 edges; one pattern per edge), is in
`paper1/data/false_refutation/instance34.json` (`minimised`). It was found by
gluing two copies of a 17-customer near-miss of the false-refutation hunt
(`paper1/false_refutation_hunt.py`; the near-miss came from the `cex14`
family), joined by one edge, then minimised. The script that found it is
`paper1/near_miss_study.py`. Its session ended on an API error before
writing a report.

**The facts**, re-checked independently of the hunt's code
(`tests/test_false_refutation_instance.py`):
- **A solution with 6 open stacks exists.** A product order derived from the
  witness closing order (cut each pattern when its first customer closes)
  peaks at 6 open stacks, by plain simulation and by `mosp.verify`.
- **The production customer search under the published rules answers unsat at
  k = 6**, through the public `decide`, in both the C code (526 nodes) and the
  Python reference (839 nodes). It would report the optimum as 7.
- **The repaired rules answer sat at 6 and unsat at 5**, so the optimum is 6.

**Which published configurations fail:**

| configuration (published rules) | answer at k = 6 |
|---|---|
| definite move + subset rule + old move, memo on or off, better move off | **unsat: wrong** |
| definite move + subset rule, old move off | sat |
| any configuration with the better move on | sat |

**The mechanism.** The failure needs the old move. The definite move's false
refutation of one subtree is inherited by later siblings through the old move,
which prunes their way to the remaining solutions. This is the propagation the
hunt was designed to exploit. With the better move on, this instance happens
to be answered correctly. Chu (2011, §6.3.2) notes that their implementation
of the better move subsumes the definite move. Whether a configuration with
the better move can also be made to fail is open, and is the next hunt target.

The hunt was stopped after this find (3.1M candidates, best fitness 30.43,
no repaired-search error, no oracle disagreement).
