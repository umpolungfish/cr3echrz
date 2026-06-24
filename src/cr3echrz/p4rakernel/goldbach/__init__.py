"""
cr3echrz.p4rakernel.goldbach — Goldbach's Conjecture

"Every even integer n ≥ 4 is the sum of two primes." Goldbach (1742).
Verified for n < 4×10¹⁸ (Oliveira e Silva 2014); unproven in general.

Implements prime-pair enumeration as FSPLIT, with FFUSE reconstituting n.
"""
from cr3echrz.p4rakernel.goldbach.main import run_goldbach
from cr3echrz.p4rakernel.goldbach.state import state, status_name, VOID, FOUND, COUNTER, MULTIPLE
