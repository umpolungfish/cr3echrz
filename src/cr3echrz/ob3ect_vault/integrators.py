#!/usr/bin/env python3
"""
integrators.py — AFWD, AREV, CLINK execution kernels for all ob3ect domains

  exec domains (mathematical, computational, physical):
    AFWD  → forward step (3n+1, time integration, register transition)
    AREV  → reverse step (n/2, time reversal, register unwind)
    CLINK → chain iteration (sequence iteration, long integration)

  symbolic domains (magical, divinatory, alchemical, ...):
    AFWD  → Belnap register forward transition (VOID→TRUE, TRUE→TRUE, FALSE→FALSE, BOTH→BOTH)
    AREV  → Belnap register reverse (unwind to prior state)
    CLINK → chain of register transitions with dialetheic tracking

Author: Lando⊗⊙perator
"""
import numpy as np
from typing import List, Tuple, Optional
from cr3echrz.ob3ect_vault import state as st
from cr3echrz.ob3ect_vault.state import Ob3ectState, VOID, TRUE, FALSE, BOTH, REG_NAMES


# ═══════════════════════════════════════════════════════════════════════
#  AFWD — Forward Morphism
# ═══════════════════════════════════════════════════════════════════════

def afwd(state: Ob3ectState, dt=1.0, n_steps=1, masses=None):
    """AFWD: forward morphism — advance state by n_steps."""
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')

    if cat == 'exec':
        return _afwd_exec(state, dt, n_steps, system, masses)
    else:
        return _afwd_symbolic(state, n_steps)


def _afwd_exec(state, dt, n_steps, system, masses=None):
    """Forward step for executable domains."""
    if system == 'mathematical':
        return _afwd_mathematical(state, n_steps)
    elif system == 'computational':
        return _afwd_computational(state, n_steps)
    elif system == 'physical' and masses is not None:
        return _afwd_physical(state, dt, n_steps, masses)
    else:
        return _afwd_generic(state, n_steps)


def _afwd_mathematical(state, n_steps):
    """Mathematical forward: apply operation n_steps times."""
    n = int(state.X[0])
    op_map = state.metadata.get('opcode_map', {})
    afwd_name = op_map.get('AFWD', '3n+1')

    traj = state.metadata.get('trajectory', [n])
    for _ in range(n_steps):
        if 'collatz' in afwd_name.lower() or '3n' in afwd_name:
            n = 3 * n + 1 if n % 2 == 1 else n // 2
        elif 'n+1' in afwd_name or 'successor' in afwd_name.lower():
            n = n + 1
        elif 'square' in afwd_name.lower():
            n = n * n
        elif 'double' in afwd_name.lower() or '2n' in afwd_name:
            n = n * 2
        elif 'goldbach' in afwd_name.lower() or 'partition' in afwd_name.lower():
            # Goldbach: search for prime partition of n
            primes = state.metadata.get('primes', [])
            for p in primes:
                if p <= n // 2 and (n - p) in primes:
                    state.metadata.setdefault('partitions', []).append((p, n - p))
            break
        else:
            # Default: n → n+1
            n = n + 1
        traj.append(n)

    state.X = np.array([float(n)])
    state.metadata['trajectory'] = traj
    state.metadata['step_count'] = state.metadata.get('step_count', 0) + n_steps
    return state


def _afwd_computational(state, n_steps):
    """Computational forward: register machine transition."""
    for _ in range(n_steps):
        if state.reg == VOID:
            state.reg = TRUE
        # TRUE/FALSE/BOTH remain stable
    return state


