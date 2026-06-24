"""
state.py — VINIT, IMSCRIB, Belnap status register, and theorem initial conditions

Every theorem operationalization shares the same state architecture:
  - STATUS register: 2-bit Belnap FOUR (0b00 void | 0b01 true | 0b10 false | 0b11 paradox)
  - VINIT: initialise void state
  - IMSCRIB: compute and record the theorem's conserved quantities (the "invariants")

The state vector X is theorem-specific:
  - Gravitational N-body: positions + momenta  (shape determined by n_bodies)
  - Collatz:            (n, trajectory, steps)
  - Goldbach:           (even_number, partition_candidates)
  - ... etc
"""
import numpy as np
import sys as _sys, os as _os
from cr3echrz.shared import BelnapRegister, FrobeniusVerifier
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional

# ════════════════════════════════════════════════════════════════
#  BELNAP FOUR STATUS REGISTER
# ════════════════════════════════════════════════════════════════

STATUS = 0b00   # 0b00 void | 0b01 true/integrable | 0b10 false/chaotic | 0b11 paradox/KAM


def vinit():
    """
    VINIT: initialise void state.
    Returns an empty container state; STATUS = 0b00.
    The returned object is theorem-specific — callers should use
    the theorem-specific initial-condition functions to populate it.
    """
    global STATUS
    STATUS = 0b00
    return TheoremState()


def imscrib(state, masses=None, invariants=None):
    """
    IMSCRIB: inject structural data; compute conserved quantities.
    Sets STATUS = 0b01 (true / integrable mode).

    Parameters
    ----------
    state : TheoremState or ndarray
        The theorem state object.
    masses : list[float] or None
        For gravitational / physical systems: body masses.
    invariants : dict or None
        For number-theoretic systems: pre-computed invariants to record.

    Returns
    -------
    state, conserved : tuple
        `conserved` is a dict of {name: value} invariant quantities.
    """
    global STATUS
    STATUS = 0b01
    if invariants is not None:
        state.invariants.update(invariants)
        return state, invariants
    if masses is not None:
        # Physical system: compute E, L
        conserved = _compute_conserved_physical(state, masses)
        state.invariants.update(conserved)
        return state, conserved
    return state, {}


def _compute_conserved_physical(state, masses):
    """Compute total energy E and angular momentum L for N-body system."""
    m = np.asarray(masses, dtype=float)
    n_bodies = len(m)
    pos = state.X[:3*n_bodies].reshape(n_bodies, 3)
    mom = state.X[3*n_bodies:].reshape(n_bodies, 3)
    G = 1.0

    # Kinetic
    T = sum(0.5 * np.dot(mom[i], mom[i]) / m[i] for i in range(n_bodies))
    # Potential
    V = 0.0
    for i in range(n_bodies):
        for j in range(i+1, n_bodies):
            r_ij = np.linalg.norm(pos[j] - pos[i])
            if r_ij > 1e-14:
                V -= G * m[i] * m[j] / r_ij
    E = T + V
    L = sum(np.cross(pos[i], mom[i]) for i in range(n_bodies))
    return {'E_total': float(E), 'L_vector': L}


def compute_conserved(state, masses=None):
    """Recompute conserved quantities from current state (no status change).
    For physical systems (masses provided): returns (E, L) tuple.
    For other systems: returns dict of invariants.
    """
    if masses is not None:
        conserved = _compute_conserved_physical(state, masses)
        E = conserved.get('E_total', 0.0)
        L = conserved.get('L_vector', 0.0)
        return E, L
    return state.invariants.copy()


# ════════════════════════════════════════════════════════════════
#  THEOREM STATE
# ════════════════════════════════════════════════════════════════

class TheoremState:
    """Generic container for any theorem's operationalization state."""
    def __init__(self, X=None, metadata=None):
        self.X = X if X is not None else np.zeros(0)
        self.metadata = metadata or {}
        self.invariants = {}
        self.history = []

    def copy(self):
        s = TheoremState(self.X.copy(), dict(self.metadata))
        s.invariants = dict(self.invariants)
        s.history = list(self.history)
        return s

    def __repr__(self):
        return f"TheoremState(shape={self.X.shape}, invariants={list(self.invariants.keys())})"


# ════════════════════════════════════════════════════════════════
#  THEOREM-SPECIFIC INITIAL CONDITIONS
# ════════════════════════════════════════════════════════════════

def figure8_ic():
    """Chenciner-Montgomery figure-8 initial conditions. 3-body, equal masses."""
    r1 = np.array([-0.97000436,  0.24308753, 0.0])
    r2 = np.array([ 0.0,         0.0,        0.0])
    r3 = np.array([ 0.97000436, -0.24308753, 0.0])

    v12 = np.array([0.93240737/2, 0.86473146/2, 0.0])
    v2  = np.array([-0.93240737, -0.86473146, 0.0])

    X = np.zeros(18)
    X[0:3], X[3:6], X[6:9]      = r1, r2, r3
    X[9:12], X[12:15], X[15:18] = v12, v2, v12
    state = TheoremState(X)
    state.metadata = {'n_bodies': 3, 'masses': [1.0, 1.25, 1.33],
                      'system': 'gravitational', 'ic': 'figure8'}
    return state


def pythagorean_ic():
    """Pythagorean three-body problem: m=[3,4,5], bodies start at rest."""
    r1 = np.array([1.0,  3.0, 0.0])
    r2 = np.array([-2.0, -1.0, 0.0])
    r3 = np.array([1.0, -1.0, 0.0])

    X = np.zeros(18)
    X[0:3], X[3:6], X[6:9] = r1, r2, r3
    state = TheoremState(X)
    state.metadata = {'n_bodies': 3, 'masses': [3.0, 4.0, 5.0],
                      'system': 'gravitational', 'ic': 'pythagorean'}
    return state


def collatz_ic(n=27):
    """Collatz conjecture: start with integer n. State is (n, trajectory, step_count)."""
    state = TheoremState(np.array([float(n)]))
    state.metadata = {'n_start': n, 'system': 'collatz',
                      'trajectory': [n], 'step_count': 0}
    return state


def goldbach_ic(even_n=100):
    """Goldbach conjecture: even n > 2. State tracks partition candidates."""
    primes = _sieve_eratosthenes(even_n)
    state = TheoremState(np.array([float(even_n)]))
    state.metadata = {'even_n': even_n, 'primes': primes,
                      'system': 'goldbach', 'partitions': []}
    return state


def _sieve_eratosthenes(n):
    """Sieve up to n; returns list of primes <= n."""
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            sieve[i*i:n+1:i] = [False] * len(sieve[i*i:n+1:i])
    return [i for i, is_p in enumerate(sieve) if is_p]

# Module-level constants
G = 1.0  # gravitational constant in natural units
