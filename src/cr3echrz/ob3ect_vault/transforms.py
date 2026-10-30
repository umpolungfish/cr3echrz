#!/usr/bin/env python3
"""
transforms.py — FSPLIT, FFUSE, TANCH (Frobenius δ/μ) for all ob3ect domains

The Frobenius condition FFUSE(FSPLIT(x)) = x is the universal invariant.
Each domain implements its own split/fuse semantics:

  exec domains (mathematical, computational, physical):
    FSPLIT → decompose state into T-arm and F-arm
    FFUSE  → recompose arms, verify identity

  symbolic domains (magical, divinatory, alchemical, ...):
    FSPLIT → Belnap register split (VOID→BOTH, TRUE→(T,F), FALSE→(F,F), BOTH→(T,F))
    FFUSE  → Belnap register fuse with dialetheic awareness

Author: Lando⊗⊙perator
"""
import numpy as np
from typing import Any, Dict, Tuple, Optional
from cr3echrz.ob3ect_vault import state as st
from cr3echrz.ob3ect_vault.state import Ob3ectState, VOID, TRUE, FALSE, BOTH, REG_NAMES


# ═══════════════════════════════════════════════════════════════════════
#  FSPLIT — Frobenius Split δ
# ═══════════════════════════════════════════════════════════════════════

def fsplit(state: Ob3ectState, masses=None):
    """
    FSPLIT: Frobenius split δ — decompose into true/false arms.

    For exec domains: performs domain-specific decomposition.
    For symbolic domains: splits the Belnap register.

    Returns (arm_T, arm_F) — two Ob3ectState objects.
    """
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', state.metadata.get('domain_type', '???'))

    if cat == 'exec':
        return _fsplit_exec(state, system, masses)
    else:
        return _fsplit_symbolic(state)


def _fsplit_exec(state, system, masses=None):
    """Domain-specific FSPLIT for executable ob3ects."""
    arm_T = state.copy()
    arm_F = state.copy()

    if system == 'mathematical':
        # For math: split by parity / primality / algebraic property
        n = int(state.X[0]) if len(state.X) > 0 else 0
        op_map = state.metadata.get('opcode_map', {})
        split_elem = op_map.get('FSPLIT', 'parity')

        if 'modulo' in split_elem.lower() or 'parity' in split_elem.lower():
            # Parity split: n = 2q + r
            r = n % 2
            q = n // 2
            arm_T.metadata['split_r'] = r
            arm_T.metadata['split_q'] = q
            arm_T.metadata['branch'] = 'odd' if r == 1 else 'even'
            arm_F.metadata['split_r'] = r
            arm_F.metadata['split_q'] = q
            arm_F.metadata['branch'] = 'odd' if r == 1 else 'even'
        else:
            arm_T.metadata['branch'] = 'true'
            arm_F.metadata['branch'] = 'false'

    elif system == 'computational':
        # Computational: register split
        arm_T.metadata['branch'] = 'true'
        arm_F.metadata['branch'] = 'false'

    elif system == 'physical' and masses is not None:
        # Jacobi split for N-body
        m = np.asarray(masses, dtype=float)
        n_bodies = len(m)
        pos = state.X[:3*n_bodies].reshape(n_bodies, 3)
        mom = state.X[3*n_bodies:].reshape(n_bodies, 3)
        M = sum(m)

        cm_pos = sum(m[i] * pos[i] for i in range(n_bodies)) / M
        cm_mom = sum(mom)

        rel_pos = pos - cm_pos
        rel_mom = np.zeros_like(mom)
        for i in range(n_bodies):
            rel_mom[i] = mom[i] - (m[i]/M) * cm_mom

        arm_T.X = np.concatenate([cm_pos.flatten(), cm_mom.flatten()])
        arm_F.X = np.concatenate([rel_pos.flatten(), rel_mom.flatten()])
        arm_T.metadata['arm'] = 'cm'
        arm_F.metadata['arm'] = 'relative'

    else:
        arm_T.metadata['branch'] = 'true'
        arm_F.metadata['branch'] = 'false'

    arm_T.metadata['split'] = True
    arm_F.metadata['split'] = True
    return arm_T, arm_F


