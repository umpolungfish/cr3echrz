"""
state.py — Goldbach decomposition automaton data layer.

Prime-pair representation of even integers.

STATUS register (2-bit Belnap FOUR):
  0b00  N  — uninitialized (no n examined)
  0b01  T  — FOUND: at least one prime pair p+q=n confirmed
  0b10  F  — COUNTER: no prime pair exists (conjecture fails — never fires)
  0b11  B  — MULTIPLE: more than one prime pair coexists (paradice)
"""

VOID     = 0b00   # N
FOUND    = 0b01   # T
COUNTER  = 0b10   # F  (never activated if conjecture holds)
MULTIPLE = 0b11   # B

# Permanent record (accumulates across cases)
verified: dict = {}   # n -> list of (p, q) pairs
chain:    list = []   # ordered sequence of processed n values

# Per-case state (reset each run)
state = {
    'n':       None,
    'pairs':   [],
    'status':  VOID,
    'history': [],
}


def status_name(s: int) -> str:
    return {
        VOID:     'VOID(N)',
        FOUND:    'FOUND(T)',
        COUNTER:  'COUNTER(F)',
        MULTIPLE: 'MULTIPLE(B)',
    }.get(s, f'???({s})')
