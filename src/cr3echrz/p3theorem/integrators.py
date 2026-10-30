"""
integrators.py — AFWD, AREV, CLINK (theorem execution kernels)

AFWD  — forward morphism: advance the theorem state along its natural direction
AREV  — reverse morphism: time-reversal / backward step (benchmark)
CLINK — chain link: compose many steps; verify structural invariants along the way

Every theorem has its own AFWD step semantics:
  - Gravitational: Forest-Ruth 4th-order symplectic step
  - Collatz:       n → n/2 (even) or n → 3n+1 (odd)
  - Goldbach:      test a candidate partition of even n

Forest-Ruth coefficients (ξ = 1/(2-2^(1/3))):
  drift c = [ξ/2, (1-ξ)/2, (1-ξ)/2, ξ/2]
  kick  d = [ξ,   1-2ξ,    ξ        ]
"""
import numpy as np
from cr3echrz.p3theorem.state import TheoremState, G as GRAV


# ── Forest-Ruth coefficients ────────────────────────────────────────────────
_XI  = 1.0 / (2.0 - 2.0 ** (1.0/3.0))
_FR_C = np.array([_XI/2, (1-_XI)/2, (1-_XI)/2, _XI/2])
_FR_D = np.array([_XI, 1 - 2*_XI, _XI])


def _gravity_force(pos, masses):
    """Gravitational force on each body: dp_i/dt = Σ_{j≠i} G m_i m_j (r_j-r_i)/|r|³."""
    m = np.asarray(masses, dtype=float)
    n_bodies = len(m)
    F = np.zeros_like(pos)
    for i in range(n_bodies):
        for j in range(n_bodies):
            if i == j: continue
            r_ij = pos[j] - pos[i]
            d = np.linalg.norm(r_ij)
            F[i] += GRAV * m[i] * m[j] * r_ij / d**3
    return F


def _fr4_step(pos, mom, masses, dt):
    """Single Forest-Ruth 4th-order symplectic step."""
    m = np.asarray(masses, dtype=float)
    n_bodies = len(m)
    for i in range(3):
        pos = pos + _FR_C[i] * dt * (mom / m[:, np.newaxis])
        mom = mom + _FR_D[i] * dt * _gravity_force(pos, masses)
    pos = pos + _FR_C[3] * dt * (mom / m[:, np.newaxis])
    return pos, mom


# ════════════════════════════════════════════════════════════════
#  AFWD — Forward Morphism
# ════════════════════════════════════════════════════════════════

def afwd(state, dt, steps, masses=None):
    """
    AFWD: advance the theorem state forward by `steps` increments.

    Parameters
    ----------
    state  : TheoremState
    dt     : float — timestep (physics) or unit step size (number-theoretic)
    steps  : int
    masses : list[float] or None

    Returns
    -------
    TheoremState — advanced state
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        return _afwd_gravitational(state, dt, steps, masses)
    elif system == 'collatz':
        return _afwd_collatz(state, int(steps))
    elif system == 'goldbach':
        return _afwd_goldbach(state, int(steps))
    else:
        return _afwd_generic(state, dt, steps)


def _afwd_gravitational(state, dt, steps, masses):
    pos = state.X[:9].reshape(3, 3).copy()
    mom = state.X[9:].reshape(3, 3).copy()
    m = np.asarray(masses, dtype=float)

    for _ in range(steps):
        pos, mom = _fr4_step(pos, mom, m, dt)

    X_out = np.empty(18)
    X_out[:9] = pos.ravel()
    X_out[9:] = mom.ravel()

    new_state = state.copy()
    new_state.X = X_out
    return new_state


def _afwd_collatz(state, steps):
    n = int(state.X[0])
    traj = list(state.metadata.get('trajectory', [n]))
    for _ in range(steps):
        if n == 1:
            break
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        traj.append(n)
    new_state = state.copy()
    new_state.X = np.array([float(n)])
    new_state.metadata['trajectory'] = traj
    new_state.metadata['step_count'] = len(traj) - 1
    return new_state


def _afwd_goldbach(state, steps):
    even_n = int(state.X[0])
    primes = state.metadata.get('primes', [])
    partitions = list(state.metadata.get('partitions', []))

    for _ in range(steps):
        if len(partitions) >= 10:  # enough partitions found
            break
        for p in primes:
            if p > even_n // 2:
                break
            q = even_n - p
            if q in primes and (p, q) not in partitions and (q, p) not in partitions:
                partitions.append((p, q))
                break

    new_state = state.copy()
    new_state.metadata['partitions'] = partitions
    return new_state


def _afwd_generic(state, dt, steps):
    """Generic forward: identity (no-op). Override for specific theorems."""
    return state.copy()


# ════════════════════════════════════════════════════════════════
#  AREV — Reverse Morphism (Time-Reversal Benchmark)
# ════════════════════════════════════════════════════════════════

def arev(state, dt, steps, masses=None):
    """
    AREV: time-reversal benchmark.

    Protocol:
      1. Integrate forward n steps  → X_fwd
      2. Flip momenta / reverse      → X_flip
      3. Integrate X_flip forward n steps → X_rev
      4. Flip back / unreverse       → X_final ≈ X_original

    Returns (X_final, reversibility_error).
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        # Forward pass
        X_fwd = _afwd_gravitational(state, dt, steps, masses)
        # Time reversal: flip momenta
        X_flip = X_fwd.copy()
        X_flip.X[9:] = -X_flip.X[9:]
        # Reverse pass
        X_rev = _afwd_gravitational(X_flip, dt, steps, masses)
        X_rev.X[9:] = -X_rev.X[9:]
        rev_error = float(np.linalg.norm(X_rev.X - state.X))
        return X_rev, rev_error

    if system == 'collatz':
        # Collatz is irreversible forward (no backward step unless n is known to be reachable)
        # For benchmark, we integrate forward and verify n returns
        X_fwd = _afwd_collatz(state, steps)
        n_final = int(X_fwd.X[0])
        rev_error = 0.0 if n_final == 1 else 1.0  # converged if n=1
        return X_fwd, rev_error

    # Generic: just forward and return
    X_fwd = afwd(state, dt, steps, masses)
    return X_fwd, 0.0


