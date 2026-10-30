"""
cr3echrz.p4rakernel.threebody — Three-Body Problem

Poincaré (1890): the gravitational three-body problem has no general
analytic solution — it is non-integrable. The figure-8 periodic orbit
(Chénciner-Montgomery 2000) provides a Belnap BOTH state: simultaneously
deterministic (T) and non-integrable (F).

Implements Liouville integrability probe as TANCH verification,
Hamiltonian flow as AFWD/AREV pair, and Poincaré section as FSPLIT.
"""
from cr3echrz.p4rakernel.threebody.main import run_threebody_protocol
from cr3echrz.p4rakernel.threebody.state import STATUS, vinit, imscrib, compute_conserved, figure8_ic, pythagorean_ic

# Status constants (2-bit)
VOID          = 0b00
INTEGRABLE    = 0b01
NON_INTEGRABLE = 0b10
PARADOX       = 0b11

def status_name(s: int) -> str:
    return {
        VOID:          'VOID',
        INTEGRABLE:    'INTEGRABLE',
        NON_INTEGRABLE: 'NON_INTEGRABLE',
        PARADOX:       'PARADOX (KAM)',
    }.get(s, f'???({s})')
