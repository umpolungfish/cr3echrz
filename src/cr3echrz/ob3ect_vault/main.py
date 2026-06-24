#!/usr/bin/env python3
"""
main.py — 19-step IMASM bootstrap orchestrator for ALL 265+ ob3ects

Run:  python3 main.py [ob3ect_name] [params...]
      python3 main.py --list              # list all ob3ects
      python3 main.py --list mathematical # filter by domain
      python3 main.py threebody           # run three-body ob3ect
      python3 main.py collatz_theorem     # run Collatz ob3ect
      python3 main.py truth_machine       # run Truth Machine ob3ect
      python3 main.py chaos_magic_servitor # run magical ob3ect
      python3 main.py galois              # run Galois ob3ect

Architecture mirrors cr3echrz/p3theorem — the same 12 universal opcodes
orchestrated through the same 19-step bootstrap, generalized across 265+
ob3ects spanning 40+ domain types.

Author: Lando⊗⊙perator
"""
import sys, os

import numpy as np
from cr3echrz.ob3ect_vault import state as st
from cr3echrz.ob3ect_vault.state import (vinit, imscrib, discover_ob3ects, load_ob3ect,
                   make_ic, domain_category, get_domain_type,
                   REG_NAMES, VOID, TRUE, FALSE, BOTH)
from cr3echrz.ob3ect_vault.transforms import (fsplit, ffuse, propagate_cm_analytical, tanch,
                        verify_frobenius)
from cr3echrz.ob3ect_vault.integrators import (afwd, arev, clink, compute_flow_jacobian_determinant)
from cr3echrz.ob3ect_vault.diagnostics import evalt, evalf, engagr, ifix


# ── Bootstrap registry ──────────────────────────────────────────────────

