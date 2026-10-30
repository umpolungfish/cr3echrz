"""
opcodes.py — Erdos-Straus decomposition opcode library.

FSPLIT / FFUSE Frobenius invariant:
    After all IFIX calls, FFUSE verifies:
        sum(Fraction(1,d) for d in terms) == Fraction(4, n)
    i.e., the decomposition reconstructs 4/n exactly: mu o delta = id.
"""
from fractions import Fraction
from cr3echrz.p4rakernel.erdos_straus import state as st
from cr3echrz.p4rakernel.erdos_straus.state import VOID, FOUND, FAILED, MULTIPLE


def vinit(n: int) -> Fraction:
    """VINIT: genesis — initialize 4/n, STATUS=VOID."""
    assert n >= 2
    st.state['n']         = n
    st.state['remainder'] = Fraction(4, n)
    st.state['terms']     = []
    st.state['status']    = VOID
    st.state['branch']    = None
    st.state['history']   = [('VINIT', n)]
    return Fraction(4, n)


def tanch(n: int) -> bool:
    """TANCH: verify universal boundary n >= 2."""
    ok = (n >= 2)
    assert ok
    st.state['history'].append(('TANCH', n))
    return ok


def fsplit(n: int) -> int:
    """
    FSPLIT (delta): branch on n mod 4 — four congruence classes.
    This is the delta-decomposition splitting the integer tape into four arms.
    FFUSE (mu) reconstitutes by verifying sum of unit fractions = 4/n.
    """
    r = n % 4
    st.state['branch'] = r
    st.state['history'].append(('FSPLIT', r))
    return r


def afwd(r: int) -> int:
    """
    AFWD: select the first unit fraction denominator.
      r=0: single term 1/(n/4) suffices — 4/n = 1/(n//4).
      r=1,2,3: greedy first term x = ceil(n/4).
    Returns the denominator (does not commit to state).
    """
    n = st.state['n']
    denom = n // 4 if r == 0 else -(-n // 4)   # ceil(n/4)
    st.state['history'].append(('AFWD', denom))
    return denom


def ifix(denom: int):
    """IFIX: permanently record unit fraction 1/denom, update remainder."""
    st.state['terms'].append(denom)
    st.state['remainder'] -= Fraction(1, denom)
    st.state['history'].append(('IFIX', denom))


def evalt() -> bool:
    """EVALT (T-arm): True iff current remainder is exactly zero."""
    result = (st.state['remainder'] == 0)
    st.state['history'].append(('EVALT', result))
    return result


def arev() -> Fraction:
    """AREV: log and return current remainder (non-destructive checkpoint)."""
    rem = st.state['remainder']
    st.state['history'].append(('AREV', rem))
    return rem


def clink() -> Fraction:
    """CLINK: chain log — record current remainder state."""
    rem = st.state['remainder']
    st.state['history'].append(('CLINK', rem))
    return rem


def evalf() -> bool:
    """EVALF (F-arm): True iff remainder is still positive (decomposition incomplete)."""
    result = (st.state['remainder'] > 0)
    st.state['history'].append(('EVALF', result))
    return result


def greedy_step() -> int:
    """
    Select the largest unit fraction <= current remainder via greedy rule.
    For remainder p/q: x = ceil(q/p) = smallest integer s.t. 1/x <= p/q.
    Returns denominator (does not commit).
    """
    rem = st.state['remainder']
    assert rem > 0
    denom = -(-rem.denominator // rem.numerator)   # ceil(q/p)
    return denom


def ffuse() -> bool:
    """
    FFUSE (mu): reconstitute — verify sum of terms equals 4/n exactly.

    Frobenius identity: mu o delta = id.
    The decomposition is lossless: summing the Egyptian fractions recovers 4/n.
    """
    n = st.state['n']
    total = sum(Fraction(1, d) for d in st.state['terms'])
    ok = (total == Fraction(4, n))
    st.state['history'].append(('FFUSE', ok))
    return ok


def imscrib() -> bool:
    """IMSCRIB: self-recognition — assert decomposition complete (remainder=0)."""
    n = st.state['n']
    total = sum(Fraction(1, d) for d in st.state['terms'])
    ok = (total == Fraction(4, n)) and (st.state['remainder'] == 0)
    assert ok, (f"IMSCRIB FAIL: sum={total}, "
                f"expected={Fraction(4,n)}, remainder={st.state['remainder']}")
    st.state['history'].append(('IMSCRIB', ok))
    return ok


def engagr() -> int:
    """ENGAGR: acknowledge that multiple valid decompositions exist (Belnap B)."""
    st.state['status'] = MULTIPLE
    st.state['history'].append(('ENGAGR', MULTIPLE))
    return MULTIPLE


def ifix_final() -> int:
    """IFIX (final): permanently fix STATUS=FOUND — one valid decomposition confirmed."""
    st.state['status'] = FOUND
    st.state['history'].append(('IFIX_FINAL', list(st.state['terms'])))
    return FOUND


def tanch_final() -> bool:
    """TANCH (final): boundary verification — sum of terms = 4/n."""
    n = st.state['n']
    total = sum(Fraction(1, d) for d in st.state['terms'])
    ok = (total == Fraction(4, n))
    assert ok
    st.state['history'].append(('TANCH_FINAL', ok))
    return ok
