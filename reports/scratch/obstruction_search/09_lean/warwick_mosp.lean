import MOSPFormalization.ObstructionCertificate
open MOSPFormalization
namespace Warwick
def ones : List (ℕ × ℕ) := [(0, 18), (1, 7), (1, 8), (1, 14), (1, 20), (2, 4), (2, 15), (2, 20), (2, 26), (3, 6), (3, 10), (3, 14), (4, 6), (4, 22), (4, 27), (5, 1), (5, 8), (5, 13), (5, 21), (6, 0), (6, 16), (6, 19), (6, 28), (6, 29), (7, 7), (7, 21), (8, 8), (8, 12), (8, 15), (9, 3), (10, 17), (11, 10), (11, 23), (12, 5), (12, 6), (12, 17), (12, 26), (13, 1), (13, 9), (14, 10), (14, 12), (14, 28), (15, 9), (15, 11), (15, 24), (16, 22), (16, 23), (16, 25), (16, 27), (17, 4), (17, 18), (18, 13), (18, 20), (18, 29), (19, 2), (20, 2), (20, 29), (21, 1), (21, 15), (22, 2), (22, 5), (22, 7), (22, 9), (22, 11), (22, 24), (22, 25), (23, 11), (24, 16), (24, 18), (25, 3), (25, 4), (25, 25), (25, 27), (26, 0), (26, 5), (26, 19), (26, 26), (26, 28), (27, 0), (27, 17), (27, 23), (28, 22), (29, 3), (29, 12), (29, 13), (29, 14), (29, 16), (29, 19), (29, 21), (29, 24)]
def M : MOSPInstance (Fin 30) (Fin 30) where
  requires c p := (c.val, p.val) ∈ ones
instance : DecidableRel M.requires := fun c p => inferInstanceAs (Decidable ((c.val, p.val) ∈ ones))
def seq : List (Fin 30 × Option (Fin 30)) := [(0, some 17), (9, some 25), (10, some 27), (19, some 20), (23, some 15), (28, some 4), (15, some 13), (17, some 24), (20, some 18), (4, some 16), (7, some 5), (11, some 27), (13, some 21), (24, some 25), (16, some 25), (21, some 2), (8, some 14), (3, some 1), (5, some 14), (6, some 18), (12, some 26), (27, some 14)]
set_option maxRecDepth 100000 in
theorem seq_legal : IsContractionSeq M.mospGraph seq := by decide +kernel
set_option maxRecDepth 100000 in
theorem seq_minDegree : 7 ≤ minDegreeOfMinor M.mospGraph seq := by decide +kernel
theorem eight_le_mospValue : 8 ≤ M.mospValue :=
  M.mospValue_ge_of_minor_minDegree ⟨0, 18, by decide⟩ seq seq_legal _ seq_minDegree
end Warwick