def _afwd_physical(state, dt, n_steps, masses):
    """Physical forward: symplectic integration (Forest-Ruth 4th order)."""
    m = np.asarray(masses, dtype=float)
    n_bodies = len(m)
    G = 1.0

    w = 1.0 / (2.0 - 2.0 ** (1.0/3.0))
    c = [w/2.0, (1.0-w)/2.0, (1.0-w)/2.0, w/2.0]
    d = [w, 1.0 - 2.0*w, w, 0.0]

    pos = state.X[:3*n_bodies].copy()
    mom = state.X[3*n_bodies:].copy()

    def accel(p):
        a = np.zeros_like(p)
        for i in range(n_bodies):
            for j in range(i+1, n_bodies):
                r_ij = p[j] - p[i]
                dist = np.linalg.norm(r_ij)
                if dist > 1e-14:
                    f = G * m[i] * m[j] * r_ij / (dist**3)
                    a[i] += f / m[i]
                    a[j] -= f / m[j]
        return a

    for _ in range(n_steps):
        for ci, di in zip(c, d):
            pos = pos + ci * dt * mom / m[:, None]
            a = accel(pos.reshape(n_bodies, 3))
            mom = mom + di * dt * a.flatten()

    state.X = np.concatenate([pos, mom])
    return state


def _afwd_generic(state, n_steps):
    """Generic forward: increment."""
    if len(state.X) > 0:
        state.X[0] += n_steps
    return state


def _afwd_symbolic(state, n_steps):
    """Symbolic forward: Belnap register transition."""
    for _ in range(n_steps):
        if state.reg == VOID:
            state.reg = TRUE
        # TRUE, FALSE, BOTH are fixed points under forward
        state.history.append(state.reg)
    return state


# ═══════════════════════════════════════════════════════════════════════
#  AREV — Reverse Morphism
# ═══════════════════════════════════════════════════════════════════════

def arev(state: Ob3ectState, dt=1.0, n_steps=1, masses=None) -> Tuple[Ob3ectState, float]:
    """AREV: reverse morphism + time-reversal error benchmark."""
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')

    if cat == 'exec':
        return _arev_exec(state, dt, n_steps, system, masses)
    else:
        return _arev_symbolic(state, n_steps)


def _arev_exec(state, dt, n_steps, system, masses=None):
    """Reverse step for executable domains."""
    if system == 'mathematical':
        return _arev_mathematical(state, n_steps)
    elif system == 'computational':
        return _arev_computational(state, n_steps)
    elif system == 'physical' and masses is not None:
        return _arev_physical(state, dt, n_steps, masses)
    else:
        return _arev_generic(state, n_steps)


def _arev_mathematical(state, n_steps):
    """Mathematical reverse: apply inverse operation."""
    n = int(state.X[0])
    op_map = state.metadata.get('opcode_map', {})
    arev_name = op_map.get('AREV', 'n/2')
    original_n = state.metadata.get('n_start', n)

    traj = state.metadata.get('trajectory', [n])
    for _ in range(n_steps):
        if 'n/2' in arev_name or 'collatz' in arev_name.lower():
            # Collatz reverse: if even (and came from even), n/2; if 3n+1→even, undo
            n = n * 2 if n % 2 == 0 else (n - 1) // 3
        elif 'n-1' in arev_name or 'predecessor' in arev_name.lower():
            n = max(0, n - 1)
        elif 'sqrt' in arev_name.lower():
            n = int(np.sqrt(n))
        else:
            n = max(0, n - 1)
        traj.append(n)

    state.X = np.array([float(n)])
    state.metadata['trajectory'] = traj
    rev_err = abs(n - original_n) / max(abs(original_n), 1)
    return state, rev_err


def _arev_computational(state, n_steps):
    """Computational reverse: unwind register."""
    for _ in range(n_steps):
        if state.reg == TRUE:
            state.reg = VOID
    return state, 0.0


def _arev_physical(state, dt, n_steps, masses):
    """Physical reverse: time-reversed symplectic integration."""
    m = np.asarray(masses, dtype=float)
    n_bodies = len(m)
    G = 1.0

    w = 1.0 / (2.0 - 2.0 ** (1.0/3.0))
    c = [w/2.0, (1.0-w)/2.0, (1.0-w)/2.0, w/2.0]
    d = [w, 1.0 - 2.0*w, w, 0.0]

    pos_orig = state.X[:3*n_bodies].copy()
    pos = pos_orig.copy()
    mom = state.X[3*n_bodies:].copy()

    def accel(p):
        a = np.zeros_like(p)
        for i in range(n_bodies):
            for j in range(i+1, n_bodies):
                r_ij = p[j] - p[i]
                dist = np.linalg.norm(r_ij)
                if dist > 1e-14:
                    f = G * m[i] * m[j] * r_ij / (dist**3)
                    a[i] += f / m[i]
                    a[j] -= f / m[j]
        return a

    for _ in range(n_steps):
        for ci, di in reversed(list(zip(c, d))):
            a = accel(pos.reshape(n_bodies, 3))
            mom = mom - di * dt * a.flatten()
            pos = pos - ci * dt * mom / m[:, None]

    rev_err = float(np.linalg.norm(pos - pos_orig))
    return state, rev_err


