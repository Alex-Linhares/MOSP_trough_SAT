import Lake
open Lake DSL

package MOSPFormalization where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

@[default_target]
lean_lib MOSPFormalization where
  srcDir := "."

require "leanprover-community" / "mathlib" @ git "master"
