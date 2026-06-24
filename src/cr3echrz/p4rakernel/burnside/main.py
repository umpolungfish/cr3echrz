"""
main.py — 13-step Burnside bootstrap orchestration.

Mirrors the three-body bootstrap structure exactly.
Run:  python main.py
"""

from cr3echrz.p4rakernel.burnside.rewriting import burnside_reduce, free_reduce, primitive_root
from cr3echrz.p4rakernel.burnside.opcodes import (vinit, afwd, arev, clink, tanch,
                       fsplit, ffuse, evalt, evalf,
                       imscrib, engagr, ifix)
from cr3echrz.p4rakernel.burnside import state as st
from cr3echrz.p4rakernel.burnside.state import word_str, status_name


def separator(title):
    print(f"\n{'─'*62}")
    print(f"  {title}")
    print('─'*62)


def run_burnside_protocol(m: int, n: int, seed_word: tuple) -> dict:
    """
    Execute the 13-step Burnside bootstrap for B(m,n) on seed_word.
    Returns the final state dict.
    """
    st.state['m'] = m
    st.state['n'] = n

    # ── Step 1: VINIT ───────────────────────────────────────────────
    separator("Step 1 — VINIT  [STATUS=0b00, VOID]")
    w = vinit()
    print(f"  word         = {word_str(w)}")
    print(f"  STATUS       = {bin(st.state['status'])}  ({status_name(st.state['status'])})")

    # ── Step 2: Seed the word tape ──────────────────────────────────
    separator("Step 2 — Seed word tape (free reduction)")
    w = free_reduce(seed_word)
    print(f"  seed_word    = {seed_word}")
    print(f"  free-reduced = {word_str(w)}")

    # ── Step 3: AREV — append inverse of generator 1 ───────────────
    separator("Step 3 — AREV (append a1⁻¹)")
    w = arev(w, 1)
    print(f"  word         = {word_str(w)}")

    # ── Step 4: CLINK — concatenate with identity ───────────────────
    separator("Step 4 — CLINK (compose with e)")
    w = clink(w, ())
    print(f"  word         = {word_str(w)}")

    # ── Step 5: TANCH — impose x^n=1 ───────────────────────────────
    separator(f"Step 5 — TANCH (Burnside reduction: x^{n}=1)")
    w_pre = w
    w = tanch(w, n)
    reduced = True if w != w_pre else False
    print(f"  before       = {word_str(w_pre)}")
    print(f"  after        = {word_str(w)}")
    print(f"  reduced      = {reduced}")
    print(f"  |w|          = {len(w)}")

    # ── Step 6: FSPLIT — Adian δ-decomposition ─────────────────────
    separator("Step 6 — FSPLIT  (Adian δ-decomposition)")
    periodics, bridges = fsplit(w)
    print(f"  periodics    = {[word_str(p) for p in periodics] or ['—']}")
    print(f"  bridges      = {[word_str(b) for b in bridges]   or ['—']}")
    print(f"  |periodics|  = {len(periodics)}, |bridges| = {len(bridges)}")

    # ── Step 7: EVALT — T-arm: local finiteness ────────────────────
    separator("Step 7 — EVALT  (T-arm: periodic segments locally finite?)")
    t_arm = evalt(periodics, n)
    if periodics:
        roots = [word_str(primitive_root(p)) for p in periodics]
        print(f"  primitive roots = {roots}")
    print(f"  EVALT        = {t_arm}  ({'locally finite' if t_arm else 'FAILS local finiteness'})")

    # ── Step 8: EVALF — F-arm: aperiodic residuals ─────────────────
    separator("Step 8 — EVALF  (F-arm: aperiodic residuals in bridges?)")
    f_arm = evalf(bridges, n)
    print(f"  EVALF        = {f_arm}  "
          f"({'aperiodic residual detected — potential ∞-order obstruction' if f_arm else 'no aperiodic residuals'})")

    # ── Step 9: FFUSE — Adian μ-reconstruction ──────────────────────
    separator("Step 9 — FFUSE  (Adian μ-reconstruction)")
    w_recon = ffuse(periodics, bridges)
    assert w_recon == w, (
        f"FFUSE INTEGRITY FAIL: got {w_recon!r}, expected {w!r}"
    )
    print(f"  reconstructed = {word_str(w_recon)}")
    print(f"  μ∘δ = id:     PASS  (||w_recon - w|| = 0)")

    # ── Step 10: IMSCRIB — is w the identity? ───────────────────────
    separator("Step 10 — IMSCRIB  (self-recognition: w =? e in B(m,n))")
    is_id = imscrib(w_recon, n)
    st.state['history'].append(w_recon)
    print(f"  word         = {word_str(w_recon)}")
    print(f"  = identity?  = {is_id}")

    # ── Step 11: ENGAGR — engage paradox register ───────────────────
    separator("Step 11 — ENGAGR  (engage Belnap STATUS register)")
    eng_status = engagr(n)
    print(f"  exponent n   = {n}")
    if n in st.FINITE_EXPONENTS:
        print(f"  n={n} is a known-finite exponent (Burnside/Sanov/Hall).")
    elif n % 2 == 1 and n >= st.INFINITE_THRESHOLD:
        print(f"  n={n} is odd ≥ {st.INFINITE_THRESHOLD}: Novikov-Adian → INFINITE.")
    else:
        print(f"  n={n} is unresolved. Entering paradox mode: "
              f"B(m,{n}) is BOTH finite AND infinite until proven otherwise.")
    print(f"  ENGAGR STATUS= {bin(eng_status)}  ({status_name(eng_status)})")

    # ── Step 12: IFIX — permanent fixation ──────────────────────────
    separator("Step 12 — IFIX  (Novikov-Adian permanent fixation)")
    fixed_status = ifix(n)
    if fixed_status == st.FINITE:
        print(f"  B(m,{n}) is FINITE.  (Theorem: Burnside 1902 / Sanov 1940 / Hall 1958)")
    elif fixed_status == st.INFINITE:
        print(f"  B(m,{n}) is INFINITE. (Theorem: Novikov-Adian 1968, odd n ≥ {st.INFINITE_THRESHOLD})")
    else:
        print(f"  B(m,{n}) status is an OPEN PROBLEM.")
    print(f"  IFIX STATUS  = {bin(fixed_status)}  ({status_name(fixed_status)})")

    # ── Step 13: Final IMSCRIB — close the proof ────────────────────
    separator("Step 13 — Final IMSCRIB  (protocol closure)")
    final_status = st.state['status']
    print(f"  STATUS       = {bin(final_status)}  ({status_name(final_status)})")
    if final_status == st.PARADOX:
        print(f"  The 4-2-1 equivalent paradox: B(m,{n}) holds both"
              f" finite and infinite topology until proven otherwise.")
    elif final_status == st.FINITE:
        print(f"  Closure: B(m,{n}) is finite. Word problem decidable.")
    elif final_status == st.INFINITE:
        print(f"  Closure: B(m,{n}) is infinite. Non-trivial elements of infinite order exist.")

    print(f"\n  Closure: True")
    print(f"  word  = {word_str(w_recon)}")
    print(f"  m={m}, n={n}, |w|={len(w_recon)}, is_id={is_id}")

    return dict(st.state)


