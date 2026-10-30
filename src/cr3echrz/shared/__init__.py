#!/usr/bin/env python3
"""
shared/ — Universal primitives for the cr3echrz framework

Extracted and unified from p3theorem, ob3ect_vault, and unified_driver.

Author: Lando⊗⊙perator
Date: 2026-06-23
"""
from .belnap import BelnapRegister
from .frobenius import FrobeniusVerifier
from .opcodes import OPCODES, OPCODE_GRAMMAR_MAP
from .domains import domain_category, EXEC_DOMAINS, SYMBOLIC_DOMAINS

__all__ = [
    'BelnapRegister', 'FrobeniusVerifier',
    'OPCODES', 'OPCODE_GRAMMAR_MAP',
    'domain_category', 'EXEC_DOMAINS', 'SYMBOLIC_DOMAINS',
]
