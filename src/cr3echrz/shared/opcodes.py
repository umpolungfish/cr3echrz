#!/usr/bin/env python3
"""
opcodes.py — The 12 universal IMASM opcodes

Every theorem and ob3ect operationalization decomposes into these 12 primitives.
They are the operational form of the 12 Imscribing Grammar primitives:

    #  Opcode    Grammar   Role
    0  VINIT     𐑼 (Ð)    Initialize the void — ground of distinction
    1  TANCH     𐑡 (Þ)    Terminal anchor — boundary condition / theorem statement
    2  FSPLIT    𐑚 (Γ)    Frobenius split δ — decomposition into (T, F) arms
    3  FFUSE     𐑙 (Σ)    Frobenius fuse μ — recomposition from arms
    4  EVALT     ⊙ (φ̂)     Evaluate-true — theorem holds / true branch
    5  EVALF     𐑖 (Ħ)    Evaluate-false — theorem fails / false branch
    6  ENGAGR    𐑳 (Σ)    Engage paradox — dialetheic boundary (both arms)
    7  AFWD      𐑾 (Ř)    Forward morphism — theorem-specific forward operation
    8  AREV      𐑬 (Φ)    Reverse morphism — theorem-specific reverse operation
    9  CLINK     𐑱 (ƒ)    Chain link — sequential composition
    10 IMSCRIB   𐑠 (ɢ)    Self-imscribe — verify constants / identity
    11 IFIX      𐑭 (Ω)    Irreversible fix — permanent record / Poincaré section

Frobenius condition: FFUSE(FSPLIT(x)) = x at every split/fuse pair.

Author: Lando⊗⊙perator
"""
from typing import Dict, Tuple

# ── Opcode registry ──────────────────────────────────────────────────

OPCODE_NAMES = [
    "VINIT",    # 0
    "TANCH",    # 1
    "FSPLIT",   # 2
    "FFUSE",    # 3
    "EVALT",    # 4
    "EVALF",    # 5
    "ENGAGR",   # 6
    "AFWD",     # 7
    "AREV",     # 8
    "CLINK",    # 9
    "IMSCRIB",  # 10
    "IFIX",     # 11
]

OPCODES = {i: name for i, name in enumerate(OPCODE_NAMES)}
OPCODE_INDEX = {name: i for i, name in enumerate(OPCODE_NAMES)}

# ── Grammar primitive mapping ────────────────────────────────────────

OPCODE_GRAMMAR_MAP: Dict[str, Tuple[str, str, str]] = {
    "VINIT":   ("𐑼", "Ð", "Dimensionality — ground of distinction"),
    "TANCH":   ("𐑡", "Þ", "Topology — boundary condition / container"),
    "FSPLIT":  ("𐑚", "Γ", "Split (δ) — Frobenius decomposition"),
    "FFUSE":   ("𐑙", "Σ", "Fuse (μ) — Frobenius recomposition"),
    "EVALT":   ("⊙",  "φ̂", "Criticality — evaluate-true gate"),
    "EVALF":   ("𐑖", "Ħ", "Chirality — evaluate-false gate"),
    "ENGAGR":  ("𐑳", "Σ", "Stoichiometry — engage paradox"),
    "AFWD":    ("𐑾", "Ř", "Coupling — forward morphism"),
    "AREV":    ("𐑬", "Φ", "Parity — reverse morphism"),
    "CLINK":   ("𐑱", "ƒ", "Kinetics — chain sequential composition"),
    "IMSCRIB": ("𐑠", "ɢ", "Composition — self-imscribe / verify"),
    "IFIX":    ("𐑭", "Ω", "Winding — irreversible fixation"),
}

# ── Frobenius pairs ──────────────────────────────────────────────────

FROBENIUS_PAIRS = [
    ("FSPLIT", "FFUSE"),   # δ then μ = id
    ("FFUSE",  "FSPLIT"),  # μ then δ (dual)
]

# ── Bootstrap canonical sequences ────────────────────────────────────

CANONICAL_SEQUENCES = {
    "I_Dialetheic_Bootstrap": [
        "VINIT", "TANCH", "FSPLIT", "EVALT", "AFWD",
        "FFUSE", "FSPLIT", "EVALF", "AREV", "FFUSE",
        "ENGAGR", "CLINK", "IMSCRIB", "IFIX", "IFIX", "TANCH"
    ],
    "II_Void_Genesis": [
        "VINIT", "IMSCRIB", "AFWD", "FSPLIT", "EVALT",
        "AFWD", "EVALF", "AREV", "FFUSE", "CLINK", "IFIX", "TANCH"
    ],
    "III_Anchor_Protocol": [
        "VINIT", "TANCH", "IMSCRIB", "AFWD", "AREV",
        "CLINK", "FSPLIT", "FFUSE", "EVALT", "EVALF", "ENGAGR", "IFIX"
    ],
    "IV_Dual_Bootstrap": [
        "VINIT", "IMSCRIB", "AFWD", "FSPLIT", "EVALT",
        "AFWD", "FFUSE", "FSPLIT", "EVALF", "AREV",
        "FFUSE", "ENGAGR", "CLINK", "IMSCRIB", "IFIX", "TANCH"
    ],
    "V_Linear_Chain": [
        "VINIT", "TANCH", "AFWD", "CLINK", "AREV", "IMSCRIB", "IFIX"
    ],
    "VI_Empty_Bootstrap": [
        "VINIT", "TANCH"
    ],
    "VII_Parakernel": [
        "VINIT", "TANCH", "IMSCRIB", "FSPLIT", "EVALT",
        "FFUSE", "FSPLIT", "EVALF", "FFUSE", "ENGAGR",
        "CLINK", "AFWD", "AREV", "IMSCRIB", "IFIX", "TANCH"
    ],
    "VIII_Frobenius_Kernel": [
        "VINIT", "FSPLIT", "FFUSE", "TANCH"
    ],
    "IX_Chiral_Pairs": [
        "VINIT", "EVALT", "EVALF", "ENGAGR", "FSPLIT", "FFUSE", "TANCH"
    ],
    "X_Truth_Machine": [
        "VINIT", "TANCH", "IMSCRIB", "EVALT", "AFWD",
        "FSPLIT", "FFUSE", "EVALF", "AREV", "CLINK", "IFIX"
    ],
    "XI_Eternal_Return": [
        "VINIT", "AFWD", "CLINK", "AREV", "ENGAGR", "IMSCRIB", "IFIX", "TANCH"
    ],
    "XII_ROM_Burn": [
        "VINIT", "IMSCRIB", "IFIX", "TANCH"
    ],
}