# ════════════════════════════════════════════════════════════════════
#  THREE CANONICAL CASES
# ════════════════════════════════════════════════════════════════════

def header(title):
    print("\n" + "═"*62)
    print(f"  {title}")
    print("═"*62)


if __name__ == '__main__':

    # ── Case 1: n=3  (FINITE — Burnside 1902) ──────────────────────
    header("CASE 1:  B(2,3)  —  FINITE  (Burnside 1902)")
    r1 = run_burnside_protocol(m=2, n=3, seed_word=(1, 2, -1, -2))

    # ── Case 2: n=665  (INFINITE — Novikov-Adian) ──────────────────
    header("CASE 2:  B(2,665)  —  INFINITE  (Novikov-Adian 1968)")
    r2 = run_burnside_protocol(m=2, n=665, seed_word=(1, 2, 1, 2))

    # ── Case 3: n=5  (PARADOX — open problem) ──────────────────────
    header("CASE 3:  B(2,5)  —  PARADOX  (open problem)")
    r3 = run_burnside_protocol(
        m=2, n=5,
        seed_word=(1, 2, 1, 2, 1, 2, 3, -3, -1, -2)
    )

    # ── Summary ────────────────────────────────────────────────────
    print("\n" + "═"*62)
    print("  SUMMARY")
    print("═"*62)
    for case, r in [("B(2,3)",  r1), ("B(2,665)", r2), ("B(2,5)",  r3)]:
        print(f"  {case:10s}  STATUS={bin(r['status'])}  "
              f"({status_name(r['status'])})")
    print()
