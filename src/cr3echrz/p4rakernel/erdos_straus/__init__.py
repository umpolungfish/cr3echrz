"""
cr3echrz.p4rakernel.erdos_straus — Erdős–Straus Conjecture

"For every n ≥ 2, 4/n = 1/x + 1/y + 1/z with x,y,z positive integers."
Erdős-Straus (1948). Verified computationally for n ≤ 10¹⁴; unproven in general.

Implements congruence-class branching (n mod 4) as FSPLIT/greedy decomposition.
"""
from cr3echrz.p4rakernel.erdos_straus.main import run_erdos_straus
from cr3echrz.p4rakernel.erdos_straus.state import state, status_name, VOID, FOUND, FAILED, MULTIPLE
