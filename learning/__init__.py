"""Machine learning over the certified corpus: instance structure -> optimum.

The corpus holds 6,376 instances whose optimum is *proved*, which makes it a
supervised dataset with no label noise -- an unusual position for a learned
model of an NP-hard problem, where training targets are normally whatever a
solver managed within its budget.

What is learned here never becomes a bound. A predicted value is not a proof
and a model that predicted one point too high would make the search start above
the optimum and return a wrong answer that still passes witness verification --
the failure mode `satisfiability.mosp_solver._lower_bound` is careful about.
Predictions are used for analysis, for ordering work, and for choosing between
solvers; orderings a model proposes are checked by simulation like any other.
"""
