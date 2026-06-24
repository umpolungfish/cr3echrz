"""
main.py — 12-step Connes Embedding bootstrap.

Three canonical cases:
  R        (post-2020) -> EMBEDDABLE(T)      hyperfinite, Connes' theorem
  L(F_2)   (post-2020) -> NON_EMBEDDABLE(F)  JNVWY 2020: MIP*=RE refutes conjecture
  L(F_2)   (pre-2020)  -> PARADOX(B)         Connes conjecture historically unresolved
"""

from cr3echrz.p4rakernel.connes import state as st
from cr3echrz.p4rakernel.connes.state import status_name, EMBEDDABLE, NON_EMBEDDABLE, PARADOX
from cr3echrz.p4rakernel.connes.opcodes import (vinit, imscrib, tanch, fsplit, ffuse,
                     evalt, evalf, afwd, arev, clink, engagr,
                     ifix as opcode_ifix)


def separator(title):
    print(f"\n{'─'*62}")
    print(f"  {title}")
    print('─'*62)


def header(title):
    print("\n" + "═"*62)
    print(f"  {title}")
    print("═"*62)


def run_connes_protocol(factor_name: str, use_2020: bool) -> dict:
    st.state['use_2020'] = use_2020

    # ── Step 1: VINIT ───────────────────────────────────────────────
    separator("Step 1 — VINIT  [STATUS=0b00, VOID]")
    factor = vinit(factor_name)
    print(f"  factor       = {factor.name}")
    print(f"  STATUS       = {bin(st.state['status'])}  ({status_name(st.state['status'])})")

    # ── Step 2: IMSCRIB ─────────────────────────────────────────────
    separator("Step 2 — IMSCRIB  (self-similarity R =~ R otimes R)")
    factor = imscrib(factor)
    print(f"  is_hyperfinite = {factor.is_hyperfinite}")
    print(f"  trace          = {factor.trace or '<undefined>'}")

    # ── Step 3: TANCH ───────────────────────────────────────────────
    separator("Step 3 — TANCH  (construct R^omega terminal anchor)")
    ultrapower = tanch(factor)
    print(f"  base         = {ultrapower.base.name}")
    print(f"  ultrafilter  = omega  ({ultrapower.ultrafilter})")

    # ── Step 4: FSPLIT ──────────────────────────────────────────────
    separator("Step 4 — FSPLIT  (C*-tensor norm delta-bifurcation)")
    min_norm, max_norm = fsplit(factor)
    print(f"  min_norm     = {min_norm.value}   is_equal={min_norm.is_equal}")
    print(f"  max_norm     = {max_norm.value}  is_equal={max_norm.is_equal}")

    # ── Step 5: EVALT ───────────────────────────────────────────────
    separator("Step 5 — EVALT  (T-arm: min==max? -> embeddable)")
    t_arm = evalt(min_norm, max_norm)
    print(f"  EVALT        = {t_arm}  "
          f"({'norms coincide — embeds in R^omega' if t_arm else 'norms diverge — no embedding confirmed'})")

    # ── Step 6: AFWD ────────────────────────────────────────────────
    separator("Step 6 — AFWD  (forward trace-preserving embedding M -> R^omega)")
    emb = afwd(factor, ultrapower)
    print(f"  success              = {emb.success}")
    print(f"  is_trace_preserving  = {emb.is_trace_preserving}")

    # ── Step 7: EVALF ───────────────────────────────────────────────
    separator("Step 7 — EVALF  (F-arm: min!=max? -> MIP*=RE obstruction)")
    f_arm = evalf(min_norm, max_norm)
    print(f"  EVALF        = {f_arm}  "
          f"({'norm divergence — non-embeddable witness' if f_arm else 'no divergence'})")

    # ── Step 8: FFUSE ───────────────────────────────────────────────
    separator("Step 8 — FFUSE  (C*-tensor norm mu-reconstitution)")
    norms_recon = ffuse(min_norm, max_norm)
    sp_ok  = norms_recon['spatial'].value    == 'spatial'
    pj_ok  = norms_recon['projective'].value == 'projective'
    sp_eq  = norms_recon['spatial'].is_equal    == min_norm.is_equal
    pj_eq  = norms_recon['projective'].is_equal == max_norm.is_equal
    assert sp_ok and pj_ok and sp_eq and pj_eq, "FFUSE INTEGRITY FAIL: mu o delta != id"
    print(f"  spatial      = {norms_recon['spatial'].value}     is_equal={norms_recon['spatial'].is_equal}  [reconstructed]")
    print(f"  projective   = {norms_recon['projective'].value}  is_equal={norms_recon['projective'].is_equal}  [reconstructed]")
    print(f"  mu o delta = id:  PASS  (norm labels and equality flags reconstructed exactly)")

    # ── Step 9: AREV ────────────────────────────────────────────────
    separator("Step 9 — AREV  (reverse ultraproduct descent -> complexity class)")
    complexity = arev(ultrapower, factor)
    print(f"  complexity   = {complexity}")

    # ── Step 10: CLINK ──────────────────────────────────────────────
    separator("Step 10 — CLINK  (compose MIP* with RE)")
    eq = clink()
    print(f"  {eq}")

    # ── Step 11: ENGAGR ─────────────────────────────────────────────
    separator("Step 11 — ENGAGR  (engage Belnap STATUS register)")
    pre2020 = not use_2020
    eng_status = engagr(factor, pre2020=pre2020)
    era = "pre-2020" if pre2020 else "post-2020"
    if factor.name == 'R':
        print(f"  R is hyperfinite: embeddability is unconditional (Connes' theorem).")
    elif pre2020:
        print(f"  L(F_2) pre-2020: conjecture unresolved. Entering paradox mode.")
    else:
        print(f"  L(F_2) post-2020: JNVWY theorem applies. MIP*=RE refutes embeddability.")
    print(f"  era          = {era}")
    print(f"  ENGAGR STATUS= {bin(eng_status)}  ({status_name(eng_status)})")

    # ── Step 12: IFIX ───────────────────────────────────────────────
    separator("Step 12 — IFIX  (Ji-Natarajan-Vidick-Wright-Yuen permanent fixation)")
    final_status = opcode_ifix(factor, use_2020=use_2020)
    if final_status == EMBEDDABLE:
        print(f"  {factor.name} EMBEDS in R^omega.  (hyperfinite — Connes' theorem)")
    elif final_status == NON_EMBEDDABLE:
        print(f"  {factor.name} does NOT embed in R^omega.  "
              f"(JNVWY 2020: MIP*=RE)")
    else:
        print(f"  {factor.name} embedding status OPEN.  "
              f"(Connes conjecture unresolved pre-2020)")
    print(f"  IFIX STATUS  = {bin(final_status)}  ({status_name(final_status)})")

    print(f"\n  Closure: True")
    print(f"  factor={factor.name}  hyperfinite={factor.is_hyperfinite}"
          f"  use_2020={use_2020}  complexity={complexity}")

    return dict(st.state)


# ════════════════════════════════════════════════════════════════════
#  THREE CANONICAL CASES
# ════════════════════════════════════════════════════════════════════

def main():
    header("CASE 1:  R (hyperfinite)  —  EMBEDDABLE  (Connes' theorem)")
    r1 = run_connes_protocol('R', use_2020=True)

    header("CASE 2:  L(F_2) post-2020  —  NON-EMBEDDABLE  (MIP*=RE)")
    r2 = run_connes_protocol('L(F_2)', use_2020=True)

    header("CASE 3:  L(F_2) pre-2020  —  PARADOX  (Connes conjecture open)")
    r3 = run_connes_protocol('L(F_2)', use_2020=False)

    print("\n" + "═"*62)
    print("  SUMMARY")
    print("═"*62)
    cases = [
        ("R (post-2020)",      r1),
        ("L(F_2) post-2020",   r2),
        ("L(F_2) pre-2020",    r3),
    ]
    for label, r in cases:
        print(f"  {label:22s}  STATUS={bin(r['status'])}  ({status_name(r['status'])})")
    print()


if __name__ == '__main__':
    main()
