"""
cr3echrz.p4rakernel.connes — Connes Embedding Problem

"Does every separable II₁ factor embed in the ultrapower R^ω of the
hyperfinite II₁ factor?" Connes (1976) conjectured yes.
Ji-Natarajan-Vidick-Wright-Yuen (2020): no — MIP*=RE refutes embeddability.

Implements C*-tensor norm bifurcation as FSPLIT, with MIP*=RE as CLINK.
"""
from cr3echrz.p4rakernel.connes.main import run_connes_protocol
from cr3echrz.p4rakernel.connes.state import state, status_name, VOID, EMBEDDABLE, NON_EMBEDDABLE, PARADOX
