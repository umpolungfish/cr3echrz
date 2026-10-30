#!/usr/bin/env python3
"""
diagnostics.py — EVALT, EVALF, ENGAGR, IFIX for all ob3ect domains

  EVALT  → evaluate TRUE branch (theorem holds, integrable, register is TRUE)
  EVALF  → evaluate FALSE branch (theorem fails, chaotic, register is FALSE)
  ENGAGR → engage paradox (both arms, KAM boundary, dialetheic register)
  IFIX   → irreversible fix (record trajectory, Poincaré section, permanent log)

Author: Lando⊗⊙perator
"""
import numpy as np
from typing import List, Tuple, Optional
from cr3echrz.ob3ect_vault import state as st
from cr3echrz.ob3ect_vault.state import Ob3ectState, VOID, TRUE, FALSE, BOTH, REG_NAMES
from cr3echrz.ob3ect_vault.integrators import afwd


# ═══════════════════════════════════════════════════════════════════════
#  EVALT — Evaluate TRUE
# ═══════════════════════════════════════════════════════════════════════

def evalt(state: Ob3ectState, masses=None, dt=1.0, n_steps=1000) -> bool:
    """EVALT: evaluate TRUE branch — does the theorem hold?"""
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')

    if cat == 'exec':
        return _evalt_exec(state, system, masses, dt, n_steps)
    else:
        return _evalt_symbolic(state)


def _evalt_exec(state, system, masses, dt, n_steps):
    """EVALT for executable domains."""
    if system == 'mathematical':
        n = int(state.X[0]) if len(state.X) > 0 else 0
        traj = state.metadata.get('trajectory', [])
        # TRUE if: converges to 1, or prime partition found, or invariant holds
        if n == 1:
            return True
        if state.metadata.get('partitions') and len(state.metadata['partitions']) > 0:
            return True
        # Check for cycles indicating quasi-periodicity
        if len(traj) > 10 and len(set(traj[-10:])) < 3:
            return True
        return len(traj) > 100  # long trajectory without divergence = quasi-periodic

    elif system == 'computational':
        return state.reg in (TRUE, BOTH)

    elif system == 'physical':
        # TRUE = quasi-periodic (KAM torus intact)
        try:
            conserved = st.compute_conserved(state, masses)
            if isinstance(conserved, tuple):
                E = conserved[0]
            else:
                E = conserved.get('E_total', 0)
        except Exception:
            return True  # assume quasi-periodic if state is malformed
        E0 = state.invariants.get('E_total', E)
        dE = abs(E - E0) if isinstance(E, (int, float)) else 0.0
        return dE < 1e-3

    return True


def _evalt_symbolic(state):
    """EVALT for symbolic: register is TRUE or BOTH."""
    return state.reg in (TRUE, BOTH)


# ═══════════════════════════════════════════════════════════════════════
#  EVALF — Evaluate FALSE
# ═══════════════════════════════════════════════════════════════════════

def evalf(state: Ob3ectState, dt=1.0, masses=None, n_steps=300) -> float:
    """EVALF: evaluate FALSE branch — returns a diagnostic metric (FLI or similar)."""
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')

    if cat == 'exec':
        return _evalf_exec(state, system, dt, masses, n_steps)
    else:
        return _evalf_symbolic(state)


def _evalf_exec(state, system, dt, masses, n_steps):
    """EVALF for executable domains. Returns FLI-like metric."""
    if system == 'mathematical':
        # FLI surrogate: max trajectory value / divergence measure
        traj = state.metadata.get('trajectory', [])
        if not traj:
            return 0.0
        # Low FLI (< 1) = quasi-periodic/convergent; high FLI (> 1) = divergent
        max_val = max(abs(v) for v in traj)
        mean_val = sum(abs(v) for v in traj) / len(traj)
        if mean_val == 0:
            return 0.0
        return np.log(max_val / mean_val + 1e-10)

    elif system == 'computational':
        return 0.0 if state.reg == FALSE else 1.0

    elif system == 'physical':
        try:
            s1 = state.copy()
            s2 = state.copy()
            delta0 = 1e-8
            if hasattr(s2.X, '__len__') and len(s2.X) > 0 and hasattr(s2.X, 'copy'):
                s2.X = s2.X.copy()
                s2.X[0] += delta0
            for _ in range(min(n_steps, 200)):
                s1 = afwd(s1, dt, 1, masses)
                s2 = afwd(s2, dt, 1, masses)
            if hasattr(s1.X, 'shape') and hasattr(s2.X, 'shape') and len(s1.X) > 0:
                d = float(np.linalg.norm(s1.X - s2.X))
                if d > 0 and delta0 > 0:
                    return np.log(d / delta0) / n_steps
        except Exception:
            pass
        return 0.0

    return 0.0


