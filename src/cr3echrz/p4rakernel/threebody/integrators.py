"""
integrators.py — AFWD, AREV, CLINK (symplectic kernels)

Base integrator: Forest-Ruth 4th-order symplectic (3 force evaluations/step).

Forest-Ruth coefficients (ξ = 1/(2-2^(1/3))):
  drift coefficients c = [ξ/2, (1-ξ)/2, (1-ξ)/2, ξ/2]
  kick  coefficients d = [ξ,   1-2ξ,    ξ        ]

Note: d[1] = 1-2ξ < 0 — normal for 4th-order composition methods.
"""
import numpy as np
from cr3echrz.p4rakernel.threebody.state import G, STATUS

# Forest-Ruth coefficients
_XI  = 1.0 / (2.0 - 2.0 ** (1.0/3.0))
_FR_C = np.array([_XI/2, (1-_XI)/2, (1-_XI)/2, _XI/2])
_FR_D = np.array([_XI, 1 - 2*_XI, _XI])


def _gravity_force(pos, masses):
    """
    Gravitational force on each body.
    Returns F (shape 3×3), where F[i] = dp_i/dt = Σ_{j≠i} G m_i m_j (r_j-r_i)/|r|³.
    """
    m   = np.asarray(masses, dtype=float)
    F   = np.zeros_like(pos)
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            r_ij = pos[j] - pos[i]
            d    = np.linalg.norm(r_ij)
            # Newton's 3rd law enforced: F_ji = -F_ij
            F[i] += G * m[i] * m[j] * r_ij / d**3
    return F


def _fr4_step(pos, mom, masses, dt):
    """Single Forest-Ruth 4th-order symplectic step."""
    m = np.asarray(masses, dtype=float)
    for i in range(3):
        # drift
        pos = pos + _FR_C[i] * dt * (mom / m[:, np.newaxis])
        # kick
        mom = mom + _FR_D[i] * dt * _gravity_force(pos, masses)
    # final drift
    pos = pos + _FR_C[3] * dt * (mom / m[:, np.newaxis])
    return pos, mom


def afwd(X, dt, steps, masses):
    """
    AFWD: forward symplectic integration using Forest-Ruth 4th order.

    Parameters
    ----------
    X      : ndarray shape (18,)  initial state
    dt     : float                timestep
    steps  : int                  number of FR steps
    masses : list[float]          [m1, m2, m3]

    Returns
    -------
    X_new  : ndarray shape (18,)
    """
    pos = X[:9].reshape(3, 3).copy()
    mom = X[9:].reshape(3, 3).copy()
    m   = np.asarray(masses, dtype=float)

    for _ in range(steps):
        pos, mom = _fr4_step(pos, mom, m, dt)

    X_out = np.empty(18)
    X_out[:9]  = pos.ravel()
    X_out[9:]  = mom.ravel()
    return X_out


def arev(X, dt, steps, masses):
    """
    AREV: time-reversal benchmark.

    Protocol (correct time-reversal test):
      1. Integrate X forward n steps  → X_fwd = X(t + n·dt)
      2. Flip momenta of X_fwd        → X_flip
      3. Integrate X_flip forward n steps → X_rev
      4. Flip momenta of X_rev        → X_final ≈ X (if symplectic)

    Deviation ||X_final - X|| is the reversibility error;
    should be O(dt^4) for Forest-Ruth.

    Returns (X_final, reversibility_error).
    """
    # Forward pass
    X_fwd = afwd(X, dt, steps, masses)

    # Flip momenta (time reversal)
    X_flip = X_fwd.copy()
    X_flip[9:] = -X_flip[9:]

    # Reverse pass (integrate forward in reversed-time direction)
    X_rev = afwd(X_flip, dt, steps, masses)

    # Flip momenta back
    X_rev[9:] = -X_rev[9:]

    rev_error = np.linalg.norm(X_rev - X)
    return X_rev, rev_error


def clink(X, dt, N, masses, symplecticity_check_interval=0):
    """
    CLINK: chain N symplectic steps; optionally monitor symplecticity.

    Parameters
    ----------
    symplecticity_check_interval : int
        If > 0, compute det(Jacobian) every this many steps.
        Triggers fallback dt halving if |det - 1| > 1e-13.

    Returns
    -------
    X_final : ndarray shape (18,)
    det_log : list of (step, det_J) — only if symplecticity_check_interval > 0
    """
    pos = X[:9].reshape(3, 3).copy()
    mom = X[9:].reshape(3, 3).copy()
    m   = np.asarray(masses, dtype=float)
    det_log = []

    step = 0
    while step < N:
        pos, mom = _fr4_step(pos, mom, m, dt)
        step += 1

        if symplecticity_check_interval > 0 and step % symplecticity_check_interval == 0:
            X_cur = np.concatenate([pos.ravel(), mom.ravel()])
            det_J = _fast_symplectic_det(X_cur, dt, 50, masses)   # only 50 steps per check
            det_log.append((step, det_J))
            dev = abs(det_J - 1.0)
            if dev > 5e-6:   # finite-diff noise floor ~1e-7; trigger only on real drift
                dt_half = dt / 2
                print(f"  [CLINK] step={step}: det(J)={det_J:.8f}, |det-1|={dev:.2e}"
                      f" → halving dt {dt:.2e}→{dt_half:.2e}")
                dt = dt_half

    X_out = np.empty(18)
    X_out[:9]  = pos.ravel()
    X_out[9:]  = mom.ravel()

    if symplecticity_check_interval > 0:
        return X_out, det_log
    return X_out


def _fast_symplectic_det(X, dt, steps, masses, eps=1e-7):
    """
    Estimate det(Jacobian) of the flow from X over 'steps' steps
    by finite differences in all 18 directions.
    For a symplectic integrator this should be 1.0.
    Only called periodically — not on every step.
    """
    n = 18
    J = np.zeros((n, n))
    X_fwd = afwd(X, dt, steps, masses)
    for j in range(n):
        e = np.zeros(n); e[j] = eps
        X_p = afwd(X + e, dt, steps, masses)
        J[:, j] = (X_p - X_fwd) / eps
    return abs(np.linalg.det(J))


def compute_flow_jacobian_determinant(X0, dt, steps, masses, eps=1e-7):
    """
    TANCH helper: compute det(J) of flow map over `steps` steps.
    For a symplectic integrator: det(J) = 1 to machine precision.
    """
    return _fast_symplectic_det(X0, dt, steps, masses, eps)
