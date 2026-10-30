"""
diagnostics.py — EVALT, EVALF, ENGAGR, IFIX

EVALT  — rotation number; True if trajectory is quasi-periodic
EVALF  — Fast Lyapunov Indicator (FLI); chaos measure
ENGAGR — controlled perturbation to push into KAM boundary
IFIX   — Poincaré section (z3 = 0 crossings)
"""
import numpy as np
from cr3echrz.p4rakernel.threebody.integrators import afwd, _fr4_step, _gravity_force
from cr3echrz.p4rakernel.threebody import state as st


# ─── EVALT ─────────────────────────────────────────────────────────────────

def evalt(X, masses, dt=0.01, n_steps=2000):
    """
    EVALT: rotation-number test for quasi-periodicity.

    Integrates the trajectory and computes the mean angular velocity
    of the relative coordinate Q1 (the r2-r1 vector).  If the angle
    winds uniformly (variance of step-to-step angle < threshold), the
    arm is quasi-periodic → returns True.

    Heuristic: robust for the CM arm (always True) and the Kepler arm
    near periodic orbits.
    """
    pos = X[:9].reshape(3, 3).copy()
    mom = X[9:].reshape(3, 3).copy()
    m   = np.asarray(masses, dtype=float)

    angles = []
    prev_theta = None

    for _ in range(n_steps):
        pos, mom = _fr4_step(pos, mom, m, dt)
        # Track angle of r2 - r1 in the xy-plane
        rel = pos[1] - pos[0]
        theta = np.arctan2(rel[1], rel[0])
        if prev_theta is not None:
            angles.append(theta)
        prev_theta = theta

    if len(angles) < 2:
        return True

    # Unwrap to get a continuous angle
    angles_uw = np.unwrap(angles)
    # Rotation number = total angle / (2π * n_steps)
    rot_num = (angles_uw[-1] - angles_uw[0]) / (2 * np.pi * n_steps)

    # Check if the unwrapped angle is close to linear (quasi-periodic)
    t = np.linspace(0, 1, len(angles_uw))
    linear_fit = np.polyfit(t, angles_uw, 1)
    residuals  = angles_uw - np.polyval(linear_fit, t)
    variance   = np.var(residuals)

    return variance < 0.1   # threshold: quasi-periodic if small variance


# ─── EVALF ─────────────────────────────────────────────────────────────────

def evalf(X, dt, masses, n_steps=500):
    """
    EVALF: Fast Lyapunov Indicator.

    Integrates the variational equations (shadow-trajectory method):
      - Two nearby trajectories X and X + ε*w
      - After each step, measure ||δX||, log it, renormalise
    FLI = Σ log(||δX||/||δX_0||) / T

    Returns FLI value (float).  Threshold ~10 distinguishes chaotic
    from quasi-periodic over n_steps steps.
    """
    m    = np.asarray(masses, dtype=float)
    eps  = 1e-9

    pos  = X[:9].reshape(3, 3).copy()
    mom  = X[9:].reshape(3, 3).copy()

    # Random unit tangent
    rng  = np.random.default_rng(42)
    w    = rng.standard_normal(18)
    w   /= np.linalg.norm(w)

    pos_s = pos + eps * w[:9].reshape(3, 3)
    mom_s = mom + eps * w[9:].reshape(3, 3)

    fli_sum = 0.0

    for _ in range(n_steps):
        pos,   mom   = _fr4_step(pos,   mom,   m, dt)
        pos_s, mom_s = _fr4_step(pos_s, mom_s, m, dt)

        delta     = np.concatenate([(pos_s - pos).ravel(), (mom_s - mom).ravel()])
        d_norm    = np.linalg.norm(delta)
        if d_norm == 0:
            continue
        fli_sum  += np.log(d_norm / eps)

        # Renormalise shadow trajectory
        delta    /= d_norm
        pos_s     = pos  + eps * delta[:9].reshape(3, 3)
        mom_s     = mom  + eps * delta[9:].reshape(3, 3)

    return fli_sum / (n_steps * dt)


# ─── ENGAGR ────────────────────────────────────────────────────────────────

def engagr(X, masses, target_fli_fraction=0.3, max_iter=20, dt=0.01, n_steps=300):
    """
    ENGAGR: tune a velocity scale factor until FLI sits near the KAM
    stability boundary.

    Strategy:
      1. Add a small out-of-plane (z) kick to body 3 so the orbit
         leaves the xy-plane — this enables z=0 Poincaré sections.
      2. Binary search on a coupling scale (relative momenta) until
         FLI ≈ target_fli_fraction × 5.0.

    Sets STATUS = 0b11 (KAM mixed mode).
    Returns X_perturbed.
    """
    from cr3echrz.p4rakernel.threebody.transforms import fsplit, ffuse

    # Step 1: small out-of-plane kick (breaks planar symmetry)
    X_kick = X.copy()
    X_kick[17] += 0.08    # pz3 += 0.08 (≈6% of typical momentum magnitude)

    target = target_fli_fraction * 5.0   # ~1.5

    X_cm, X_rel = fsplit(X_kick, masses)

    # Step 2: binary search on relative momentum scale
    lo, hi   = 1.0, 1.15   # tight range — KAM boundary is near the orbit
    X_best   = X_kick.copy()
    best_err = float('inf')

    for _ in range(max_iter):
        scale = (lo + hi) / 2.0
        X_try = ffuse(X_cm, _scale_rel_mom(X_rel, scale), masses)
        fli   = evalf(X_try, dt, masses, n_steps)

        err = abs(fli - target)
        if err < best_err:
            best_err = err
            X_best   = X_try.copy()

        if fli < target:
            lo = scale
        else:
            hi = scale

        if best_err < 0.1:
            break

    st.STATUS = 0b11
    return X_best


def _scale_rel_mom(X_rel, scale):
    """Scale the relative momenta (P1, P2) in Jacobi X_rel by factor."""
    X_r = X_rel.copy()
    X_r[6:] *= scale
    return X_r


# ─── IFIX ──────────────────────────────────────────────────────────────────

def ifix(X, dt, masses, n_crossings=200):
    """
    IFIX: Poincaré section.

    Surface of section: y3 = 0, ẏ3 > 0 (upward crossings in y of body 3).
    This section is natural for the figure-8 and its perturbations because
    body 3 oscillates through y=0 on every orbit half-period.

    Records (x3, px3) at each crossing via linear interpolation.
    Returns ndarray shape (n_crossings, 2).
    """
    m = np.asarray(masses, dtype=float)
    pos = X[:9].reshape(3, 3).copy()
    mom = X[9:].reshape(3, 3).copy()

    sections  = []
    max_steps = n_crossings * 10000
    step_cnt  = 0

    y_prev = pos[2, 1]   # y-coordinate of body 3

    while len(sections) < n_crossings and step_cnt < max_steps:
        pos_new, mom_new = _fr4_step(pos, mom, m, dt)
        step_cnt += 1
        y_cur = pos_new[2, 1]

        # Upward crossing: y3 transitions from negative to positive
        if y_prev < 0.0 < y_cur:
            f   = y_prev / (y_prev - y_cur)
            x3  = pos[2, 0] + f * (pos_new[2, 0] - pos[2, 0])
            px3 = mom[2, 0] + f * (mom_new[2, 0] - mom[2, 0])
            sections.append([x3, px3])

        y_prev = y_cur
        pos, mom = pos_new, mom_new

    return np.array(sections)
