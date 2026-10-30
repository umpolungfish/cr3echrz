"""
state.py — Burnside automaton data layer and STATUS register.

Memory (word tape): a tuple of nonzero integers.
  positive k  → generator k
  negative k  → inverse of generator k
  ()          → identity e

STATUS register (2-bit Belnap FOUR):
  0b00  N  — void (uninitialised, no generators introduced)
  0b01  T  — finite mode  (B(m,n) is known finite: n ∈ {2,3,4,6})
  0b10  F  — infinite mode (B(m,n) is known infinite: odd n ≥ 665)
  0b11  B  — intermediate paradox (finiteness unresolved: e.g. n=5)
"""

# ── STATUS constants ────────────────────────────────────────────────────────
VOID     = 0b00   # N
FINITE   = 0b01   # T
INFINITE = 0b10   # F
PARADOX  = 0b11   # B

# Exponent classification (Burnside known results)
FINITE_EXPONENTS   = frozenset([2, 3, 4, 6])
INFINITE_THRESHOLD = 665          # Novikov-Adian 1968; odd n ≥ 665

# Global state (mutable dict — single engine instance)
state = {
    'word':    (),
    'm':       2,
    'n':       5,
    'status':  VOID,
    'history': [],
}


def classify_exponent(n: int) -> int:
    """
    Classify exponent n into a STATUS value using known Burnside results.

    n ∈ {2,3,4,6}        → FINITE    (Burnside, Sanov, Hall)
    odd n ≥ 665           → INFINITE  (Novikov-Adian)
    otherwise             → PARADOX   (open problem)
    """
    if n in FINITE_EXPONENTS:
        return FINITE
    if n % 2 == 1 and n >= INFINITE_THRESHOLD:
        return INFINITE
    return PARADOX


def status_name(s: int) -> str:
    return {VOID: 'VOID(N)', FINITE: 'FINITE(T)',
            INFINITE: 'INFINITE(F)', PARADOX: 'PARADOX(B)'}.get(s, f'???({s})')


def word_str(w: tuple) -> str:
    if not w:
        return 'e'
    parts = []
    for g in w:
        if g > 0:
            parts.append(f'a{g}')
        else:
            parts.append(f'a{-g}⁻¹')
    return '·'.join(parts)