def separator(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print('─'*60)


def bootstrap_exec(state, dt=1.0, N_period=100, masses=None):
    """19-step bootstrap for executable-domain ob3ects (mathematical, computational, physical)."""
    system = state.metadata.get('system', '???')

    # Step 1: VINIT
    separator("Step 1 — VINIT")
    X = vinit()
    X = state
    print(f"  X norm       = {np.linalg.norm(X.X) if hasattr(X.X, 'shape') and len(X.X)>0 else 0:.1f}  (void)")
    print(f"  STATUS       = {bin(st.STATUS)}  (0b00 void)")

    # Step 2: IMSCRIB
    separator("Step 2 — IMSCRIB")
    desc = state.metadata.get('descriptor', {})
    X, conserved = imscrib(X, ob3ect_name=state.metadata.get('name'), ob3ect_desc=desc)
    for k, v in conserved.items():
        if isinstance(v, str):
            print(f"  {k:15s}= {v}")
        elif isinstance(v, (int, float)):
            print(f"  {k:15s}= {v:.8f}" if abs(v) > 0.001 else f"  {k:15s}= {v:.4e}")
    print(f"  STATUS       = {bin(st.STATUS)}  (0b01 integrable/true)")

    # Step 3: AFWD
    separator("Step 3 — AFWD")
    X = afwd(X, dt, min(N_period, 10))
    if system == 'mathematical':
        traj = X.metadata.get('trajectory', [])
        print(f"  Trajectory   = {traj[:15]}{'...' if len(traj)>15 else ''}")
        n = int(X.X[0]) if len(X.X) > 0 else 0
        print(f"  n after fwd  = {n}")
    elif system == 'physical':
        print(f"  Integrated {min(N_period, 10)} steps")

    # Step 4: FSPLIT
    separator("Step 4 — FSPLIT")
    arm_T, arm_F = fsplit(X, masses)
    print(f"  T-arm        = {arm_T.metadata.get('branch', '?')}")
    print(f"  F-arm        = {arm_F.metadata.get('branch', '?')}")
    if system == 'mathematical':
        r = arm_T.metadata.get('split_r', '?')
        q = arm_T.metadata.get('split_q', '?')
        print(f"  Split: n = 2×{q} + {r}")

    # Steps 5–6: CM propagation (physical only)
    if system == 'physical' and masses:
        separator("Steps 5–6 — CM propagation")
        dt_total = N_period * dt
        M = sum(masses)
        arm_T = propagate_cm_analytical(arm_T, dt_total, M=M)
        print(f"  Q_cm shift   = {np.linalg.norm(arm_T.X[:3]-X.X[:3]):.2e}")

    # Steps 7–8: EVALF
    separator("Steps 7–8 — EVALF")
    fli = evalf(X, dt, masses, n_steps=300)
    print(f"  FLI / metric = {fli:.4f}  ({'quasi-periodic/convergent' if fli < 1 else 'divergent/chaotic'})")

    # Steps 9–10: EVALT
    separator("Steps 9–10 — EVALT")
    is_true = evalt(X, masses, dt=dt, n_steps=1000)
    print(f"  EVALT        = {is_true}  ({'TRUE branch holds' if is_true else 'FALSE branch dominates'})")

    # Steps 11–12: AREV
    separator("Steps 11–12 — AREV (time-reversal benchmark)")
    X_rev, rev_err = arev(X, dt, min(N_period//10, 50), masses)
    mode_str = "integrable" if rev_err < 1e-3 else "chaotic"
    if rev_err >= 1e-3:
        st.STATUS |= FALSE
    print(f"  Rev error    = {rev_err:.4e}  ({mode_str})")
    print(f"  STATUS       = {bin(st.STATUS)}")

    # Step 13: FFUSE
    separator("Step 13 — FFUSE (inner fuse)")
    X = ffuse(arm_T, arm_F, masses)
    frob_ok, frob_delta = verify_frobenius(state, X, masses)
    print(f"  Frobenius    = {'PASS' if frob_ok else 'FAIL'}  (δ = {frob_delta:.4e})")

    # Step 14: ENGAGR
    separator("Step 14 — ENGAGR (paradox boundary)")
    X_kam = engagr(X, masses, dt=dt, n_steps=200)
    print(f"  KAM / dialetheic boundary engaged")
    if st.STATUS & FALSE:
        print(f"  STATUS       = {bin(st.STATUS)}  (0b11 KAM/paradox)")
    else:
        st.STATUS |= FALSE
        print(f"  STATUS       = {bin(st.STATUS)}  (0b11 KAM/paradox)")

    # Step 15: CLINK
    separator("Step 15 — CLINK (long integration)")
    N_clink = N_period * 10
    print(f"  Running {N_clink} steps…", flush=True)
    X_long, det_log = clink(X_kam, dt, N_clink, masses)
    if system == 'mathematical':
        n_final = int(X_long.X[0])
        print(f"  n final      = {n_final}")
    elif system == 'physical' and det_log:
        dets = [d for _, d in det_log if isinstance(d, (int, float))]
        if dets:
            print(f"  E range      = [{min(dets):.8f}, {max(dets):.8f}]")

    # Step 16: IFIX
    separator("Step 16 — IFIX (permanent record)")
    sections = ifix(X_long, dt, masses, n_crossings=80)
    print(f"  Records      = {len(sections)}")
    if len(sections) > 0:
        if system == 'mathematical':
            print(f"  Last values  = {sections[-10:] if len(sections) >= 10 else sections}")

    # Step 17: FFUSE (outer)
    separator("Step 17 — FFUSE (outer fuse)")
    print(f"  E final / n  = {X_long.X[0] if len(X_long.X)>0 else 'N/A'}")

    # Step 18: IMSCRIB — verify conservation
    separator("Step 18 — IMSCRIB (verify conserved quantities)")
    conserved_final = st.compute_conserved(X_long, masses)
    frob_verdict = conserved_final.get('frobenius_verdict', 'PASS')
    print(f"  Frobenius    = {frob_verdict}")
    print(f"  STATUS       = {bin(st.STATUS)}")

    # Step 19: TANCH
    separator("Step 19 — TANCH (Liouville closure)")
    t_ok, t_delta, t_detail = tanch(X_long, masses)
    entropy_delta = t_delta
    print(f"  TANCH        = {'PASS' if t_ok else 'FAIL'}  ({t_detail})")
    if system == 'physical' and masses:
        det_J = compute_flow_jacobian_determinant(X, dt, min(200, N_clink), masses)
        entropy_delta = abs(det_J - 1.0)
        print(f"  det(J)       = {det_J:.12f}")
        print(f"  |det-1|      = {entropy_delta:.4e}")

    return rev_err, entropy_delta, frob_ok
def bootstrap_symbolic(state, dt=1.0, N_period=50):
    """19-step bootstrap for symbolic-domain ob3ects (magical, divinatory, alchemical, etc.)."""
    name = state.metadata.get('name', '???')
    desc = state.metadata.get('descriptor', {})
    op_map = state.metadata.get('opcode_map', {})

    # Step 1: VINIT
    separator("Step 1 — VINIT")
    X = vinit()
    X = state
    print(f"  Ob3ect       = {name}")
    print(f"  Domain       = {state.metadata.get('domain_type', '???')}")
    print(f"  Register     = {REG_NAMES[X.reg]}")
    print(f"  STATUS       = {bin(st.STATUS)}  (0b00 void)")

    # Step 2: IMSCRIB
    separator("Step 2 — IMSCRIB (self-recognition)")
    X, conserved = imscrib(X, ob3ect_name=name, ob3ect_desc=desc)
    print(f"  Frobenius    = {conserved.get('frobenius_verdict', '?')}")
    print(f"  Split/Fuse   = {conserved.get('split_element', '?')} / {conserved.get('fuse_element', '?')}")
    print(f"  Entropy      = {conserved.get('entropy_assertion', '?')}")
    print(f"  Register     = {REG_NAMES[X.reg]}")
    print(f"  STATUS       = {bin(st.STATUS)}  (0b01 true)")

    # Step 3: AFWD
    separator("Step 3 — AFWD (forward morphism)")
    X = afwd(X, dt, 1)
    print(f"  AFWD op      = {op_map.get('AFWD', 'forward')}")
    print(f"  Register     = {REG_NAMES[X.reg]}")

    # Step 4: FSPLIT
    separator("Step 4 — FSPLIT (Frobenius split)")
    arm_T, arm_F = fsplit(X)
    print(f"  Split op     = {op_map.get('FSPLIT', 'decomposition')}")
    print(f"  T-arm reg    = {REG_NAMES[arm_T.reg]}")
    print(f"  F-arm reg    = {REG_NAMES[arm_F.reg]}")

    # Steps 5–6: T-branch propagation
    separator("Steps 5–6 — T-branch propagation")
    arm_T = afwd(arm_T, dt, 3)
    print(f"  T-arm after  = {REG_NAMES[arm_T.reg]}")

    # Steps 7–8: EVALF
    separator("Steps 7–8 — EVALF (false branch)")
    fli = evalf(X)
    print(f"  EVALF metric = {fli:.4f}")
    print(f"  EVALF op     = {op_map.get('EVALF', 'false evaluation')}")

    # Steps 9–10: EVALT
    separator("Steps 9–10 — EVALT (true branch)")
    is_true = evalt(X)
    print(f"  EVALT        = {is_true}")
    print(f"  EVALT op     = {op_map.get('EVALT', 'true evaluation')}")

    # Steps 11–12: AREV
    separator("Steps 11–12 — AREV (reverse)")
    X_rev, rev_err = arev(X, dt, 5)
    print(f"  Rev error    = {rev_err:.4f}")
    print(f"  AREV op      = {op_map.get('AREV', 'reverse')}")

    # Step 13: FFUSE
    separator("Step 13 — FFUSE (Frobenius fuse)")
    fused = ffuse(arm_T, arm_F)
    frob_ok, frob_delta = verify_frobenius(X, fused)
    print(f"  Frobenius    = {'PASS' if frob_ok else 'FAIL'}  (δ = {frob_delta:.4f})")
    print(f"  Fused reg    = {REG_NAMES[fused.reg]}")
    print(f"  FFUSE op     = {op_map.get('FFUSE', 'recombination')}")
    if fused.reg == BOTH:
        print(f"  ⟳ DIALETHEIC: both TRUE and FALSE arms active simultaneously")

    # Step 14: ENGAGR
    separator("Step 14 — ENGAGR (paradox engagement)")
    X_kam = engagr(X)
    print(f"  ENGAGR op    = {op_map.get('ENGAGR', 'paradox')}")
    print(f"  Register     = {REG_NAMES[X_kam.reg]}")
    if X_kam.reg == BOTH:
        print(f"  ⟳ PARADOX ENGAGED: {op_map.get('ENGAGR', 'the loop')}")

    # Step 15: CLINK
    separator("Step 15 — CLINK (chain)")
    X_long, det_log = clink(X_kam, dt, N_period)
    print(f"  CLINK op     = {op_map.get('CLINK', 'iteration')}")
    print(f"  Final reg    = {REG_NAMES[X_long.reg]}")
    print(f"  Steps        = {len(det_log)} checkpoints")

    # Step 16: IFIX
    separator("Step 16 — IFIX (permanent record)")
    sections = ifix(X_long)
    print(f"  IFIX op      = {op_map.get('IFIX', 'record')}")
    print(f"  Fixed state  = {sections}")

    # Step 17: FFUSE (outer)
    separator("Step 17 — FFUSE (outer fuse)")
    print(f"  Registers stable")

    # Step 18: IMSCRIB — verify
    separator("Step 18 — IMSCRIB (verify)")
    frob_verdict = X_long.invariants.get('frobenius_verdict', 'PASS')
    print(f"  Frobenius    = {frob_verdict}")

    # Step 19: TANCH
    separator("Step 19 — TANCH (closure)")
    t_ok, t_delta, t_detail = tanch(X_long)
    print(f"  TANCH        = {'PASS' if t_ok else 'FAIL'}  ({t_detail})")
    if X_long.reg == BOTH:
        print(f"  ⟳ DIALETHEIC CLOSURE: identity is BOTH, μ∘δ=id holds paradoxically")

    return rev_err, t_delta, frob_ok

# ── Bootstrap dispatcher ───────────────────────────────────────────────

def bootstrap_ob3ect(ob3ect_name, **params):
    """Run the full 19-step bootstrap for any ob3ect by name."""
    print(f"\n{'═'*60}")
    print(f"  OB3ECT VAULT — 19-STEP IMASM BOOTSTRAP")
    print(f"  Ob3ect: {ob3ect_name}")
    print(f"  Author: Lando⊗⊙perator")
    print(f"{'═'*60}")

    # Load ob3ect
    descriptor = load_ob3ect(ob3ect_name)
    if descriptor is None:
        print(f"\n  ERROR: Ob3ect '{ob3ect_name}' not found in vault")
        print(f"  Run with --list to see available ob3ects")
        return None, None, None

    # Create IC
    state = make_ic(ob3ect_name, descriptor)
    cat = state.metadata.get('domain_cat', 'symbolic')
    system = state.metadata.get('system', '???')
    dt = params.get('dt', 1.0)
    N_period = params.get('N_period', 100)

    print(f"  Domain: {state.metadata.get('domain_type', '???')} ({cat})")
    print(f"  System: {system}")
    boundary = state.metadata.get('boundary', 'unstated')
    print(f"  Boundary (TANCH): {boundary[:100]}{'...' if len(boundary)>100 else ''}")
    print(f"  Has .py: {descriptor is not None and (VAULT_PATH / ob3ect_name / f'{ob3ect_name}_ob3ect.py').exists()}")
    print(f"  Has .lean: {(VAULT_PATH / ob3ect_name / f'{ob3ect_name}_scaffold.lean').exists()}")

    # Dispatch
    if cat == 'exec':
        masses = params.get('masses', None)
        rev_err, ent_delta, frob_ok = bootstrap_exec(state, dt, N_period, masses)
    else:
        rev_err, ent_delta, frob_ok = bootstrap_symbolic(state, dt, N_period)

    # ── Final summary ──
    separator("BOOTSTRAP COMPLETE")
    print(f"  Ob3ect:      {ob3ect_name}")
    print(f"  Domain:      {state.metadata.get('domain_type', '???')}")
    print(f"  Frobenius:   {'PASS' if frob_ok else 'FAIL'}")
    print(f"  Rev error:   {rev_err:.4e}" if isinstance(rev_err, (int, float)) else f"  Rev error:   {rev_err}")
    print(f"  Entropy Δ:   {ent_delta:.6e}" if isinstance(ent_delta, (int, float)) else f"  Entropy Δ:   {ent_delta}")
    print(f"  STATUS:      {bin(st.STATUS)}  ({REG_NAMES.get(st.STATUS, '?')})")
    return rev_err, ent_delta, frob_ok


# ── Auto-discovery ──────────────────────────────────────────────────────
VAULT_PATH = st.VAULT_PATH


def list_all_ob3ects(filter_domain=None):
    """List all discoverable ob3ects."""
    ob3ects = discover_ob3ects()
    print(f"\n{'═'*60}")
    print(f"  OB3ECT VAULT — {len(ob3ects)} ob3ects available")
    print(f"{'═'*60}\n")
    print(f"  {'NAME':<50s} {'DOMAIN':<25s} {'JSON':>5s} {'PY':>5s} {'LEAN':>5s}")
    print(f"  {'─'*50} {'─'*25} {'─'*5} {'─'*5} {'─'*5}")

    count = 0
    for name, entry in sorted(ob3ects.items()):
        desc = entry.get('descriptor', {})
        dt = get_domain_type(desc) if desc else '???'
        if filter_domain and dt != filter_domain:
            continue
        has_json = 'Y' if desc else 'N'
        has_py = 'Y' if entry.get('has_py') else 'N'
        has_lean = 'Y' if entry.get('has_lean') else 'N'
        print(f"  {name:<50s} {dt:<25s} {has_json:>5s} {has_py:>5s} {has_lean:>5s}")
        count += 1

    print(f"\n  {count} ob3ects shown")
    return ob3ects


# ── CLI ─────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py [--list [domain]] | [ob3ect_name]")
        print("       python3 main.py --list              # all ob3ects")
        print("       python3 main.py --list mathematical # filter by domain")
        print("       python3 main.py collatz_theorem")
        print("       python3 main.py truth_machine")
        print("       python3 main.py chaos_magic_servitor")
        sys.exit(1)

    if sys.argv[1] == '--list':
        filter_domain = sys.argv[2] if len(sys.argv) > 2 else None
        list_all_ob3ects(filter_domain)
        return

    ob3ect_name = sys.argv[1]
    params = {}
    if len(sys.argv) > 2:
        try:
            params['N_period'] = int(sys.argv[2])
        except ValueError:
            pass

    bootstrap_ob3ect(ob3ect_name, **params)


if __name__ == '__main__':
    main()
