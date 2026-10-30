"""
cr3echrz.p4rakernel.burnside — Bounded Burnside Problem

"Must every finitely generated group of bounded exponent be finite?"
Burnside (1902) conjectured yes. Novikov-Adian (1968): no for odd n ≥ 665.

Implements the Adian δ/μ decomposition as FSPLIT/FFUSE opcode pair,
with Belnap FOUR classification: FINITE(T), INFINITE(F), PARADOX(B).

Canonical cases: B(2,3) FINITE, B(2,665) INFINITE, B(2,5) PARADOX.
"""
from cr3echrz.p4rakernel.burnside.main import run_burnside_protocol
from cr3echrz.p4rakernel.burnside.state import state, status_name, VOID, FINITE, INFINITE, PARADOX
