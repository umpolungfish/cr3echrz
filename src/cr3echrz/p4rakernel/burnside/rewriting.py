"""
rewriting.py — Word rewriting system for the free Burnside group B(m,n).

Three layers:
  1. Free reduction:     cancel adjacent inverse pairs g·g⁻¹ → e
  2. Burnside reduction: cancel n-th power subwords w^n → e
  3. Primitive root:     find shortest u s.t. w = u^k
"""
from typing import Tuple


Word = Tuple[int, ...]


def free_reduce(w: Word) -> Word:
    """
    Cancel all adjacent inverse pairs.  A single pass with a stack
    is sufficient because cancellation can only expose new pairs to
    the left (already on the stack).
    """
    stack = []
    for g in w:
        if stack and stack[-1] == -g:
            stack.pop()
        else:
            stack.append(g)
    return tuple(stack)


def _find_nth_power(w: Word, n: int):
    """
    Find the first occurrence of a subword block^n (any block length ≥ 1).
    Returns (start, end) of the matched range, or None.
    Scan: for each start i and block length l, check w[i:i+n*l] = block^n.
    """
    L = len(w)
    for i in range(L):
        max_l = (L - i) // n
        for l in range(1, max_l + 1):
            block = w[i:i + l]
            if all(w[i + k*l : i + (k+1)*l] == block for k in range(n)):
                return i, i + n * l
    return None


def burnside_reduce(w: Word, n: int) -> Word:
    """
    Reduce a word in B(m,n) = F_m / ⟨x^n : x ∈ F_m⟩.

    Algorithm (confluent for free part; heuristic for power part):
      Alternate between free reduction and removal of the first
      detected n-th-power subword, until no further reduction applies.

    Complexity: O(|w|³) per reduction step.  Correct and terminating
    because every reduction strictly shortens the word.
    """
    while True:
        w2 = free_reduce(w)
        if w2 != w:
            w = w2
            continue
        hit = _find_nth_power(w, n)
        if hit is None:
            break
        start, end = hit
        w = w[:start] + w[end:]   # remove block^n
    return w


def primitive_root(w: Word) -> Word:
    """
    Find the shortest primitive word u such that w = u^k for some k ≥ 1.
    A word is primitive if it is not a proper power of a shorter word.
    """
    n = len(w)
    for l in range(1, n + 1):
        if n % l == 0:
            u = w[:l]
            if u * (n // l) == w:
                return u
    return w   # unreachable for non-empty w, but safe fallback


def period_at(w: Word, i: int):
    """
    Find the shortest period p starting at position i of word w.
    Returns p (int) if w[i:i+2p] has period p, else None.
    """
    remaining = len(w) - i
    for p in range(1, remaining // 2 + 1):
        block = w[i : i + p]
        if w[i + p : i + 2*p] == block:
            return p
    return None


def maximal_periodic_run(w: Word, i: int, p: int) -> int:
    """
    Given period p starting at i, return the index j > i where
    the run of period-p blocks ends.
    """
    block = w[i : i + p]
    j = i
    while j + p <= len(w) and w[j : j + p] == block:
        j += p
    return j
