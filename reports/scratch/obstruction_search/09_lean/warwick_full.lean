import MOSPFormalization.ObstructionCertificate
open MOSPFormalization
namespace Warwick
def edges : List (ℕ × ℕ) := [(0, 17), (0, 24), (1, 2), (1, 3), (1, 5), (1, 7), (1, 8), (1, 18), (1, 22), (1, 29), (2, 8), (2, 12), (2, 17), (2, 18), (2, 21), (2, 25), (2, 26), (3, 4), (3, 11), (3, 12), (3, 14), (3, 29), (4, 12), (4, 16), (4, 25), (4, 28), (5, 7), (5, 8), (5, 13), (5, 18), (5, 21), (5, 29), (6, 14), (6, 18), (6, 20), (6, 24), (6, 26), (6, 27), (6, 29), (7, 22), (7, 29), (8, 14), (8, 21), (8, 29), (9, 25), (9, 29), (10, 12), (10, 27), (11, 14), (11, 16), (11, 27), (12, 22), (12, 26), (12, 27), (13, 15), (13, 21), (13, 22), (14, 26), (14, 29), (15, 22), (15, 23), (15, 29), (16, 22), (16, 25), (16, 27), (16, 28), (17, 24), (17, 25), (18, 20), (18, 29), (19, 20), (19, 22), (20, 22), (22, 23), (22, 25), (22, 26), (22, 29), (24, 29), (25, 29), (26, 27), (26, 29)]
def G : SimpleGraph (Fin 30) := SimpleGraph.fromRel fun a b => (a.val, b.val) ∈ edges
instance : DecidableRel G.Adj := fun a b =>
  inferInstanceAs (Decidable (a ≠ b ∧ ((a.val, b.val) ∈ edges ∨ (b.val, a.val) ∈ edges)))
def seq : List (Fin 30 × Option (Fin 30)) := [(0, some 17), (9, some 25), (10, some 27), (19, some 20), (23, some 15), (28, some 4), (15, some 13), (17, some 24), (20, some 18), (4, some 16), (7, some 5), (11, some 27), (13, some 21), (24, some 25), (16, some 25), (21, some 2), (8, some 14), (3, some 1), (5, some 14), (6, some 18), (12, some 26), (27, some 14)]
set_option maxRecDepth 100000 in
theorem seq_checked : checkSeq G seq = true := by decide +kernel
set_option maxRecDepth 100000 in
theorem seq_minDegree : minDegreeOfMinor G seq = 7 := by decide +kernel
theorem seven_le_pathwidth : 7 ≤ pathwidth G :=
  pathwidth_ge_of_checkSeq G seq seq_checked (by rw [seq_minDegree])
end Warwick
