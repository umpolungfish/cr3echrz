"""
transforms.py — FSPLIT, FFUSE (Jacobi coordinate transformations)

Jacobi coordinates for 3-body system:
  Q0 = (m1*r1 + m2*r2 + m3*r3) / M        — centre of mass
  Q1 = r2 - r1                             — relative 1-2
  Q2 = r3 - (m1*r1 + m2*r2) / M12         — body 3 w.r.t. CM(1,2)

Conjugate momenta:
  P0 = p1 + p2 + p3                        — total CM momentum
  P1 = (m1*p2 - m2*p1) / M12              — relative 1-2
  P2 = (M12*p3 - m3*(p1+p2)) / M          — body 3 vs pair

Reduced masses:
  μ1 = m1*m2 / M12     (for P1²/2μ1 kinetic term)
  μ2 = M12*m3 / M      (for P2²/2μ2 kinetic term)
"""
import numpy as np


def _jacobi_params(masses):
    m = np.asarray(masses, dtype=float)
    M   = m.sum()
    M12 = m[0] + m[1]
    mu1 = m[0] * m[1] / M12
    mu2 = M12  * m[2] / M
    return m, M, M12, mu1, mu2


def fsplit(X, masses):
    """
    FSPLIT: Jacobi split of state X.

    Returns
    -------
    X_cm  : ndarray shape (6,)  — [Q0x,Q0y,Q0z, P0x,P0y,P0z]
    X_rel : ndarray shape (12,) — [Q1(3), Q2(3), P1(3), P2(3)]
    """
    m, M, M12, mu1, mu2 = _jacobi_params(masses)
    pos = X[:9].reshape(3, 3)
    mom = X[9:].reshape(3, 3)

    # --- positions ---
    Q0 = (m[0]*pos[0] + m[1]*pos[1] + m[2]*pos[2]) / M
    Q1 = pos[1] - pos[0]
    Q2 = pos[2] - (m[0]*pos[0] + m[1]*pos[1]) / M12

    # --- momenta ---
    P0 = mom[0] + mom[1] + mom[2]
    P1 = (m[0]*mom[1] - m[1]*mom[0]) / M12
    P2 = (M12*mom[2] - m[2]*(mom[0]+mom[1])) / M

    X_cm  = np.concatenate([Q0, P0])
    X_rel = np.concatenate([Q1, Q2, P1, P2])
    return X_cm, X_rel


def ffuse(X_cm, X_rel, masses):
    """
    FFUSE: inverse Jacobi transform. Reconstructs absolute-frame state X.

    Parameters
    ----------
    X_cm  : ndarray shape (6,)
    X_rel : ndarray shape (12,)

    Returns
    -------
    X : ndarray shape (18,)
    """
    m, M, M12, mu1, mu2 = _jacobi_params(masses)

    Q0 = X_cm[:3];  P0 = X_cm[3:]
    Q1 = X_rel[0:3]; Q2 = X_rel[3:6]
    P1 = X_rel[6:9]; P2 = X_rel[9:12]

    # --- inverse positions ---
    r1 = Q0 - (m[1]/M12)*Q1 - (m[2]/M)*Q2
    r2 = Q0 + (m[0]/M12)*Q1 - (m[2]/M)*Q2
    r3 = Q0                  + (M12/M)*Q2

    # --- inverse momenta ---
    p1 = (m[0]/M)*P0 - P1 - (m[0]/M12)*P2
    p2 = (m[1]/M)*P0 + P1 - (m[1]/M12)*P2
    p3 = (m[2]/M)*P0       +             P2

    X = np.zeros(18)
    X[0:3], X[3:6], X[6:9]      = r1, r2, r3
    X[9:12], X[12:15], X[15:18] = p1, p2, p3
    return X


def propagate_cm_analytical(X_cm, dt):
    """
    CM arm is free-particle (zero force): Q0(t) = Q0(0) + t * P0/M_tot.
    Mass M is not stored here; caller must supply total mass via dt scaling
    or use unit masses. Here we treat it as Q0 += dt * P0 (M absorbed into dt).

    For a proper call: pass dt = t_total / M to get Q0(t) in natural units,
    or just pass t_total and divide the velocity by M in the caller.

    Since M=3 for the figure-8, we handle it generically below.
    Caller passes (X_cm, dt, M) if needed; here M is embedded in X_cm[3:6]
    being P0 (not v0), so velocity = P0 / M. We take M as external parameter.
    """
    # velocity of CM = P0 / M  (but M unknown here; caller normalises)
    # Simplest: return updated position only, caller handles M
    X_cm = X_cm.copy()
    X_cm[:3] += dt * X_cm[3:]   # Q0 += dt * P0 (assumes M=1 normalisation)
    return X_cm


def propagate_cm_analytical_m(X_cm, dt, M):
    """Proper CM propagation with explicit total mass."""
    X_cm = X_cm.copy()
    X_cm[:3] += dt * X_cm[3:] / M
    return X_cm


def jacobi_hamiltonian(X_cm, X_rel, masses):
    """
    Hamiltonian in Jacobi coordinates (for diagnostic use).
    T_cm = P0²/(2M)  +  T_rel = P1²/(2μ1) + P2²/(2μ2)
    V computed from absolute positions recovered by ffuse.
    """
    from cr3echrz.p4rakernel.threebody.state import G
    m, M, M12, mu1, mu2 = _jacobi_params(masses)

    P0 = X_cm[3:];  P1 = X_rel[6:9];  P2 = X_rel[9:12]
    T  = (np.dot(P0,P0)/(2*M)
         + np.dot(P1,P1)/(2*mu1)
         + np.dot(P2,P2)/(2*mu2))

    X = ffuse(X_cm, X_rel, masses)
    pos = X[:9].reshape(3, 3)
    V = 0.0
    for i in range(3):
        for j in range(i+1, 3):
            V -= G * m[i]*m[j] / np.linalg.norm(pos[j]-pos[i])
    return T + V
