"""
state.py — Erdos-Straus decomposition automaton data layer.

Egyptian fraction decomposition of 4/n.

STATUS register (2-bit Belnap FOUR):
  0b00  N  — uninitialized
  0b01  T  — decomposition found (success; theorem guarantees this for all n >= 2)
  0b10  F  — failure (theorem predicts: never occurs for n >= 2)
  0b11  B  — multiple decompositions coexist (always true for n >= 2)
"""
from fractions import Fraction

VOID     = 0b00   # N
FOUND    = 0b01   # T
FAILED   = 0b10   # F
MULTIPLE = 0b11   # B

state = {
    'n':         None,
    'remainder': None,
    'terms':     [],
    'status':    VOID,
    'branch':    None,    # n % 4
    'history':   [],
}


def status_name(s: int) -> str:
    return {
        VOID:     'VOID(N)',
        FOUND:    'FOUND(T)',
        FAILED:   'FAILED(F)',
        MULTIPLE: 'MULTIPLE(B)',
    }.get(s, f'???({s})')


def frac_str(f: Fraction) -> str:
    if f == 0:
        return '0'
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"
