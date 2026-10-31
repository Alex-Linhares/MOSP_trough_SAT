-- Axiom audit of FirstMomentAsymptotics.lean (2026-10-31).
-- Run: cd lean && lake env lean ../reports/scratch/first_moment/lean_target_check.lean
import MOSPFormalization.FirstMomentAsymptotics
open MOSPFormalization
#print axioms one_sub_pow_le_exp_neg_mul
#print axioms choose_mul_pow_mul_pow_le_add_pow
#print axioms choose_mul_choose_mul_pow_le
#print axioms exp_mul_negMulLog_div_mul_pow
#print axioms choose_mul_choose_le_exp_entropy
#print axioms negMulLog_add_le
#print axioms negMulLog_le_negMulLog_add_sub
#print axioms negMulLog_le_negMulLog_of_le
#print axioms le_negMulLog
#print axioms negMulLog_le_add_of_abs_sub_le
#print axioms negMulLog_one_div_natCast
#print axioms one_div_le_exp_neg_one
#print axioms abs_div_sub_le_one_div
#print axioms rounding_t
#print axioms firstMomentRate_def
#print axioms firstMoment_pathwidth_le
#print axioms firstMoment_pathwidth_le_fin
#print axioms exp_bound_eq
#print axioms firstMoment_pathwidth_le_fin'
#print axioms tendsto_firstMoment_bound
#print axioms tendsto_firstMoment_pathwidth
