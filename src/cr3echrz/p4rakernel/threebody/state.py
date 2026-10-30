"""
state.py — VINIT, IMSCRIB, status register
Phase-space state vector X has length 18:
  X[0:9]  = positions  [x1,y1,z1, x2,y2,z2, x3,y3,z3]
  X[9:18] = momenta    [px1,py1,pz1, px2,py2,pz2, px3,py3,pz3]
"""
import numpy as np

# Global status register (2-bit)
STATUS = 0b00   # 0b00 void | 0b01 integrable | 0b10 chaotic | 0b11 KAM

G = 1.0  # gravitational constant in natural units


def vinit():
    """VINIT: initialise void state. Returns zero state vector, STATUS=0b00."""
    global STATUS
    STATUS = 0b00
    return np.zeros(18)


def imscrib(X, masses):
    """
    IMSCRIB: inject masses; compute and return conserved quantities E and L.
    Does NOT modify X positions/momenta — call after setting initial conditions.
    Sets STATUS=0b01 (integrable mode).
    Returns: X, E_total (float), L_vector (array shape (3,))
    """
    global STATUS
    m = np.asarray(masses, dtype=float)
    E, L = compute_conserved(X, m)
    STATUS = 0b01
    return X, E, L


def compute_conserved(X, masses):
    """
    Compute total energy E and angular momentum vector L from state X.
    Returns: E (float), L (ndarray shape (3,))
    """
    m = np.asarray(masses, dtype=float)
    pos = X[:9].reshape(3, 3)
    mom = X[9:].reshape(3, 3)

    # Kinetic energy T = Σ p_i² / (2 m_i)
    T = sum(0.5 * np.dot(mom[i], mom[i]) / m[i] for i in range(3))

    # Potential energy V = -G Σ_{i<j} m_i m_j / |r_i - r_j|
    V = 0.0
    for i in range(3):
        for j in range(i + 1, 3):
            r_ij = np.linalg.norm(pos[j] - pos[i])
            V -= G * m[i] * m[j] / r_ij

    E = T + V

    # Angular momentum L = Σ r_i × p_i
    L = sum(np.cross(pos[i], mom[i]) for i in range(3))

    return E, L


def figure8_ic():
    """
    Chenciner-Montgomery figure-8 initial conditions.
    Three equal masses m=1 tracing a single figure-8 path.
    Returns X (array 18,) with masses [1,1,1].
    """
    r1 = np.array([-0.97000436,  0.24308753, 0.0])
    r2 = np.array([ 0.0,         0.0,        0.0])
    r3 = np.array([ 0.97000436, -0.24308753, 0.0])

    # Velocity of each body (CM momentum = 0 by symmetry)
    v12 = np.array([0.93240737 / 2.0, 0.86473146 / 2.0, 0.0])
    v2  = np.array([-0.93240737, -0.86473146, 0.0])

    # With m=1, momenta = velocities
    p1, p2, p3 = v12.copy(), v2.copy(), v12.copy()

    X = np.zeros(18)
    X[0:3], X[3:6], X[6:9]   = r1, r2, r3
    X[9:12], X[12:15], X[15:18] = p1, p2, p3
    return X


def pythagorean_ic():
    """
    Pythagorean three-body problem: m=[3,4,5], bodies start at rest
    at positions forming a 3-4-5 right triangle.
    Returns X (array 18,) with masses [3.0, 4.0, 5.0].
    """
    r1 = np.array([1.0,  3.0, 0.0])
    r2 = np.array([-2.0, -1.0, 0.0])
    r3 = np.array([1.0, -1.0, 0.0])

    X = np.zeros(18)
    X[0:3], X[3:6], X[6:9] = r1, r2, r3
    # Momenta zero — bodies start from rest
    return X