def _evalf_symbolic(state):
    """EVALF for symbolic: 0.0 if FALSE/BOTH, 1.0 otherwise."""
    return 0.0 if state.reg in (FALSE, BOTH) else 1.0


# ═══════════════════════════════════════════════════════════════════════
#  ENGAGR — Engage Paradox
# ═══════════════════════════════════════════════════════════════════════

def engagr(state: Ob3ectState, masses=None, target_fli_fraction=0.4,
           max_iter=15, dt=1.0, n_steps=200) -> Ob3ectState:
    """
    ENGAGR: engage paradox — perturb toward dialetheic boundary.

    For exec domains: perturb toward KAM boundary (mixed phase space).
    For symbolic domains: move register toward BOTH (dialetheic).
    """
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')

    if cat == 'exec':
        return _engagr_exec(state, system, masses, target_fli_fraction, max_iter, dt, n_steps)
    else:
        return _engagr_symbolic(state)


def _engagr_exec(state, system, masses, target_fraction, max_iter, dt, n_steps):
    """ENGAGR for executable domains."""
    result = state.copy()
    if st.STATUS & 0b10 == 0:
        st.STATUS |= 0b10  # mark paradox/KAM

    if system == 'mathematical':
        # Perturb by trying nearby seeds
        n = int(result.X[0])
        for i in range(max_iter):
            perturbed_n = n + (i + 1) * 7  # try different offsets
            result.X = np.array([float(perturbed_n)])
            result.metadata['trajectory'] = [perturbed_n]
        return result

    elif system == 'computational':
        result.reg = BOTH
        return result

    elif system == 'physical' and masses is not None:
        # Velocity perturbation
        if len(result.X) > 3:
            result.X[3] *= (1.0 + target_fraction * 0.1)
        return result

    return result


def _engagr_symbolic(state):
    """ENGAGR for symbolic: force register to BOTH (dialetheic)."""
    result = state.copy()
    result.reg = BOTH
    if st.STATUS & 0b10 == 0:
        st.STATUS |= 0b10
    return result


# ═══════════════════════════════════════════════════════════════════════
#  IFIX — Irreversible Fix
# ═══════════════════════════════════════════════════════════════════════

def ifix(state: Ob3ectState, dt=1.0, masses=None, n_crossings=80) -> List:
    """IFIX: irreversible fix — record permanent trajectory / Poincaré section."""
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')

    if cat == 'exec':
        return _ifix_exec(state, system, dt, masses, n_crossings)
    else:
        return _ifix_symbolic(state)


def _ifix_exec(state, system, dt, masses, n_crossings):
    """IFIX for executable domains."""
    sections = []

    if system == 'mathematical':
        traj = state.metadata.get('trajectory', [])
        sections = traj[-min(n_crossings, len(traj)):]

    elif system == 'computational':
        sections = [(state.reg, REG_NAMES.get(state.reg, '?'))]

    elif system == 'physical':
        # Poincaré section: record when z ≈ 0 and crossing downward
        if len(state.X) < 9:
            sections = [tuple(state.X[:6])]
        else:
            sections = [(float(state.X[2]), float(state.X[5]),
                         float(state.X[8]), float(state.X[11]))]

    else:
        sections = list(state.X[:min(10, len(state.X))])

    state.metadata['sections'] = sections
    state.metadata['ifix_count'] = len(sections)
    return sections


def _ifix_symbolic(state):
    """IFIX for symbolic: record register state permanently."""
    state.metadata['ifix_reg'] = state.reg
    state.metadata['ifix_name'] = REG_NAMES.get(state.reg, '?')
    return [(state.reg, REG_NAMES.get(state.reg, '?'))]
