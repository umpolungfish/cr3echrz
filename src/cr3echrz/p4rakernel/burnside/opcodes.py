"""
opcodes.py — The Burnside automaton opcode library.

Each opcode is a pure function operating on word tuples.
Side effects (STATUS register updates) are applied to the shared
state dict imported from state.py.

FSPLIT / FFUSE invariant:
    ffuse(*fsplit(w)) == w   for all words w
"""
from typing import Tuple, List
from cr3echrz.p4rakernel.burnside.rewriting import (free_reduce, burnside_reduce,
                       primitive_root, period_at, maximal_periodic_run)
from cr3echrz.p4rakernel.burnside import state as st

Word = Tuple[int, ...]


# ═══════════════════════════════════════════════════════════════════
# §1  CORE WORD OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def vinit() -> Word:
    """VINIT: genesis — return empty word, set STATUS=VOID."""
    st.state['word']    = ()
    st.state['status']  = st.VOID
    st.state['history'] = [()]
    return ()


def afwd(w: Word, gen: int) -> Word:
    """AFWD: right-multiply by generator gen (positive int)."""
    assert gen > 0
    return w + (gen,)


def arev(w: Word, gen: int) -> Word:
    """AREV: right-multiply by inverse of generator gen."""
    assert gen > 0
    return w + (-gen,)


def clink(w1: Word, w2: Word) -> Word:
    """CLINK: free concatenation of two words."""
    return w1 + w2


def tanch(w: Word, n: int) -> Word:
    """
    TANCH: impose the Burnside relator x^n = 1.
    Returns the fully reduced form of w in B(m,n).
    Updates state['word'].
    """
    reduced = burnside_reduce(w, n)
    st.state['word'] = reduced
    st.state['history'].append(reduced)
    return reduced


# ═══════════════════════════════════════════════════════════════════
# §2  ADIAN DECOMPOSITION  (δ / μ  pair)
# ═══════════════════════════════════════════════════════════════════

def fsplit(w: Word):
    """
    FSPLIT (δ): Adian decomposition of w into alternating
    non-periodic bridges and maximal periodic runs.

    Structure produced:
        bridges[0]  periodics[0]  bridges[1]  periodics[1]  …  bridges[-1]
    so len(bridges) == len(periodics) + 1 always.

    Scans left-to-right; at each position attempts to find the shortest
    period p ≥ 1 such that the word starting there repeats block^2.
    If found, extracts the maximal run of that block.
    """
    bridges:   List[Word] = []
    periodics: List[Word] = []
    current_bridge: Word = ()
    i = 0

    while i < len(w):
        p = period_at(w, i)
        if p is None:
            current_bridge += (w[i],)
            i += 1
        else:
            j = maximal_periodic_run(w, i, p)
            bridges.append(current_bridge)
            periodics.append(w[i:j])
            current_bridge = ()
            i = j

    bridges.append(current_bridge)   # final bridge (may be empty)
    return periodics, bridges


def ffuse(periodics: List[Word], bridges: List[Word]) -> Word:
    """
    FFUSE (μ): reconstruct word from Adian components.

    Invariant: ffuse(*fsplit(w)) == w.
    Interleaves bridges and periodics in the canonical order
    B[0] P[0] B[1] P[1] … B[-1].
    """
    result: Word = ()
    for i, b in enumerate(bridges):
        result += b
        if i < len(periodics):
            result += periodics[i]
    return result


# ═══════════════════════════════════════════════════════════════════
# §3  ARMS:  EVALT (T-arm)  /  EVALF (F-arm)
# ═══════════════════════════════════════════════════════════════════

def evalt(periodics: List[Word], n: int) -> bool:
    """
    EVALT (T-arm): verify local finiteness of all periodic segments.

    For each periodic run, extract its primitive root u.
    In B(m,n) every element satisfies x^n = e, so u^n must reduce
    to identity.  Returns True iff all periodic segments satisfy this
    (confirming they contribute only finite-order elements).
    """
    for seg in periodics:
        u = primitive_root(seg)
        if burnside_reduce(u * n, n) != ():
            return False
    return True   # vacuously True for empty periodics list


def evalf(bridges: List[Word], n: int) -> bool:
    """
    EVALF (F-arm): detect aperiodic residuals in bridges.

    A bridge is an aperiodic residual if:
      1. It is non-empty.
      2. It itself contains no internal periodic structure (period_at
         returns None for every starting position).
      3. It does not reduce to identity under Burnside reduction
         (it is genuinely non-trivial in B(m,n)).

    Returns True if any bridge qualifies — indicating a potential
    obstruction to global finiteness (Adian-type aperiodic element).
    """
    for b in bridges:
        if not b:
            continue
        b_red = burnside_reduce(b, n)
        if not b_red:
            continue                          # trivial — not a residual
        # Check internal periodicity: a purely aperiodic word has no period
        internally_aperiodic = all(
            period_at(b_red, i) is None for i in range(len(b_red))
        )
        if internally_aperiodic:
            return True
    return False


# ═══════════════════════════════════════════════════════════════════
# §4  IDENTITY CHECK
# ═══════════════════════════════════════════════════════════════════

def imscrib(w: Word, n: int) -> bool:
    """
    IMSCRIB: self-recognition of the identity element.
    Returns True iff w reduces to the empty word in B(m,n).
    """
    return burnside_reduce(w, n) == ()


# ═══════════════════════════════════════════════════════════════════
# §5  REGIME CLASSIFIERS
# ═══════════════════════════════════════════════════════════════════

def engagr(n: int) -> int:
    """
    ENGAGR: engage the paradox register for exponent n.
    Updates and returns st.state['status'].
    """
    new_status = st.classify_exponent(n)
    st.state['status'] |= new_status   # OR-accumulate before IFIX override
    return new_status


def ifix(n: int) -> int:
    """
    IFIX: permanent fixation — consult Novikov-Adian published results.
    Overrides status with the definitive known value.
    Updates and returns st.state['status'].
    """
    fixed = st.classify_exponent(n)
    st.state['status'] = fixed
    return fixed
