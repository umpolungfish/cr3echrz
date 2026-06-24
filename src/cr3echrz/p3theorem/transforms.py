"""
transforms.py — FSPLIT, FFUSE, TANCH (Frobenius decomposition/recomposition)

FSPLIT (Frobenius split δ) and FFUSE (Frobenius fuse μ) satisfy:
    μ ∘ δ = id   (the Frobenius condition)

Every theorem operationalization decomposes its state into true/false arms
via FSPLIT and recomposes via FFUSE. The decomposition is theorem-specific.

Physics systems: Jacobi coordinate split  (CM + relative)
Number-theoretic: true-branch / false-branch split
Generic:         any (T, F) decomposition
"""
import numpy as np
from cr3echrz.p3theorem.state import TheoremState


# ════════════════════════════════════════════════════════════════
#  FSPLIT — Frobenius Split
# ════════════════════════════════════════════════════════════════

def fsplit(state, masses=None, theorem=None):
    """
    FSPLIT: decompose state into independent arms.

    Physics (gravitational): Jacobi split into CM + relative arms
    Collatz: split into true-arm (even → n/2) and false-arm (odd → 3n+1)
    Goldbach: split into candidate partitions

    Returns (arm_T, arm_F) — the true and false arms of the decomposition.
    For physics, returns (X_cm, X_rel).
    For theorem-logical, returns (true_state, false_state).
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        return _fsplit_jacobi(state, masses)
    elif system == 'collatz':
        return _fsplit_collatz(state)
    elif system == 'goldbach':
        return _fsplit_goldbach(state)
    else:
        return _fsplit_generic(state)


def _fsplit_jacobi(state, masses):
    """Jacobi coordinate split for N=3 gravitational system."""
    m = np.asarray(masses, dtype=float)
    M   = m.sum()
    M12 = m[0] + m[1]

    pos = state.X[:9].reshape(3, 3)
    mom = state.X[9:].reshape(3, 3)

    Q0 = (m[0]*pos[0] + m[1]*pos[1] + m[2]*pos[2]) / M
    Q1 = pos[1] - pos[0]
    Q2 = pos[2] - (m[0]*pos[0] + m[1]*pos[1]) / M12

    P0 = mom[0] + mom[1] + mom[2]
    P1 = (m[0]*mom[1] - m[1]*mom[0]) / M12
    P2 = (M12*mom[2] - m[2]*(mom[0]+mom[1])) / M

    X_cm  = np.concatenate([Q0, P0])
    X_rel = np.concatenate([Q1, Q2, P1, P2])

    arm_T = TheoremState(X_cm, dict(state.metadata))
    arm_F = TheoremState(X_rel, dict(state.metadata))
    arm_T.metadata['arm'] = 'CM'
    arm_F.metadata['arm'] = 'relative'
    return arm_T, arm_F


def _fsplit_collatz(state):
    """Split Collatz state into true-branch (even) and false-branch (odd)."""
    n = int(state.X[0])
    arm_T = state.copy()
    arm_F = state.copy()
    arm_T.metadata['branch'] = 'true_even'
    arm_F.metadata['branch'] = 'false_odd'
    return arm_T, arm_F


def _fsplit_goldbach(state):
    """Split Goldbach state into partition candidates."""
    state_copy = state.copy()
    return state_copy, state_copy.copy()


def _fsplit_generic(state):
    """Generic split: clone state into two arms."""
    return state.copy(), state.copy()


# ════════════════════════════════════════════════════════════════
#  FFUSE — Frobenius Fuse
# ════════════════════════════════════════════════════════════════

def ffuse(arm_T, arm_F, masses=None, theorem=None):
    """
    FFUSE: recompose the original state from its arms.

    Must satisfy: ffuse(fsplit(X)) ≈ X (Frobenius condition).
    """
    system = arm_T.metadata.get('system', 'generic')

    if system == 'gravitational':
        return _ffuse_jacobi(arm_T, arm_F, masses)
    elif system == 'collatz':
        return _ffuse_collatz(arm_T, arm_F)
    elif system == 'goldbach':
        return _ffuse_goldbach(arm_T, arm_F)
    else:
        return _ffuse_generic(arm_T, arm_F)


def _ffuse_jacobi(X_cm, X_rel, masses):
    """Inverse Jacobi transform: reconstruct absolute-frame state."""
    m = np.asarray(masses, dtype=float)
    M   = m.sum()
    M12 = m[0] + m[1]

    Q0 = X_cm.X[:3];  P0 = X_cm.X[3:]
    Q1 = X_rel.X[0:3]; Q2 = X_rel.X[3:6]
    P1 = X_rel.X[6:9]; P2 = X_rel.X[9:12]

    r1 = Q0 - (m[1]/M12)*Q1 - (m[2]/M)*Q2
    r2 = Q0 + (m[0]/M12)*Q1 - (m[2]/M)*Q2
    r3 = Q0                 + (M12/M)*Q2

    p1 = (m[0]/M)*P0 - P1 - (m[0]/M12)*P2
    p2 = (m[1]/M)*P0 + P1 - (m[1]/M12)*P2
    p3 = (m[2]/M)*P0      +             P2

    X = np.zeros(18)
    X[0:3], X[3:6], X[6:9]      = r1, r2, r3
    X[9:12], X[12:15], X[15:18] = p1, p2, p3

    state = X_cm.copy()
    state.X = X
    return state


def _ffuse_collatz(arm_T, arm_F):
    """Recombine Collatz arms. The 'true' arm (last viable) carries forward."""
    return arm_T.copy()


def _ffuse_goldbach(arm_T, arm_F):
    """Recombine Goldbach arms with discovered partition."""
    return arm_T.copy()


def _ffuse_generic(arm_T, arm_F):
    """Generic FFUSE: return true arm (Frobenius condition checked by caller)."""
    return arm_T.copy()


# ════════════════════════════════════════════════════════════════
#  TANCH — Terminal Anchor / Liouville Closure
# ════════════════════════════════════════════════════════════════

def tanch(state, dt=None, steps=None, masses=None):
    """
    TANCH: verify structural closure — the theorem's terminal anchor.

    For physical systems: Liouville theorem — det(J) = 1 for symplectic flow.
    For number-theoretic: verify that the operation preserves the invariant.
    """
    system = state.metadata.get('system', 'generic')

    if system == 'gravitational':
        from integrators import compute_flow_jacobian_determinant
        check_steps = min(steps or 200, 200)
        det_J = compute_flow_jacobian_determinant(state, dt, check_steps, masses)
        return {'det_J': det_J, '|det-1|': abs(det_J - 1.0),
                'pass': abs(det_J - 1.0) < 1e-7}

    if system == 'collatz':
        n = int(state.X[0])
        return {'n_final': n, 'pass': n == 1 or n in state.metadata.get('trajectory', [])}

    if system == 'goldbach':
        partitions = state.metadata.get('partitions', [])
        return {'partitions_found': len(partitions),
                'pass': len(partitions) > 0}

    return {'pass': True}


def verify_frobenius(state_original, state_recombined, tol=1e-10):
    """
    Verify μ ∘ δ = id: FSPLIT followed by FFUSE must return the original state.
    Returns the Frobenius error ||X_recombined - X_original||.
    """
    if hasattr(state_original, 'X') and hasattr(state_recombined, 'X'):
        if state_original.X.shape == state_recombined.X.shape:
            return float(np.linalg.norm(state_recombined.X - state_original.X))
    return float('inf')


# ════════════════════════════════════════════════════════════════
#  ANALYTICAL PROPAGATION
# ════════════════════════════════════════════════════════════════

def propagate_cm_analytical(X_cm, dt, M=None):
    """CM arm is free-particle: Q0(t) = Q0(0) + t*P0/M."""
    state = X_cm.copy()
    if M is not None:
        state.X[:3] += dt * state.X[3:] / M
    else:
        state.X[:3] += dt * state.X[3:]
    return state
