/-
Copyright (c) 2026 Alexandre Linhares. All rights reserved.
Released under the MIT license as described in the file LICENSE.

# The customer search, assembled: a refutation means MOSP > k and pw > k − 1

Loop0006 item 12, `paper1/search_soundness.md` §5. Source: Chu & Stuckey, *Minimizing the
maximum number of open stacks by customer search*, CP 2009, §3 (the search and Theorems 1–3),
as implemented by `satisfiability/customer_search.py` (`decide`) and
`satisfiability/customer_search.c` (`search`, `dominance_filter`).

The abstract search is `Exec` (`Memo.lean`): the tree of free-closed states, each node
pruned by an abstract filter `F` at `(S, Q)`, with free moves (`cl`), the memo (any policy),
old moves (any inherited subset passing the code's test) and any child order. This file
instantiates it with the rules of items 07–11 in the code's order and draws the corollaries.

## What is proved

* **The repaired search** (`definite → subset → better` with both repairs, any `L`):
  - `exec_repairedFullFilter_narrowness`: a run from the root answering `false` gives
    `k < narrowness G`;
  - `exec_repairedFullFilter_pathwidth`: `k ≤ pathwidth G`, that is `pw(G) > k − 1`, for `V`
    nonempty;
  - `exec_repairedFullFilter_mospValue`: on the MOSP graph of an instance with a requirement,
    `k < mospValue M`; and `exec_repairedFullFilter_mospGraph_pathwidth`, `k ≤ pw(G_M)`.
* **The search as coded** (`codeFullFilter`, the published premises `close ≥ open` for the
  definite move and the corrected premise 4 for the better move) is **not** node-sound
  (`DefiniteMove.lean`, `BetterMove.lean`), and `not_codeFilterSound_cexGraph` restates this
  against the named property `CodeFilterSound G k L` (node soundness of the code's filter at
  every state of one instance at one `k`), which fails on `cexGraph` at `k = 6` for every `L`.
  What holds for it is conditional, and the condition is named, never assumed silently:
  - `ExecOn N` is `Exec` with every node of the run required to satisfy `N`, and
    `ExecOn.sound` needs the filter node-sound only at those nodes (`NodeSoundAt`);
  - `codeExec_sound_of_runSound`: if every node of the code's run is a node where the
    code's filter is node-sound, the refutation is genuine (`¬ Solvable G k ∅`); this is the
    stated gap, **"the code's filter never loses the last solution at a node of its own
    run"**, used as an explicit hypothesis;
  - `codeExec_sound_of_codeFilterSound`: the same from `CodeFilterSound G k L` for the
    instance at hand;
  - `nodeSoundAt_codeFullFilter_of_repaired`: a **checkable** sufficient condition at one
    node, `CodeNodeRepaired`: the definite move, if it fires, fires on a hereditarily
    definite customer; if it does not fire, every customer the better move drops has *some*
    earlier cited survivor meeting the repaired premise. `codeExec_sound_of_repaired`: a run of the code
    each of whose nodes passes this check is sound. This is what a certificate would have
    to carry to certify the code's refutations under the repaired theorems.
  - Corollaries in MOSP and pathwidth form for all three.

* **The certificate checker's node check** (`learning/search_certificate.py`, steps 4–5):
  `nodeSoundAt_of_covering` — if every cited link carries a solution forward and every
  playable candidate outside `Q` reaches a kept child or an old move along cited links
  (`Covered`), the filter is node-sound there. The links are justified by
  `definite_link` (repaired premise), `searchSol_cl_insert_of_newlyOpened_subset` (subset)
  and `searchSol_cl_insert_of_repairedBetter` (repaired better move); Cert checks the
  code's premises for the first and the last, which `definiteMove_counterexample` and
  `betterMove_counterexample` show can certify a false link. `paper1/search_soundness.md`
  §5.3 has the table.

No whole-instance false refutation by the code is known (`search_soundness.md` §2.2, §4.2,
§4.4): the gap is at the node, and whether it ever reaches a root answer is open.

## Checks

`python -m paper1.search_check --decide` (`paper1/search_check.py`) runs the search with old
move and the memo on every labelled graph on 1–6 vertices and a sample beyond, and checks at
every node of every run the conditions named here; see `paper1/search_soundness.md` §5.
-/

import MOSPFormalization.Search.Memo

set_option linter.unusedSectionVars false

namespace MOSPFormalization

namespace Search

open Finset

/-! ### Node soundness at one node, and runs that visit only such nodes -/

section General

variable {V : Type*} [Fintype V] [DecidableEq V]
variable (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ)
variable (F : Finset V → Finset V → Finset V)

/-- The filter is node-sound at the node `(S, Q)` (`search_soundness.md` §2.0): under the node
invariant, with `Q` refuted, a solution at `S` survives in some kept child. -/
def NodeSoundAt (S Q : Finset V) : Prop :=
  (opened G S \ S).card ≤ k → S ≠ univ → (∀ q ∈ Q, ¬ SearchSol G k (cl G (insert q S))) →
    SearchSol G k S → ∃ c ∈ F S Q, SearchSol G k (cl G (insert c S))

theorem filterSound_iff : FilterSound G k F ↔ ∀ S Q, NodeSoundAt G k F S Q := Iff.rfl

/-- `ExecOn G k F N`: `Exec` in which every node expanded (`Exec.node`, with the filter applied
at `(S, Q ∖ S)`) satisfies `N`. -/
inductive ExecOn (N : Finset V → Finset V → Prop) :
    Set (Finset V) → Finset V → Finset V → Option (List V) → Set (Finset V) → Prop
  | hit {M : Set (Finset V)} {S Q : Finset V} : S ∈ M → ExecOn N M S Q none M
  | node {M M' : Set (Finset V)} {S Q : Finset V} (l : List V) (record : Bool) : S ≠ univ →
      N S (Q \ S) → (∀ c, c ∈ l ↔ c ∈ F S (Q \ S)) → ExecOn N M S (Q \ S) (some l) M' →
      ExecOn N M S Q none (if record then insert S M' else M')
  | nil {M : Set (Finset V)} {S seen : Finset V} : ExecOn N M S seen (some []) M
  | cons {M M₁ M₂ : Set (Finset V)} {S seen Q' : Finset V} (c : V) (l : List V) :
      Q' ⊆ seen.filter (fun q => stepCost G (insert q S) c ≤ k) →
      ExecOn N M (cl G (insert c S)) Q' none M₁ → ExecOn N M₁ S (insert c seen) (some l) M₂ →
      ExecOn N M S seen (some (c :: l)) M₂

variable {G k F}

/-- Every run is a run on the trivial node predicate. -/
theorem Exec.execOn {M M' : Set (Finset V)} {S Q : Finset V} {o : Option (List V)}
    (h : Exec G k F M S Q o M') : ExecOn G k F (fun _ _ => True) M S Q o M' := by
  induction h with
  | hit hS => exact ExecOn.hit hS
  | node l record hS hl _ ih => exact ExecOn.node l record hS trivial hl ih
  | nil => exact ExecOn.nil
  | cons c l hQ' _ _ ihc ihl => exact ExecOn.cons c l hQ' ihc ihl

/-- An `ExecOn` run is an `Exec` run. -/
theorem ExecOn.exec {N : Finset V → Finset V → Prop} {M M' : Set (Finset V)} {S Q : Finset V}
    {o : Option (List V)} (h : ExecOn G k F N M S Q o M') : Exec G k F M S Q o M' := by
  induction h with
  | hit hS => exact Exec.hit hS
  | node l record hS _ hl _ ih => exact Exec.node l record hS hl ih
  | nil => exact Exec.nil
  | cons c l hQ' _ _ ihc ihl => exact Exec.cons c l hQ' ihc ihl

/-- Weakening the node predicate. -/
theorem ExecOn.mono {N N' : Finset V → Finset V → Prop} (hN : ∀ S Q, N S Q → N' S Q)
    {M M' : Set (Finset V)} {S Q : Finset V} {o : Option (List V)}
    (h : ExecOn G k F N M S Q o M') : ExecOn G k F N' M S Q o M' := by
  induction h with
  | hit hS => exact ExecOn.hit hS
  | node l record hS hNS hl _ ih => exact ExecOn.node l record hS (hN _ _ hNS) hl ih
  | nil => exact ExecOn.nil
  | cons c l hQ' _ _ ihc ihl => exact ExecOn.cons c l hQ' ihc ihl

/-- A run over a node predicate `N` turns into a run over "`F` is node-sound here" as soon as
`F` is node-sound wherever `N` holds. -/
theorem ExecOn.of_nodeSound {N : Finset V → Finset V → Prop}
    (hN : ∀ S Q, N S Q → NodeSoundAt G k F S Q) {M M' : Set (Finset V)} {S Q : Finset V}
    {o : Option (List V)} (h : ExecOn G k F N M S Q o M') :
    ExecOn G k F (NodeSoundAt G k F) M S Q o M' :=
  h.mono hN

/-- **`Exec.sound`, localised to the run.** The filter needs to be node-sound only at the nodes
the run expands. -/
theorem ExecOn.sound (hP : FilterPlayable G k F)
    {M M' : Set (Finset V)} {S Q : Finset V} {o : Option (List V)}
    (h : ExecOn G k F (NodeSoundAt G k F) M S Q o M') :
    (opened G S \ S).card ≤ k → (∀ T ∈ M, ¬ SearchSol G k T) →
      (∀ q ∈ Q, q ∉ S → ¬ SearchSol G k (cl G (insert q S))) →
      (∀ l, o = some l → ∀ c ∈ l, c ∉ S ∧ stepCost G S c ≤ k) →
      (∀ T ∈ M', ¬ SearchSol G k T) ∧ (o = none → ¬ SearchSol G k S) ∧
        (∀ l, o = some l → ∀ c ∈ l, ¬ SearchSol G k (cl G (insert c S))) := by
  induction h with
  | hit hS =>
    intro _ hM _ _
    exact ⟨hM, (fun _ => hM _ hS), (fun _ h => by cases h)⟩
  | @node M M' S Q l record hS hNS hl _ ih =>
    intro hk hM hQ _
    have hQ' : ∀ q ∈ Q \ S, q ∉ S → ¬ SearchSol G k (cl G (insert q S)) :=
      fun q hq hqS => hQ q (mem_sdiff.1 hq).1 hqS
    obtain ⟨hM', -, hchildren⟩ := ih hk hM hQ'
      (fun l' hl' c hc => hP S _ c ((hl c).1 (by cases hl'; exact hc)))
    have hnot : ¬ SearchSol G k S := fun hs => by
      obtain ⟨c, hc, hcs⟩ := hNS hk hS (fun q hq => hQ' q hq (mem_sdiff.1 hq).2) hs
      exact hchildren l rfl c ((hl c).2 hc) hcs
    refine ⟨?_, (fun _ => hnot), (fun _ h => by cases h)⟩
    cases record
    · exact hM'
    · intro T hT
      rcases Set.mem_insert_iff.1 hT with rfl | hT
      · exact hnot
      · exact hM' T hT
  | nil =>
    intro _ hM _ _
    exact ⟨hM, (fun h => by cases h), (fun _ h => by cases h; simp)⟩
  | @cons M M₁ M₂ S seen Q' c l hQ' _ _ ihc ihl =>
    intro hk hM hseen hl
    obtain ⟨hcS, hck⟩ := hl _ rfl c (List.mem_cons_self ..)
    have hkc := card_opened_cl_insert_sdiff_le_of_playable hcS hck
    have hQc : ∀ q ∈ Q', q ∉ cl G (insert c S) →
        ¬ SearchSol G k (cl G (insert q (cl G (insert c S)))) := by
      intro q hq hqc hs
      obtain ⟨hqseen, htest⟩ := mem_filter.1 (hQ' hq)
      exact hseen q hqseen (fun h => hqc (subset_cl_insert S c h)) (searchSol_reinsert htest hs)
    obtain ⟨hM₁, hc, -⟩ := ihc hkc hM hQc (fun _ h => by cases h)
    have hc := hc rfl
    have hseen' : ∀ q ∈ insert c seen, q ∉ S → ¬ SearchSol G k (cl G (insert q S)) := by
      intro q hq hqS
      rcases mem_insert.1 hq with rfl | hq
      · exact hc
      · exact hseen q hq hqS
    obtain ⟨hM₂, -, hrest⟩ := ihl hk hM₁ hseen'
      (fun _ h c' hc' => hl _ rfl c' (List.mem_cons_of_mem _ (by cases h; exact hc')))
    refine ⟨hM₂, (fun h => by cases h), fun l' h c' hc' => ?_⟩
    cases h
    rcases List.mem_cons.1 hc' with rfl | hc'
    · exact hc
    · exact hrest l rfl c' hc'

/-- A run from the root that expands only nodes where its filter is node-sound refutes
`Solvable G k ∅`. -/
theorem execOn_root_sound (hP : FilterPlayable G k F) {M' : Set (Finset V)}
    (h : ExecOn G k F (NodeSoundAt G k F) ∅ ∅ ∅ none M') : ¬ Solvable G k ∅ := by
  rw [solvable_empty_iff]
  exact (h.sound hP (by simp [opened_empty]) (fun _ h => absurd h (Set.notMem_empty _))
    (fun _ h => absurd h (Finset.notMem_empty _)) (fun _ h => by cases h)).2.1 rfl

/-! ### The certificate checker's covering condition (Cert step 5) -/

/-- `Covered K Q cite c`: from the candidate `c`, following cited links `cite r d`
(`r` covered by `d`), one reaches a kept child (`K`) or an old move (`Q`). This is what the
certificate checker's step 5 walks (`learning/search_certificate.py`, "exhaustiveness"); its
cycle check is what makes the walk finite, and finiteness is what the inductive asserts. -/
inductive Covered (K Q : Finset V) (cite : V → V → Prop) : V → Prop
  | kept {c : V} : c ∈ K → Covered K Q cite c
  | old {c : V} : c ∈ Q → Covered K Q cite c
  | link {c d : V} : cite c d → Covered K Q cite d → Covered K Q cite c

/-- **Cert's node check is node soundness**, given sound links: if every cited link
`r → d` carries a solution from `S·r` to `S·d`, and every playable candidate outside `Q` is
`Covered`, then the filter is node-sound at `(S, Q)`. -/
theorem nodeSoundAt_of_covering {S Q : Finset V} (cite : V → V → Prop)
    (hcite : SearchSol G k S → ∀ r d, cite r d → SearchSol G k (cl G (insert r S)) →
      SearchSol G k (cl G (insert d S)))
    (hcov : ∀ c, c ∉ S → c ∉ Q → stepCost G S c ≤ k → Covered (F S Q) Q cite c) :
    NodeSoundAt G k F S Q := by
  intro _ hS hQ hs
  have key : ∀ c, Covered (F S Q) Q cite c → SearchSol G k (cl G (insert c S)) →
      ∃ c' ∈ F S Q, SearchSol G k (cl G (insert c' S)) := by
    intro c hc
    induction hc with
    | kept h => exact fun hcs => ⟨_, h, hcs⟩
    | old h => exact fun hcs => absurd hcs (hQ _ h)
    | link h _ ih => exact fun hcs => ih (hcite hs _ _ h hcs)
  cases hs with
  | done h => exact absurd h hS
  | step c hcS hck hcs =>
    by_cases hcQ : c ∈ Q
    · exact absurd hcs (hQ c hcQ)
    · exact key c (hcov c hcS hcQ hck) hcs

end General

/-! ### The links Cert's step 4 checks, in the form `Sol_k(S·r) → Sol_k(S·d)` -/

section Links

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

/-- A definite link `r → q` (Cert records one for every other playable `r` when the definite
move fires) is sound when `q` is hereditarily definite: `Sol(S·r)` gives `Sol(S)`, which
gives `Sol(S·q)`. With the code's premise `IsDefinite` it is not
(`definiteMove_counterexample`). -/
theorem definite_link {k : ℕ} {S : Finset V} {q r : V} (hq : IsHereditarilyDefinite G S q)
    (hqS : q ∉ S) (hk : (opened G S \ S).card ≤ k) (hrS : r ∉ S) (hr : stepCost G S r ≤ k)
    (h : SearchSol G k (cl G (insert r S))) : SearchSol G k (cl G (insert q S)) :=
  searchSol_cl_insert_of_hereditarilyDefinite hq hqS hk (SearchSol.step r hrS hr h)

end Links

/-! ### The repaired search: a refutation means MOSP > k and pw > k − 1 -/

section Repaired

variable {V : Type*} [Fintype V] [LinearOrder V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

/-- A refutation by the repaired search is a lower bound on narrowness. -/
theorem exec_repairedFullFilter_narrowness {k L : ℕ} {M' : Set (Finset V)}
    (h : Exec G k (repairedFullFilter G k L) ∅ ∅ ∅ none M') : k < Complex.narrowness G := by
  have := exec_repairedFullFilter_sound h
  rw [solvable_empty_iff, searchSol_empty_iff_narrowness_le] at this
  omega

/-- **A refutation by the repaired search means `pw(G) > k − 1`.** -/
theorem exec_repairedFullFilter_pathwidth [Nonempty V] {k L : ℕ} {M' : Set (Finset V)}
    (h : Exec G k (repairedFullFilter G k L) ∅ ∅ ∅ none M') : k ≤ pathwidth G := by
  have := exec_repairedFullFilter_sound h
  rw [solvable_empty_iff, searchSol_empty_iff_pathwidth_add_one_le] at this
  omega

end Repaired

section RepairedMOSP

variable {C Pt : Type*} [Fintype C] [LinearOrder C] [Fintype Pt] [DecidableEq Pt]

/-- **A refutation by the repaired search on the MOSP graph means MOSP > k.** -/
theorem exec_repairedFullFilter_mospValue (M : MOSPInstance C Pt) [DecidableRel M.requires]
    (hreq : ∃ c p, M.requires c p) {k L : ℕ} {M' : Set (Finset C)}
    (h : Exec M.mospGraph k (repairedFullFilter M.mospGraph k L) ∅ ∅ ∅ none M') :
    k < M.mospValue := by
  have := exec_repairedFullFilter_sound h
  rw [solvable_empty_iff, searchSol_mospGraph_iff_mospValue_le M hreq] at this
  omega

/-- The same refutation, in pathwidth form: `pw(G_M) > k − 1`. -/
theorem exec_repairedFullFilter_mospGraph_pathwidth (M : MOSPInstance C Pt)
    [DecidableRel M.requires] (hreq : ∃ c p, M.requires c p) {k L : ℕ} {M' : Set (Finset C)}
    (h : Exec M.mospGraph k (repairedFullFilter M.mospGraph k L) ∅ ∅ ∅ none M') :
    k ≤ pathwidth M.mospGraph := by
  have : Nonempty C := let ⟨c, _⟩ := hreq; ⟨c⟩
  exact exec_repairedFullFilter_pathwidth h

end RepairedMOSP

/-! ### The search as coded: the named gap, and a checkable sufficient condition -/

section Code

variable {V : Type*} [Fintype V] [LinearOrder V]
variable (G : SimpleGraph V) [DecidableRel G.Adj]

theorem codeFullFilter_playable (k L : ℕ) : FilterPlayable G k (codeFullFilter G k L) := by
  intro S Q c hc
  obtain ⟨hcK, hck⟩ := mem_filter.1 (fullFilter_subset _ _ S _ hc)
  exact ⟨(mem_sdiff.1 (mem_sdiff.1 hcK).1).2, hck⟩

/-- **The named property the code's refutations rest on**, for one instance at one `k`: the
code's filter is node-sound at every state. It is false in general
(`not_codeFilterSound_cexGraph`). -/
def CodeFilterSound (k L : ℕ) : Prop := FilterSound G k (codeFullFilter G k L)

/-- **The run-local form of the gap**: the run expands only nodes at which the code's filter
keeps a solution whenever one exists. -/
def CodeRunSound (k L : ℕ) (M' : Set (Finset V)) : Prop :=
  ExecOn G k (codeFullFilter G k L) (NodeSoundAt G k (codeFullFilter G k L)) ∅ ∅ ∅ none M'

/-- A checkable condition at one node: the definite move, if it fires, fires on a hereditarily
definite customer (item 08's repair); if it does not fire, every customer the better move drops
has some earlier cited survivor (within the limit) meeting the repaired premise (item 10's
repair). -/
def CodeNodeRepaired (k L : ℕ) (S Q : Finset V) : Prop :=
  (∀ h : ((playable G k S ((univ \ S) \ Q)).filter (IsDefinite G S)).Nonempty,
      IsHereditarilyDefinite G S
        (((playable G k S ((univ \ S) \ Q)).filter (IsDefinite G S)).min' h)) ∧
  (¬ ((playable G k S ((univ \ S) \ Q)).filter (IsDefinite G S)).Nonempty →
  ∀ r ∈ subsetFilter G S (playable G k S ((univ \ S) \ Q)),
    (∃ q ∈ subsetFilter G S (playable G k S ((univ \ S) \ Q)), q < r ∧
      betterCite G k L S (subsetFilter G S (playable G k S ((univ \ S) \ Q))) r q) →
    ∃ q ∈ subsetFilter G S (playable G k S ((univ \ S) \ Q)), q < r ∧
      IsRepairedBetter G k S r q)

variable {G}

/-- **The code's filter is node-sound at any node passing the check.** -/
theorem nodeSoundAt_codeFullFilter_of_repaired {k L : ℕ} {S Q : Finset V}
    (hrep : CodeNodeRepaired G k L S Q) : NodeSoundAt G k (codeFullFilter G k L) S Q := by
  intro hk hS hQ hs
  obtain ⟨hD, hB⟩ := hrep
  set P := playable G k S ((univ \ S) \ Q) with hPdef
  have hPmem : ∀ c ∈ P, c ∉ S ∧ stepCost G S c ≤ k := fun c hc => by
    obtain ⟨hcK, hck⟩ := mem_filter.1 hc
    exact ⟨(mem_sdiff.1 (mem_sdiff.1 hcK).1).2, hck⟩
  unfold codeFullFilter fullFilter
  rw [← hPdef]
  split_ifs with h
  · refine ⟨_, mem_singleton_self _, ?_⟩
    have hm := (mem_filter.1 (min'_mem _ h)).1
    exact searchSol_cl_insert_of_hereditarilyDefinite (hD h) (hPmem _ hm).1 hk hs
  · set W := subsetFilter G S P with hW
    have hWP : ∀ c ∈ W, c ∉ S ∧ stepCost G S c ≤ k := fun c hc =>
      hPmem c (subsetFilter_subset _ _ hc)
    obtain ⟨c, hc, hcs⟩ := subsetFilter_sound hQ hs hS
    classical
    set A := W.filter (fun c => SearchSol G k (cl G (insert c S)))
    have hA : A.Nonempty := ⟨c, mem_filter.2 ⟨hc, hcs⟩⟩
    obtain ⟨hmW, hms⟩ := mem_filter.1 (A.min'_mem hA)
    refine ⟨A.min' hA, mem_filter.2 ⟨hmW, ?_⟩, hms⟩
    intro hcite
    obtain ⟨q, hqW, hlt, hq⟩ := hB h _ hmW hcite
    have hqs : SearchSol G k (cl G (insert q S)) :=
      searchSol_cl_insert_of_repairedBetter (hWP _ hmW).1 (hWP q hqW).1 (hWP _ hmW).2 hq hms
    exact absurd (A.min'_le q (mem_filter.2 ⟨hqW, hqs⟩)) (not_le.2 hlt)

/-- **The code's refutations are genuine, given the named gap**: a run of the search as coded
(free moves, memo, old move, `definite → subset → better` with the published premises) that
expands only nodes where its filter is node-sound refutes `Solvable G k ∅`. -/
theorem codeExec_sound_of_runSound {k L : ℕ} {M' : Set (Finset V)}
    (h : CodeRunSound G k L M') : ¬ Solvable G k ∅ :=
  execOn_root_sound (codeFullFilter_playable G k L) h

/-- The same from the instance-wide property `CodeFilterSound`. -/
theorem codeExec_sound_of_codeFilterSound {k L : ℕ} {M' : Set (Finset V)}
    (hF : CodeFilterSound G k L) (h : Exec G k (codeFullFilter G k L) ∅ ∅ ∅ none M') :
    ¬ Solvable G k ∅ :=
  codeExec_sound_of_runSound (h.execOn.of_nodeSound fun S Q _ => (filterSound_iff ..).1 hF S Q)

/-- **A run of the code whose every node passes the repaired check is sound.** -/
theorem codeExec_sound_of_repaired {k L : ℕ} {M' : Set (Finset V)}
    (h : ExecOn G k (codeFullFilter G k L) (CodeNodeRepaired G k L) ∅ ∅ ∅ none M') :
    ¬ Solvable G k ∅ :=
  codeExec_sound_of_runSound
    (ExecOn.of_nodeSound (N := CodeNodeRepaired G k L)
      (fun _ _ hr => nodeSoundAt_codeFullFilter_of_repaired hr) h)

/-- Under the gap, a code refutation is a pathwidth lower bound. -/
theorem codeExec_pathwidth_of_runSound [Nonempty V] {k L : ℕ} {M' : Set (Finset V)}
    (h : CodeRunSound G k L M') : k ≤ pathwidth G := by
  have := codeExec_sound_of_runSound h
  rw [solvable_empty_iff, searchSol_empty_iff_pathwidth_add_one_le] at this
  omega

end Code

section CodeMOSP

variable {C Pt : Type*} [Fintype C] [LinearOrder C] [Fintype Pt] [DecidableEq Pt]

/-- Under the gap, a code refutation on the MOSP graph means MOSP > k. -/
theorem codeExec_mospValue_of_runSound (M : MOSPInstance C Pt) [DecidableRel M.requires]
    (hreq : ∃ c p, M.requires c p) {k L : ℕ} {M' : Set (Finset C)}
    (h : CodeRunSound M.mospGraph k L M') : k < M.mospValue := by
  have := codeExec_sound_of_runSound h
  rw [solvable_empty_iff, searchSol_mospGraph_iff_mospValue_le M hreq] at this
  omega

/-- A code run whose every node passes the repaired check, on the MOSP graph: MOSP > k. -/
theorem codeExec_mospValue_of_repaired (M : MOSPInstance C Pt) [DecidableRel M.requires]
    (hreq : ∃ c p, M.requires c p) {k L : ℕ} {M' : Set (Finset C)}
    (h : ExecOn M.mospGraph k (codeFullFilter M.mospGraph k L)
      (CodeNodeRepaired M.mospGraph k L) ∅ ∅ ∅ none M') : k < M.mospValue :=
  codeExec_mospValue_of_runSound M hreq
    (ExecOn.of_nodeSound (N := CodeNodeRepaired M.mospGraph k L)
      (fun _ _ hr => nodeSoundAt_codeFullFilter_of_repaired hr) h)

end CodeMOSP

/-! ### The gap is real at the node -/

theorem codeFullFilter_cex (L : ℕ) : codeFullFilter cexGraph 6 L {2} ∅ = {0} := by
  unfold codeFullFilter fullFilter
  split_ifs with h
  · congr 1
  · exact absurd (by decide +kernel) h

/-- **`CodeFilterSound` fails**: on `cexGraph` at `k = 6`, for every limit `L`, the code's filter
keeps only `0` at the free-closed state `{2}`, which has a solution while `cl({0, 2})` has none
(`definiteMove_counterexample`). -/
theorem not_codeFilterSound_cexGraph (L : ℕ) : ¬ CodeFilterSound cexGraph 6 L := by
  intro hF
  obtain ⟨_, hinv, -, -, -, -, -, hs, -, hns⟩ := definiteMove_counterexample
  obtain ⟨c, hc, hcs⟩ := hF {2} ∅ hinv (by decide) (by simp) hs
  rw [codeFullFilter_cex, mem_singleton] at hc
  subst hc
  exact hns hcs

end Search

end MOSPFormalization