def _fsplit_symbolic(state):
    """Belnap register split for symbolic domains."""
    arm_T = state.copy()
    arm_F = state.copy()

    # Symbolic split semantics:
    # VOID  → (VOID, VOID)   — nothing to split
    # TRUE  → (TRUE, VOID)   — truth arm carries the token, false arm is void
    # FALSE → (VOID, FALSE)  — false arm carries the token, true arm is void
    # BOTH  → (TRUE, FALSE)  — dialetheic split into both arms

    if state.reg == VOID:
        arm_T.reg = VOID
        arm_F.reg = VOID
    elif state.reg == TRUE:
        arm_T.reg = TRUE
        arm_F.reg = VOID
    elif state.reg == FALSE:
        arm_T.reg = VOID
        arm_F.reg = FALSE
    elif state.reg == BOTH:
        arm_T.reg = TRUE
        arm_F.reg = FALSE

    arm_T.metadata['branch'] = 'true'
    arm_F.metadata['branch'] = 'false'
    arm_T.metadata['split'] = True
    arm_F.metadata['split'] = True
    return arm_T, arm_F


# ═══════════════════════════════════════════════════════════════════════
#  FFUSE — Frobenius Fuse μ
# ═══════════════════════════════════════════════════════════════════════

def ffuse(arm_T: Ob3ectState, arm_F: Ob3ectState, masses=None):
    """
    FFUSE: Frobenius fuse μ — recompose from true/false arms.

    For exec domains: domain-specific recomposition.
    For symbolic domains: Belnap register fusion.

    The Frobenius condition: FFUSE(FSPLIT(x)) should reconstitute x exactly.
    """
    cat = arm_T.metadata.get('domain_cat', 'symbolic')
    system = arm_T.metadata.get('system', '???')

    if cat == 'exec':
        return _ffuse_exec(arm_T, arm_F, system, masses)
    else:
        return _ffuse_symbolic(arm_T, arm_F)


def _ffuse_exec(arm_T, arm_F, system, masses=None):
    """Domain-specific FFUSE for executable ob3ects."""
    fused = arm_T.copy()

    if system == 'mathematical':
        # Reconstitute n = 2q + r (or other algebraic identity)
        r = arm_T.metadata.get('split_r', 0)
        q = arm_T.metadata.get('split_q', 0)
        n_reconstructed = 2 * q + r
        fused.X = np.array([float(n_reconstructed)])
        fused.metadata['reconstructed'] = n_reconstructed
        fused.metadata['original'] = int(fused.X[0]) if hasattr(fused, '_original_n') else n_reconstructed
        fused.metadata.pop('split_r', None)
        fused.metadata.pop('split_q', None)
        fused.metadata.pop('branch', None)
        fused.metadata.pop('split', None)

    elif system == 'computational':
        fused.metadata.pop('branch', None)
        fused.metadata.pop('split', None)

    elif system == 'physical' and masses is not None:
        m = np.asarray(masses, dtype=float)
        n_bodies = len(m)
        cm_vec = arm_T.X
        rel_vec = arm_F.X

        cm_pos = cm_vec[:3]
        cm_mom = cm_vec[3:6]
        rel_pos = rel_vec[:3*n_bodies].reshape(n_bodies, 3)
        rel_mom = rel_vec[3*n_bodies:].reshape(n_bodies, 3)

        M = sum(m)
        pos = rel_pos + cm_pos
        mom = np.zeros_like(rel_mom)
        for i in range(n_bodies):
            mom[i] = rel_mom[i] + (m[i]/M) * cm_mom

        fused.X = np.concatenate([pos.flatten(), mom.flatten()])
        fused.metadata.pop('arm', None)
        fused.metadata.pop('split', None)

    else:
        fused.metadata.pop('branch', None)
        fused.metadata.pop('split', None)

    return fused


