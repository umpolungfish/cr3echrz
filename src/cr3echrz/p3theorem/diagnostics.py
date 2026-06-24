"""
diagnostics.py — EVALT, EVALF, ENGAGR, IFIX

The theorem diagnostic suite:

  EVALT  — Evaluate-True:  verify theorem holds (quasi-periodic, prime, finite...)
  EVALF  — Evaluate-False: measure failure (chaotic, composite, infinite...)
  ENGAGR — Engage Paradox:  push to the KAM/dialetheic boundary
  IFIX   — Irreversible Fix: permanent record (Poincaré section, trajectory log)

Every theorem has its own semantic mapping:
  - Gravitational: EVALT = rotation number, EVALF = FLI, IFIX = Poincaré section
  - Collatz:       EVALT = n→1 convergence, EVALF = divergence counter
  - Goldbach:      EVALT = partition found, EVALF = counterexample search
"""
import numpy as np
from cr3echrz.p3theorem.integrators import _fr4_step, _gravity_force, afwd
from cr3echrz.p3theorem import state as st


# ════════════════════════════════════════════════════════════════
#  EVALT — Evaluate-True
# ════════════════════════════════════════════════════════════════

def evalt(state, masses=None, dt=0.01, n_steps=1000):
    """
    EVALT: test whether the theorem holds (true arm).

    Physics: rotation-number quasi-periodicity test
    Collatz: check if n converges to 1
    Goldbach: verify partition exists
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        return _evalt_rotation(state, masses, dt, n_steps)
    elif system == 'collatz':
        return _evalt_collatz(state)
    elif system == 'goldbach':
        return _evalt_goldbach(state)
    else:
        return True


def _evalt_rotation(state, masses, dt, n_steps):
    """Rotation-number test: is the trajectory quasi-periodic?"""
    pos = state.X[:9].reshape(3, 3).copy()
    mom = state.X[9:].reshape(3, 3).copy()
    m = np.asarray(masses, dtype=float)

    angles = []
    prev_theta = None

    for _ in range(n_steps):
        pos, mom = _fr4_step(pos, mom, m, dt)
        rel = pos[1] - pos[0]
        theta = np.arctan2(rel[1], rel[0])
        if prev_theta is not None:
            angles.append(theta)
        prev_theta = theta

    if len(angles) < 2:
        return True

    angles_uw = np.unwrap(angles)
    t = np.linspace(0, 1, len(angles_uw))
    linear_fit = np.polyfit(t, angles_uw, 1)
    residuals = angles_uw - np.polyval(linear_fit, t)
    variance = np.var(residuals)

    return variance < 0.1


def _evalt_collatz(state):
    """Collatz: theorem holds if n converges to 1."""
    n = int(state.X[0])
    return n == 1


def _evalt_goldbach(state):
    """Goldbach: theorem holds if at least one partition found."""
    partitions = state.metadata.get('partitions', [])
    return len(partitions) > 0


# ════════════════════════════════════════════════════════════════
#  EVALF — Evaluate-False
# ════════════════════════════════════════════════════════════════

def evalf(state, dt=None, masses=None, n_steps=500):
    """
    EVALF: measure failure or chaos in the system.

    Physics: Fast Lyapunov Indicator (FLI)
    Collatz: check for divergence / unbounded growth
    Goldbach: count failed partition attempts
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        return _evalf_fli(state, dt, masses, n_steps)
    elif system == 'collatz':
        return _evalf_collatz(state)
    elif system == 'goldbach':
        return _evalf_goldbach(state)
    else:
        return 0.0


def _evalf_fli(state, dt, masses, n_steps):
    """Fast Lyapunov Indicator via shadow-trajectory method."""
    m = np.asarray(masses, dtype=float)
    eps = 1e-9

    pos = state.X[:9].reshape(3, 3).copy()
    mom = state.X[9:].reshape(3, 3).copy()

    rng = np.random.default_rng(42)
    w = rng.standard_normal(18)
    w /= np.linalg.norm(w)

    pos_s = pos + eps * w[:9].reshape(3, 3)
    mom_s = mom + eps * w[9:].reshape(3, 3)

    fli_sum = 0.0

    for _ in range(n_steps):
        pos,   mom   = _fr4_step(pos,   mom,   m, dt)
        pos_s, mom_s = _fr4_step(pos_s, mom_s, m, dt)

        delta = np.concatenate([(pos_s - pos).ravel(), (mom_s - mom).ravel()])
        d_norm = np.linalg.norm(delta)
        if d_norm == 0:
            continue
        fli_sum += np.log(d_norm / eps)

        delta /= d_norm
        pos_s = pos + eps * delta[:9].reshape(3, 3)
        mom_s = mom + eps * delta[9:].reshape(3, 3)

    return fli_sum / (n_steps * dt)


def _evalf_collatz(state):
    """Collatz false branch: measure divergence — maximum value reached."""
    traj = state.metadata.get('trajectory', [int(state.X[0])])
    return float(max(traj))  # larger = more divergent


