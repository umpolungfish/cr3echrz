"""
state.py — Connes Embedding automaton data layer.

II_1 factor embedding landscape.

STATUS register (2-bit Belnap FOUR):
  0b00  N  — unclassified (no trace or embedding defined)
  0b01  T  — embeddable (factor embeds in R^omega)
  0b10  F  — non-embeddable (MIP*=RE counterexample, JNVWY 2020)
  0b11  B  — pre-2020 unresolved paradox (Connes conjecture open)
"""
from dataclasses import dataclass
from typing import Optional

# STATUS constants
VOID           = 0b00   # N
EMBEDDABLE     = 0b01   # T
NON_EMBEDDABLE = 0b10   # F
PARADOX        = 0b11   # B

# Global state (mutable dict — single engine instance)
state = {
    'factor':     None,
    'ultrapower': None,
    'status':     VOID,
    'use_2020':   False,
    'history':    [],
}


@dataclass
class II1Factor:
    name:             str
    trace:            Optional[str] = None
    is_hyperfinite:   bool          = False
    embedding_status: Optional[str] = None


@dataclass
class Ultrapower:
    base:        II1Factor
    ultrafilter: str = "free_omega"


@dataclass
class Norm:
    value:    str    # "spatial" or "projective"
    is_equal: bool   # True if min == max (factor is embeddable)


@dataclass
class Embedding:
    source:              II1Factor
    target:              Ultrapower
    is_trace_preserving: bool = False
    success:             bool = False


def status_name(s: int) -> str:
    return {
        VOID:           'VOID(N)',
        EMBEDDABLE:     'EMBEDDABLE(T)',
        NON_EMBEDDABLE: 'NON_EMBEDDABLE(F)',
        PARADOX:        'PARADOX(B)',
    }.get(s, f'???({s})')
