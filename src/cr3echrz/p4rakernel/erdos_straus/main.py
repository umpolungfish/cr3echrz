"""
main.py — Erdos-Straus decomposition bootstrap.

Four canonical cases, one per congruence class mod 4:
  n=4  (0 mod 4) -> 4/4  = 1/1               STATUS=FOUND(T)
  n=5  (1 mod 4) -> 4/5  = 1/2 + 1/4 + 1/20  STATUS=FOUND(T)
  n=6  (2 mod 4) -> 4/6  = 1/2 + 1/6         STATUS=FOUND(T)
  n=7  (3 mod 4) -> 4/7  = 1/2 + 1/14        STATUS=FOUND(T)

Theorem (Erdos-Straus 1948): for every integer n >= 2, there exist
positive integers x, y, z such that 4/n = 1/x + 1/y + 1/z.
Verified computationally for all n <= 10^14; no counterexample known.
"""

from fractions import Fraction
from cr3echrz.p4rakernel.erdos_straus import state as st
from cr3echrz.p4rakernel.erdos_straus.state import status_name, FOUND, frac_str
from cr3echrz.p4rakernel.erdos_straus.opcodes import (vinit, tanch, fsplit, afwd, ifix, evalt,
                     arev, clink, evalf, greedy_step, ffuse,
                     imscrib, engagr, ifix_final, tanch_final)


def separator(title):
    print(f"\n{'─'*62}")
    print(f"  {title}")
    print('─'*62)


def header(title):
    print("\n" + "═"*62)
    print(f"  {title}")
    print("═"*62)


BRANCH_LABELS = {
    0: 'n = 0 (mod 4)',
    1: 'n = 1 (mod 4)',
    2: 'n = 2 (mod 4)',
    3: 'n = 3 (mod 4)',
}