def _evalf_goldbach(state):
    """Goldbach false branch: count failed attempts."""
    even_n = int(state.X[0])
    partitions = state.metadata.get('partitions', [])
    return max(0, even_n // 2 - len(partitions))  # remaining candidates


# ════════════════════════════════════════════════════════════════
#  ENGAGR — Engage Paradox
# ════════════════════════════════════════════════════════════════

def engagr(state, masses=None, target_fli_fraction=0.4, max_iter=15, dt=0.01, n_steps=200,
           target_heuristic=None):
    """
    ENGAGR: perturb the system to the KAM boundary / dialetheic edge.

    Physics: binary search on velocity scale to reach target FLI
    Collatz: search for a starting value near the boundary of convergence
    Goldbach: search for a near-counterexample candidate
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        return _engagr_gravitational(state, masses, target_fli_fraction, max_iter, dt, n_steps)
    elif system == 'collatz':
        return _engagr_collatz(state, max_iter)
    elif system == 'goldbach':
        return _engagr_goldbach(state, max_iter)
    else:
        st.STATUS = 0b11
        return state.copy()


def _engagr_gravitational(state, masses, target_fli_fraction, max_iter, dt, n_steps):
    from transforms import fsplit, ffuse

    X_kick = state.copy()
    X_kick.X[17] += 0.08  # pz3 kick

    target = target_fli_fraction * 5.0

    arm_T, arm_F = fsplit(X_kick, masses)

    lo, hi = 1.0, 1.15
    X_best = X_kick.copy()
    best_err = float('inf')

    for _ in range(max_iter):
        scale = (lo + hi) / 2.0
        X_rel_scaled = arm_F.copy()
        X_rel_scaled.X[6:] *= scale
        X_try = ffuse(arm_T, X_rel_scaled, masses)
        fli = _evalf_fli(X_try, dt, masses, n_steps)

        err = abs(fli - target)
        if err < best_err:
            best_err = err
            X_best = X_try.copy()

        if fli < target:
            lo = scale
        else:
            hi = scale

        if best_err < 0.1:
            break

    st.STATUS = 0b11
    return X_best


def _engagr_collatz(state, max_iter):
    """Search for Collatz starting point near convergence boundary."""
    n0 = int(state.X[0])
    best_n = n0
    best_steps = 0

    for offset in range(-max_iter//2, max_iter//2):
        candidate = n0 + offset
        if candidate <= 1:
            continue
        test_state = st.collatz_ic(candidate)
        test_state = afwd(test_state, 1, 200)
        steps = test_state.metadata.get('step_count', 0)
        if steps > best_steps:
            best_steps = steps
            best_n = candidate

    st.STATUS = 0b11
    new_state = st.collatz_ic(best_n)
    return new_state


def _engagr_goldbach(state, max_iter):
    """Search for even number with few partitions (near-Goldbach boundary)."""
    even_n = int(state.X[0])
    best_n = even_n
    fewest = float('inf')

    for offset in range(0, max_iter * 2, 2):
        candidate = even_n + offset
        if candidate <= 2:
            continue
        primes = st._sieve_eratosthenes(candidate)
        count = 0
        for p in primes:
            if p > candidate // 2:
                break
            if (candidate - p) in primes:
                count += 1
        if count < fewest and count > 0:
            fewest = count
            best_n = candidate

    st.STATUS = 0b11
    return st.goldbach_ic(best_n)


# ════════════════════════════════════════════════════════════════
#  IFIX — Irreversible Fix (Poincaré Section / Trajectory Log)
# ════════════════════════════════════════════════════════════════

def ifix(state, dt=None, masses=None, n_crossings=80):
    """
    IFIX: record permanent trajectory markers.

    Physics: Poincaré section — (y3, py3) at z3=0 upward crossings
    Collatz: trajectory log of (n, step)
    Goldbach: partition log
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        return _ifix_poincare(state, dt, masses, n_crossings)
    elif system == 'collatz':
        return _ifix_collatz_trajectory(state)
    elif system == 'goldbach':
        return _ifix_goldbach_partitions(state)
    else:
        return np.array([])


def _ifix_poincare(state, dt, masses, n_crossings):
    """Poincaré section: y3=0, ẏ3>0 upward crossings."""
    m = np.asarray(masses, dtype=float)
    pos = state.X[:9].reshape(3, 3).copy()
    mom = state.X[9:].reshape(3, 3).copy()

    sections = []
    max_steps = n_crossings * 10000
    step_cnt = 0

    y_prev = pos[2, 1]

    while len(sections) < n_crossings and step_cnt < max_steps:
        pos_new, mom_new = _fr4_step(pos, mom, m, dt)
        step_cnt += 1
        y_cur = pos_new[2, 1]

        if y_prev < 0.0 < y_cur:
            f = y_prev / (y_prev - y_cur)
            x3 = pos[2, 0] + f * (pos_new[2, 0] - pos[2, 0])
            px3 = mom[2, 0] + f * (mom_new[2, 0] - mom[2, 0])
            sections.append([x3, px3])

        y_prev = y_cur
        pos, mom = pos_new, mom_new

    return np.array(sections)


def _ifix_collatz_trajectory(state):
    """Collatz trajectory log as (step, n) pairs."""
    traj = state.metadata.get('trajectory', [])
    return np.array([[i, n] for i, n in enumerate(traj)])


def _ifix_goldbach_partitions(state):
    """Goldbach partition log."""
    parts = state.metadata.get('partitions', [])
    return np.array(parts) if parts else np.array([])
