#!/usr/bin/env python3
"""
cr3echrz — Unified cr3echrz Framework

12 universal IMASM opcodes, 7 theorem engines, 271 vault ob3ects,
Belnap FOUR logic, Frobenius verification (μ∘δ=id).

Author: Lando⊗⊙perator
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Lando⊗⊙perator"

from cr3echrz.shared import (
    BelnapRegister,
    FrobeniusVerifier,
    OPCODES,
    OPCODE_GRAMMAR_MAP,
    domain_category,
    EXEC_DOMAINS,
    SYMBOLIC_DOMAINS,
)

__all__ = [
    "__version__",
    "__author__",
    "BelnapRegister",
    "FrobeniusVerifier",
    "OPCODES",
    "OPCODE_GRAMMAR_MAP",
    "domain_category",
    "EXEC_DOMAINS",
    "SYMBOLIC_DOMAINS",
]