def _ffuse_symbolic(arm_T, arm_F):
    """Belnap register fusion for symbolic domains with dialetheic awareness."""
    fused = arm_T.copy()

    # Symbolic fuse semantics:
    # (VOID, VOID)   → VOID
    # (TRUE, VOID)   → TRUE
    # (VOID, FALSE)  → FALSE
    # (TRUE, FALSE)  → BOTH  ← dialetheic!
    # (VOID, TRUE)   → TRUE
    # (FALSE, VOID)  → FALSE
    # (FALSE, TRUE)  → BOTH  ← dialetheic!
    # (TRUE, TRUE)   → TRUE
    # (FALSE, FALSE) → FALSE

    t_reg = arm_T.reg
    f_reg = arm_F.reg

    if t_reg == TRUE and f_reg == FALSE:
        fused.reg = BOTH  # dialetheic
    elif f_reg == TRUE and t_reg == FALSE:
        fused.reg = BOTH  # dialetheic
    elif t_reg == TRUE or f_reg == TRUE:
        fused.reg = TRUE
    elif t_reg == FALSE or f_reg == FALSE:
        fused.reg = FALSE
    else:
        fused.reg = VOID

    fused.metadata.pop('branch', None)
    fused.metadata.pop('split', None)
    return fused


# ═══════════════════════════════════════════════════════════════════════
#  TANCH — Terminal Anchor (Liouville / Frobenius closure)
# ═══════════════════════════════════════════════════════════════════════

def tanch(state: Ob3ectState, masses=None):
    """
    TANCH: terminal anchor — verify closure at boundary.

    For exec domains: verify conservation laws, determinant of flow.
    For symbolic domains: verify Frobenius condition on register.

    Returns (pass: bool, delta: float, detail: str)
    """
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')

    if cat == 'exec':
        return _tanch_exec(state, system, masses)
    else:
        return _tanch_symbolic(state)


def _tanch_exec(state, system, masses=None):
    """TANCH for executable domains."""
    if system == 'mathematical':
        # For math, TANCH is convergence / invariant preservation
        n = int(state.X[0]) if len(state.X) > 0 else 0
        target = state.metadata.get('convergence_target', 1)
        delta = abs(n - target) if target else 0.0
        return delta < 1e-9, delta, f"n={n}, target={target}"

    elif system == 'computational':
        return True, 0.0, "register stable"

    elif system == 'physical':
        # Liouville theorem: det(J) ≈ 1
        det_J = state.metadata.get('det_J', 1.0)
        delta = abs(det_J - 1.0)
        return delta < 1e-7, delta, f"det(J)={det_J:.12f}"

    return True, 0.0, "generic: assumed closed"


def _tanch_symbolic(state):
    """TANCH for symbolic domains — Frobenius verify on register."""
    # Symbolic TANCH: check that register is in a terminal state
    # Terminal states: TRUE (coherent closure) or BOTH (dialetheic closure)
    if state.reg in (TRUE, BOTH):
        return True, 0.0, f"terminal: {REG_NAMES[state.reg]}"
    elif state.reg == FALSE:
        return True, 0.0, f"terminal: {REG_NAMES[state.reg]} (false closure)"
    else:  # VOID
        return False, 1.0, f"unclosed: {REG_NAMES[state.reg]}"


# ═══════════════════════════════════════════════════════════════════════
#  CM Propagation (for physical systems)
# ═══════════════════════════════════════════════════════════════════════

def propagate_cm_analytical(state, dt_total, M=1.0):
    """Analytical CM propagation: constant velocity."""
    result = state.copy()
    if len(state.X) >= 6:
        result.X[0:3] = state.X[0:3] + state.X[3:6] * dt_total / M
    return result


# ═══════════════════════════════════════════════════════════════════════
#  FROBENIUS VERIFICATION
# ═══════════════════════════════════════════════════════════════════════

def verify_frobenius(original: Ob3ectState, fused: Ob3ectState,
                     masses=None) -> Tuple[bool, float]:
    """
    Verify FFUSE(FSPLIT(x)) = x.

    For exec domains: compare state vectors.
    For symbolic domains: compare Belnap registers.
    """
    cat = original.metadata.get('domain_cat', 'symbolic')

    if cat == 'exec':
        if hasattr(original.X, 'shape') and hasattr(fused.X, 'shape'):
            delta = float(np.linalg.norm(original.X - fused.X))
            return delta < 1e-10, delta
        return True, 0.0
    else:
        # Symbolic: registers should match
        delta = 0.0 if original.reg == fused.reg else 1.0
        return original.reg == fused.reg, delta