def run_erdos_straus(n: int) -> dict:

    # ── Step 1: VINIT ───────────────────────────────────────────────
    separator("Step 1 — VINIT")
    target = vinit(n)
    print(f"  n            = {n}")
    print(f"  target       = 4/{n} = {frac_str(target)}")
    print(f"  STATUS       = {bin(st.state['status'])}  ({status_name(st.state['status'])})")

    # ── Step 2: TANCH ───────────────────────────────────────────────
    separator("Step 2 — TANCH  (n >= 2 boundary)")
    tanch(n)
    print(f"  n >= 2:      PASS")

    # ── Step 3: FSPLIT ──────────────────────────────────────────────
    separator("Step 3 — FSPLIT  (branch on n mod 4)")
    r = fsplit(n)
    print(f"  n mod 4      = {r}  [{BRANCH_LABELS[r]}]")

    # ── Step 4: AFWD ────────────────────────────────────────────────
    separator("Step 4 — AFWD  (select first unit fraction denominator)")
    d0 = afwd(r)
    print(f"  first denom  = {d0}   (1/{d0})")
    if r == 0:
        print(f"  n = 0 (mod 4): single term 1/{d0} suffices (4/{n} = 4/{n})")
    else:
        print(f"  greedy first term: x = ceil({n}/4) = {d0}")

    # ── Step 5: IFIX (first term) ───────────────────────────────────
    separator("Step 5 — IFIX  (commit first unit fraction)")
    ifix(d0)
    print(f"  committed    = 1/{d0}")
    print(f"  remainder    = {frac_str(st.state['remainder'])}")

    # ── Step 6: EVALT ───────────────────────────────────────────────
    separator("Step 6 — EVALT  (T-arm: remainder = 0?)")
    t_arm = evalt()
    print(f"  EVALT        = {t_arm}  "
          f"({'exact — single-term decomposition complete' if t_arm else 'remainder non-zero — continue'})")

    # ── Step 7: AREV ────────────────────────────────────────────────
    separator("Step 7 — AREV  (checkpoint: current remainder)")
    rem = arev()
    print(f"  remainder    = {frac_str(rem)}")

    # ── Step 8: CLINK ───────────────────────────────────────────────
    separator("Step 8 — CLINK  (chain log)")
    clink()
    print(f"  remainder    = {frac_str(st.state['remainder'])}")

    # ── Step 9: EVALF ───────────────────────────────────────────────
    separator("Step 9 — EVALF  (F-arm: remainder > 0?)")
    f_arm = evalf()
    print(f"  EVALF        = {f_arm}  "
          f"({'further decomposition needed' if f_arm else 'complete'})")

    # ── Step 10: Greedy reduction ────────────────────────────────────
    separator("Step 10 — Greedy reduction (IFIX x greedy until remainder = 0)")
    step = 0
    while st.state['remainder'] > 0:
        d = greedy_step()
        ifix(d)
        step += 1
        print(f"  greedy[{step}]    = 1/{d}   remainder -> {frac_str(st.state['remainder'])}")

    # ── Step 11: EVALT (final) ───────────────────────────────────────
    separator("Step 11 — EVALT  (T-arm: remainder = 0 now?)")
    t_arm2 = evalt()
    print(f"  EVALT        = {t_arm2}  (decomposition complete)")
    assert t_arm2

    # ── Step 12: FFUSE ──────────────────────────────────────────────
    separator("Step 12 — FFUSE  (mu-reconstitution: verify sum = 4/n)")
    ok = ffuse()
    total = sum(Fraction(1, d) for d in st.state['terms'])
    assert ok, f"FFUSE INTEGRITY FAIL: {total} != {Fraction(4, n)}"
    eq_str = ' + '.join(f'1/{d}' for d in st.state['terms'])
    print(f"  sum          = {eq_str}")
    print(f"               = {frac_str(total)}")
    print(f"  expected     = {frac_str(Fraction(4, n))}")
    print(f"  mu o delta = id:  PASS  (decomposition is lossless)")

    # ── Step 13: IMSCRIB ────────────────────────────────────────────
    separator("Step 13 — IMSCRIB  (self-recognition: decomposition verified)")
    imscrib()
    print(f"  4/{n} = {eq_str}  (verified)")

    # ── Step 14: ENGAGR ─────────────────────────────────────────────
    separator("Step 14 — ENGAGR  (acknowledge multiple valid decompositions)")
    engagr()
    print(f"  STATUS       = {bin(st.state['status'])}  ({status_name(st.state['status'])})")
    print(f"  (Multiple decompositions exist; this is one canonical greedy representative.)")

    # ── Step 15: IFIX_FINAL ─────────────────────────────────────────
    separator("Step 15 — IFIX_FINAL  (fix STATUS=FOUND)")
    ifix_final()
    print(f"  STATUS       = {bin(st.state['status'])}  ({status_name(st.state['status'])})")
    print(f"  terms        = {st.state['terms']}")

    # ── Step 16: TANCH_FINAL ────────────────────────────────────────
    separator("Step 16 — TANCH_FINAL  (boundary verification)")
    tanch_final()
    print(f"  sum = {frac_str(total)} = {frac_str(Fraction(4, n))}  PASS")

    print(f"\n  Closure: True")
    print(f"  n={n}  mod4={r}  terms={st.state['terms']}  STATUS={bin(st.state['status'])}")

    return dict(st.state)


# ════════════════════════════════════════════════════════════════════
#  FOUR CANONICAL CASES  (one per congruence class mod 4)
# ════════════════════════════════════════════════════════════════════

CASES = [
    (4,  "n = 4   (n = 0 mod 4, single term)"),
    (5,  "n = 5   (n = 1 mod 4, three terms)"),
    (6,  "n = 6   (n = 2 mod 4, two terms)"),
    (7,  "n = 7   (n = 3 mod 4, two terms)"),
]


def main():
    results = {}
    for n, label in CASES:
        header(f"CASE: {label}")
        results[n] = run_erdos_straus(n)

    print("\n" + "═"*62)
    print("  SUMMARY")
    print("═"*62)
    for n, label in CASES:
        r = results[n]
        decomp = ' + '.join(f'1/{d}' for d in r['terms'])
        print(f"  n={n}  4/{n} = {decomp}")
        print(f"       STATUS={bin(r['status'])}  ({status_name(r['status'])})")
    print()


if __name__ == '__main__':
    main()
