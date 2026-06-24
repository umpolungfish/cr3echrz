"""
cr3echrz.p4rakernel — P4RA Kernel Theorem Modules

Six standalone Belnap+Frobenius operationalizations of open mathematical problems,
each executing the 12 universal IMASM opcodes with Frobenius verification (μ∘δ=id).

Modules:
    burnside    — Bounded Burnside Problem: B(m,n) group finiteness
    connes      — Connes Embedding Problem: II₁ factor embeddability in R^ω
    erdos_straus — Erdős–Straus Conjecture: 4/n = 1/x + 1/y + 1/z
    goldbach    — Goldbach's Conjecture: even n ≥ 4 = p + q
    landau      — Landau's Theorems: holomorphic functions on the unit disk
    threebody   — Three-Body Problem: Hamiltonian non-integrability

Author: Lando⊗⊙perator
Date: 2026-06-24
"""

# Module registry — maps short names to their run functions
P4RA_MODULES = {
    "burnside":     "cr3echrz.p4rakernel.burnside",
    "connes":       "cr3echrz.p4rakernel.connes",
    "erdos_straus": "cr3echrz.p4rakernel.erdos_straus",
    "goldbach":     "cr3echrz.p4rakernel.goldbach",
    "landau":       "cr3echrz.p4rakernel.landau",
    "threebody":    "cr3echrz.p4rakernel.threebody",
}

P4RA_DESCRIPTIONS = {
    "burnside":     "Bounded Burnside Problem — B(m,n) group finiteness (Burnside 1902 / Novikov-Adian 1968)",
    "connes":       "Connes Embedding Problem — II₁ factor embeddability in R^ω (JNVWY 2020: MIP*=RE)",
    "erdos_straus": "Erdős–Straus Conjecture — 4/n = 1/x + 1/y + 1/z (1948)",
    "goldbach":     "Goldbach's Conjecture — every even n ≥ 4 is sum of two primes (1742)",
    "landau":       "Landau's Theorems — holomorphic functions on the unit disk (Landau 1904)",
    "threebody":    "Three-Body Problem — Hamiltonian non-integrability (Poincaré 1890)",
}