# ════════════════════════════════════════════════════════════════
#  CLINK — Chain Link (Long-Term Integration)
# ════════════════════════════════════════════════════════════════

def clink(state, dt, N, masses=None, symplecticity_check_interval=0):
    """
    CLINK: chain N symplectic steps; optionally monitor structural invariants.

    Parameters
    ----------
    symplecticity_check_interval : int
        If > 0, compute det(J) every this many steps. Triggers dt halving
        if |det(J) - 1| exceeds threshold (physical systems only).

    Returns
    -------
    state_final : TheoremState
    det_log : list of (step, det_J) — only if symplecticity_check_interval > 0
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        return _clink_gravitational(state, dt, N, masses, symplecticity_check_interval)
    elif system == 'collatz':
        return _clink_collatz(state, N), []
    elif system == 'goldbach':
        return _clink_goldbach(state, N), []
    else:
        return _clink_generic(state, N), []


def _clink_gravitational(state, dt, N, masses, symplecticity_check_interval=0):
    pos = state.X[:9].reshape(3, 3).copy()
    mom = state.X[9:].reshape(3, 3).copy()
    m = np.asarray(masses, dtype=float)
    det_log = []

    step = 0
    while step < N:
        pos, mom = _fr4_step(pos, mom, m, dt)
        step += 1

        if symplecticity_check_interval > 0 and step % symplecticity_check_interval == 0:
            X_cur = np.concatenate([pos.ravel(), mom.ravel()])
            det_J = _fast_symplectic_det(X_cur, dt, 50, masses)
            det_log.append((step, det_J))
            if abs(det_J - 1.0) > 5e-6:
                dt = dt / 2
                print(f"  [CLINK] step={step}: det(J)={det_J:.8f}, |det-1|={abs(det_J-1):.2e}"
                      f" → halving dt {dt*2:.2e}→{dt:.2e}")

    X_out = np.empty(18)
    X_out[:9] = pos.ravel()
    X_out[9:] = mom.ravel()

    new_state = state.copy()
    new_state.X = X_out

    if symplecticity_check_interval > 0:
        return new_state, det_log
    return new_state, []


def _clink_collatz(state, N):
    n = int(state.X[0])
    traj = list(state.metadata.get('trajectory', [n]))
    for _ in range(N):
        if n == 1:
            break
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        traj.append(n)
    new_state = state.copy()
    new_state.X = np.array([float(n)])
    new_state.metadata['trajectory'] = traj
    new_state.metadata['step_count'] = len(traj) - 1
    return new_state


def _clink_goldbach(state, N):
    return _afwd_goldbach(state, N)


def _clink_generic(state, N):
    return state.copy()


# ════════════════════════════════════════════════════════════════
#  SYMPLECTIC / JACOBIAN UTILITIES
# ════════════════════════════════════════════════════════════════

def _fast_symplectic_det(X_vec, dt, steps, masses, eps=1e-7):
    """Estimate det(Jacobian) by finite differences in all 18 directions."""
    n = 18
    J = np.zeros((n, n))
    X_fwd = _afwd_gravitational_vec(X_vec, dt, steps, masses)
    for j in range(n):
        e = np.zeros(n); e[j] = eps
        X_p = _afwd_gravitational_vec(X_vec + e, dt, steps, masses)
        J[:, j] = (X_p - X_fwd) / eps
    return abs(np.linalg.det(J))


def _afwd_gravitational_vec(X, dt, steps, masses):
    """Gravitational AFWD on raw ndarray (for Jacobian estimation)."""
    pos = X[:9].reshape(3, 3).copy()
    mom = X[9:].reshape(3, 3).copy()
    m = np.asarray(masses, dtype=float)
    for _ in range(steps):
        pos, mom = _fr4_step(pos, mom, m, dt)
    return np.concatenate([pos.ravel(), mom.ravel()])


def compute_flow_jacobian_determinant(state, dt, steps, masses, eps=1e-7):
    """TANCH helper: det(J) of flow map over `steps`."""
    X0 = state.X if hasattr(state, 'X') else state
    return _fast_symplectic_det(X0, dt, steps, masses, eps)
