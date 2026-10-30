"""
opcodes.py — Goldbach decomposition opcode library.

FSPLIT / FFUSE Frobenius invariant:
    pairs = fsplit(n)                          # delta: n -> prime pairs
    ok    = ffuse(n, pairs[0])                 # mu:    pair -> n
    pairs[0][0] + pairs[0][1] == n             # mu o delta = id (exact)
The prime decomposition is lossless: summing any recorded pair recovers n.
"""
from math import isqrt
from typing import List, Tuple, Optional
from cr3echrz.p4rakernel.goldbach import state as st
from cr3echrz.p4rakernel.goldbach.state import VOID, FOUND, COUNTER, MULTIPLE


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True


def vinit(n: int) -> int:
    """VINIT: genesis — initialize per-case state for even n >= 4."""
    assert n >= 4 and n % 2 == 0
    st.state['n']      = n
    st.state['pairs']  = []
    st.state['status'] = VOID
    st.state['history'] = [('VINIT', n)]
    return n


def tanch(n: int) -> bool:
    """TANCH: verify boundary condition n >= 4 and n even."""
    ok = (n >= 4 and n % 2 == 0)
    assert ok
    st.state['history'].append(('TANCH', n))
    return ok


def fsplit(n: int) -> List[Tuple[int, int]]:
    """
    FSPLIT (delta): enumerate all prime pairs (p, q) with p+q=n, p<=q.

    This is the delta-decomposition of n over its prime-sum representations.
    FFUSE (mu) reconstitutes n from any recorded pair: mu o delta = id.
    """
    pairs = [(p, n - p)
             for p in range(2, n // 2 + 1)
             if is_prime(p) and is_prime(n - p)]
    st.state['pairs'] = pairs
    st.state['history'].append(('FSPLIT', pairs))
    return pairs


def evalt(pairs: List[Tuple[int, int]]) -> bool:
    """EVALT (T-arm): True iff at least one prime pair exists."""
    result = len(pairs) > 0
    st.state['history'].append(('EVALT', result))
    return result


def afwd(pairs: List[Tuple[int, int]]) -> Tuple[int, int]:
    """AFWD: canonical (lexicographically first) prime pair."""
    assert pairs
    pair = pairs[0]
    st.state['history'].append(('AFWD', pair))
    return pair


def ifix(n: int):
    """IFIX: permanently record all prime pairs for n in the global verified dict."""
    if n not in st.verified:
        st.verified[n] = []
    for p in st.state['pairs']:
        if p not in st.verified[n]:
            st.verified[n].append(p)
    st.state['history'].append(('IFIX', (n, list(st.state['pairs']))))


def ffuse(n: int, pair: Tuple[int, int]) -> bool:
    """
    FFUSE (mu): reconstitute n from prime pair.

    Frobenius identity: mu o delta = id.
    Verifies pair[0] + pair[1] == n exactly — prime decomposition is lossless.
    """
    ok = (pair[0] + pair[1] == n)
    assert ok, f"FFUSE INTEGRITY FAIL: {pair[0]}+{pair[1]} != {n}"
    st.state['history'].append(('FFUSE', ok))
    return ok


def evalf(pairs: List[Tuple[int, int]]) -> bool:
    """EVALF (F-arm): True iff no prime pair found — potential counterexample."""
    result = len(pairs) == 0
    st.state['history'].append(('EVALF', result))
    return result


def arev(n: int):
    """AREV: log failure — no prime pair for n. (Fires only if conjecture fails.)"""
    st.state['status'] = COUNTER
    st.state['history'].append(('AREV', n))


def clink(n: int):
    """CLINK: add n to the permanent chain of evidence."""
    if n not in st.chain:
        st.chain.append(n)
    st.state['history'].append(('CLINK', n))


def engagr(n: int, pairs: List[Tuple[int, int]]) -> int:
    """ENGAGR: engage Belnap STATUS — MULTIPLE(B) if >1 pair, FOUND(T) if exactly 1."""
    if len(pairs) > 1:
        new_status = MULTIPLE
    elif len(pairs) == 1:
        new_status = FOUND
    else:
        new_status = COUNTER
    st.state['status'] = new_status
    st.state['history'].append(('ENGAGR', new_status))
    return new_status


def ifix_final() -> int:
    """IFIX (final): confirm and return the permanently fixed STATUS."""
    final = st.state['status']
    st.state['history'].append(('IFIX_FINAL', final))
    return final


def tanch_final(n: int, pair: Tuple[int, int]) -> bool:
    """TANCH (final): boundary verification — pair sums to n."""
    ok = (pair[0] + pair[1] == n)
    assert ok
    st.state['history'].append(('TANCH_FINAL', ok))
    return ok


def imscrib(n: int, pair: Tuple[int, int]) -> bool:
    """IMSCRIB: self-recognition — n = p+q verified as a Goldbach instance."""
    ok = (pair[0] + pair[1] == n)
    assert ok, f"IMSCRIB FAIL: {pair[0]}+{pair[1]} != {n}"
    st.state['history'].append(('IMSCRIB', (n, pair)))
    return ok