def _arev_generic(state, n_steps):
    """Generic reverse: decrement."""
    if len(state.X) > 0:
        state.X[0] = max(0, state.X[0] - n_steps)
    return state, 0.0


def _arev_symbolic(state, n_steps):
    """Symbolic reverse: unwind register via history."""
    for _ in range(n_steps):
        if state.history:
            state.reg = state.history.pop()
        elif state.reg == TRUE:
            state.reg = VOID
    return state, 0.0


# ═══════════════════════════════════════════════════════════════════════
#  CLINK — Chain Link (sequential composition)
# ═══════════════════════════════════════════════════════════════════════

def clink(state: Ob3ectState, dt=1.0, n_steps=100, masses=None,
          symplecticity_check_interval=1000) -> Tuple[Ob3ectState, List]:
    """CLINK: chain iteration — long forward integration with invariance checks."""
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')

    if cat == 'exec':
        return _clink_exec(state, dt, n_steps, system, masses, symplecticity_check_interval)
    else:
        return _clink_symbolic(state, n_steps)


def _clink_exec(state, dt, n_steps, system, masses, check_interval):
    """CLINK for executable domains."""
    det_log = []
    current = state.copy()

    if system == 'mathematical':
        for step in range(n_steps):
            current = _afwd_mathematical(current, 1)
            n = int(current.X[0])
            if step % check_interval == 0:
                det_log.append((step, float(n)))
            if n == 1:  # convergence
                current.metadata['convergence_target'] = 1
                break

    elif system == 'computational':
        for step in range(n_steps):
            current = _afwd_computational(current, 1)
            if step % check_interval == 0:
                det_log.append((step, float(current.reg)))

    elif system == 'physical' and masses is not None:
        for step in range(n_steps):
            current = _afwd_physical(current, dt, 1, masses)
            if step % check_interval == 0:
                # Check symplecticity via energy conservation
                E, _ = st.compute_conserved(current, masses)
                det_log.append((step, E if isinstance(E, (int, float)) else 1.0))

    else:
        for step in range(n_steps):
            current = _afwd_generic(current, 1)

    return current, det_log


def _clink_symbolic(state, n_steps):
    """CLINK for symbolic domains: chain of Belnap transitions."""
    det_log = []
    current = state.copy()

    for step in range(n_steps):
        current = _afwd_symbolic(current, 1)
        if step % max(1, n_steps // 20) == 0 or step == n_steps - 1:
            det_log.append((step, float(current.reg)))

    return current, det_log


# ═══════════════════════════════════════════════════════════════════════
#  FLOW JACOBIAN (for TANCH / Liouville)
# ═══════════════════════════════════════════════════════════════════════

def compute_flow_jacobian_determinant(state, dt, n_steps, masses=None) -> float:
    """Finite-difference Jacobian determinant for Liouville verification."""
    cat = state.metadata.get('domain_cat', 'symbolic')

    if cat == 'exec' and masses is not None:
        # Physical system: finite-difference Jacobian
        x0 = state.X.copy()
        n = len(x0)
        eps = 1e-6
        J = np.zeros((n, n))
        for i in range(min(n, 6)):  # limit to first 6 dims for speed
            x_plus = x0.copy()
            x_plus[i] += eps
            s_plus = state.copy()
            s_plus.X = x_plus
            s_fwd = _afwd_physical(s_plus, dt, n_steps, masses)
            J[:, i] = (s_fwd.X - state.X) / eps
        return float(np.linalg.det(J[:min(n,6), :min(n,6)]))
    else:
        # Non-physical: identity
        return 1.0
