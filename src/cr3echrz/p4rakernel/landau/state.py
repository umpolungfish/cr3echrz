"""
state.py — Landau's Theorems automaton data layer.

Holomorphic functions on the unit disk D = {|z| < 1},
Landau omission dichotomy, and the universal Landau constant.

STATUS register (2-bit Belnap FOUR):
  0b00  N  — uninitialized; no normalization, no constraint
  0b01  T  — BOUNDED: f omits a finite value; Landau bound |f'(0)| <= L active
  0b10  F  — UNBOUNDED: f has dense range; Landau bound silent; unrestricted regime
  0b11  B  — PICARD: essential singularity; both T and F simultaneously
             (f omits at most one value AND has dense range — Picard entanglement)

Key constants:
  LANDAU_L ~ 0.5433  Landau's constant (best known lower bound; exact value open)
  KOEBE_K  = 0.25    Koebe 1/4-theorem: minimum schlicht image radius
  BLOCH_B  ~ 0.4332  Bloch's constant (approximate)
"""
from dataclasses import dataclass, field
from typing import Optional

# Mathematical constants
LANDAU_L = 0.5432588512   # Landau's constant (lower bound >= 0.5 confirmed)
KOEBE_K  = 0.25           # Koebe 1/4-theorem constant (exact)
BLOCH_B  = 0.4332         # Bloch's constant (approximate)

# STATUS constants
VOID      = 0b00   # N
BOUNDED   = 0b01   # T
UNBOUNDED = 0b10   # F
PICARD    = 0b11   # B

# Per-case state (reset each run)
state = {
    'function':   None,
    'status':     VOID,
    'L_recorded': None,   # Landau constant once fixed by IFIX
    'history':    [],
}

# Permanent record (accumulates across cases)
verified: dict = {}   # name -> classification dict


@dataclass
class HolomorphicFunction:
    name:          str
    description:   str
    f0:            complex = 0+0j      # f(0) — always 0 for normalized
    fprime0:       complex = 1+0j      # f'(0) — always 1 for normalized
    omits_finite:  Optional[bool] = None
    # True:  f omits at least one finite value w0  -> T-arm fires
    # False: f has dense range / entire image      -> F-arm fires
    # None:  undetermined (essential singularity)  -> both arms fire (B-state)
    omitted_value: Optional[complex] = None   # the specific omitted value if known
    is_essential:  bool = False               # essential singularity behavior


@dataclass
class Arm:
    label:       str            # 'T' or 'F'
    active:      bool
    bound:       Optional[float]  # LANDAU_L if T-arm, None if F-arm
    description: str


def status_name(s: int) -> str:
    return {
        VOID:      'VOID(N)',
        BOUNDED:   'BOUNDED(T)',
        UNBOUNDED: 'UNBOUNDED(F)',
        PICARD:    'PICARD(B)',
    }.get(s, f'???({s})')
