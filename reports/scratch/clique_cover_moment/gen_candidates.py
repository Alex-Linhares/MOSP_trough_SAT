"""Candidate generators for the Chu & Stuckey Random-n-m-d classes.
Matrix convention here: M is (m patterns) x (n customers), bool.  d = nominal mean customers per pattern.
Every candidate returns an accepted matrix or None if the attempt cap is hit; `attempts` is recorded
through the returned tuple (M, tries)."""
import numpy as np

def mosp_connected(M):
    m, n = M.shape
    seen_c = np.zeros(n, bool); seen_c[0] = True
    while True:
        seen_p = M[:, seen_c].any(axis=1)
        new_c = M[seen_p].any(axis=0) | seen_c
        if new_c.sum() == seen_c.sum():
            return bool(seen_c.all())
        seen_c = new_c

def bern(n, m, p, rng):
    return rng.random((m, n)) < p

def fixed(n, m, d, rng):
    idx = rng.random((m, n)).argsort(axis=1)[:, :d]
    M = np.zeros((m, n), bool)
    M[np.arange(m)[:, None], idx] = True
    return M

def pad_customers(M, kmin, rng):
    """every customer (column) with fewer than kmin patterns joins random patterns it is not in."""
    m, n = M.shape
    for j in np.flatnonzero(M.sum(axis=0) < kmin):
        need = kmin - M[:, j].sum()
        cand = np.flatnonzero(~M[:, j])
        M[rng.choice(cand, need, replace=False), j] = True
    return M

def pad_patterns(M, kmin, rng):
    """every pattern (row) with fewer than kmin customers gains random customers it does not have."""
    m, n = M.shape
    for i in np.flatnonzero(M.sum(axis=1) < kmin):
        need = kmin - M[i].sum()
        cand = np.flatnonzero(~M[i])
        M[i, rng.choice(cand, need, replace=False)] = True
    return M

def resample_patterns(M, kmin, p, rng):
    """rows with fewer than kmin ones are redrawn (truncated binomial rows)."""
    m, n = M.shape
    while True:
        bad = np.flatnonzero(M.sum(axis=1) < kmin)
        if len(bad) == 0: return M
        M[bad] = rng.random((len(bad), n)) < p

def with_rejection(draw, cap):
    def g(n, m, d, rng):
        for t in range(1, cap + 1):
            M = draw(n, m, d, rng)
            if mosp_connected(M): return M, t
        return None, cap
    return g

def no_rejection(draw):
    def g(n, m, d, rng):
        return draw(n, m, d, rng), 1
    return g

CAP = 2000
CANDIDATES = {
    # (i) exactly d per pattern, customers padded to >= 2
    "i_fixed_padC2":        no_rejection(lambda n, m, d, r: pad_customers(fixed(n, m, d, r), 2, r)),
    # (ii) Bernoulli(d/n), customers padded to >= 2
    "ii_bern_padC2":        no_rejection(lambda n, m, d, r: pad_customers(bern(n, m, d / n, r), 2, r)),
    # (iii) = (i) + discard decomposable
    "iii_fixed_padC2_conn": with_rejection(lambda n, m, d, r: pad_customers(fixed(n, m, d, r), 2, r), CAP),
    # the paper as written: Bernoulli(d/n), discard decomposable, nothing else
    "paper_bern_conn":      with_rejection(lambda n, m, d, r: bern(n, m, d / n, r), CAP),
    # Bernoulli, patterns padded to >= 2, discard decomposable
    "bern_padP2_conn":      with_rejection(lambda n, m, d, r: pad_patterns(bern(n, m, d / n, r), 2, r), CAP),
    # Bernoulli, patterns redrawn until >= 2 (truncated rows), discard decomposable
    "bern_truncP2_conn":    with_rejection(lambda n, m, d, r: resample_patterns(bern(n, m, d / n, r), 2, d / n, r), CAP),
    # Bernoulli, customers padded to >= 1 then patterns padded to >= 2, discard decomposable
    "bern_padC1_padP2_conn": with_rejection(lambda n, m, d, r: pad_patterns(pad_customers(bern(n, m, d / n, r), 1, r), 2, r), CAP),
    # same, patterns first then customers
    "bern_padP2_padC1_conn": with_rejection(lambda n, m, d, r: pad_customers(pad_patterns(bern(n, m, d / n, r), 2, r), 1, r), CAP),
    # Bernoulli, customers padded to >= 1 only, discard decomposable (control: should fail the row minimum)
    "bern_padC1_conn":      with_rejection(lambda n, m, d, r: pad_customers(bern(n, m, d / n, r), 1, r), CAP),
    # Bernoulli, customers padded to >= 1, patterns to >= 2, no rejection (how much does the discard do?)
    "bern_padC1_padP2":     no_rejection(lambda n, m, d, r: pad_patterns(pad_customers(bern(n, m, d / n, r), 1, r), 2, r)),
    # fixed d, patterns already >= 2, customers padded to >= 1, discard decomposable
    "fixed_padC1_conn":     with_rejection(lambda n, m, d, r: pad_customers(fixed(n, m, d, r), 1, r), CAP),
}

def stats(M):
    """per-instance statistics used for the fit."""
    rs = M.sum(axis=1); cs = M.sum(axis=0)
    return dict(ones=int(rs.sum()), row_mean=rs.mean(), row_var=rs.var(), row_min=int(rs.min()), row_max=int(rs.max()),
                col_mean=cs.mean(), col_var=cs.var(), col_min=int(cs.min()), col_max=int(cs.max()),
                frac_row2=(rs == 2).mean(), frac_row3=(rs == 3).mean(), frac_col1=(cs == 1).mean(), frac_col2=(cs == 2).mean(),
                rowcol_corr=_rowcol_corr(M, rs, cs))

def _rowcol_corr(M, rs, cs):
    # correlation over incidences between the pattern's size and the customer's count
    i, j = np.nonzero(M)
    a = rs[i].astype(float); b = cs[j].astype(float)
    if a.std() == 0 or b.std() == 0: return 0.0
    return float(np.corrcoef(a, b)[0, 1])

# --- intermediate variants (added after the first fit: padding undershoots the ones count, truncation overshoots) ---
def resample_empty_rows(M, p, rng):
    """rows with no ones are redrawn until non-empty; rows with one 1 are left for padding."""
    m, n = M.shape
    while True:
        bad = np.flatnonzero(M.sum(axis=1) == 0)
        if len(bad) == 0: return M
        M[bad] = rng.random((len(bad), n)) < p
CANDIDATES.update({
    # empty patterns redrawn, size-1 patterns padded to 2, empty customers padded to 1, discard decomposable
    "bern_redraw0_padP2_padC1_conn": with_rejection(lambda n, m, d, r: pad_customers(pad_patterns(resample_empty_rows(bern(n, m, d / n, r), d / n, r), 2, r), 1, r), CAP),
    # the best-fit family with the density lifted 5% (diagnostic: is the residual a density offset?)
    "bern105_padC1_padP2_conn": with_rejection(lambda n, m, d, r: pad_patterns(pad_customers(bern(n, m, 1.05 * d / n, r), 1, r), 2, r), CAP),
    "bern110_padC1_padP2_conn": with_rejection(lambda n, m, d, r: pad_patterns(pad_customers(bern(n, m, 1.10 * d / n, r), 1, r), 2, r), CAP),
})
