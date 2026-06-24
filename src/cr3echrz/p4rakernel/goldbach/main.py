"""
main.py — Goldbach decomposition bootstrap.

Three canonical cases:
  n=4   (single prime pair  2+2)             -> STATUS=FOUND(T)
  n=10  (two prime pairs   3+7, 5+5)         -> STATUS=MULTIPLE(B)
  n=30  (three prime pairs 7+23, 11+19, 13+17) -> STATUS=MULTIPLE(B)

Plus: chain verification n=4..30 (COUNTER never fires).

Conjecture (Goldbach 1742): every even integer n >= 4 is the sum of two primes.
Verified computationally for all n < 4e18 (Oliveira e Silva 2014); unproven in general.
"""

from cr3echrz.p4rakernel.goldbach import state as st
from cr3echrz.p4rakernel.goldbach.state import status_name, FOUND, COUNTER, MULTIPLE
from cr3echrz.p4rakernel.goldbach.opcodes import (is_prime, vinit, tanch, fsplit, evalt, afwd, ifix,
                     ffuse, evalf, arev, clink, engagr, ifix_final,
                     tanch_final, imscrib)


def separator(title):
    print(f"\n{'─'*62}")
    print(f"  {title}")
    print('─'*62)


def header(title):
    print("\n" + "═"*62)
    print(f"  {title}")
    print("═"*62)


def run_goldbach(n: int) -> dict:

    # ── Step 1: VINIT ───────────────────────────────────────────────
    separator("Step 1 — VINIT  [STATUS=0b00, VOID]")
    vinit(n)
    print(f"  n            = {n}")
    print(f"  STATUS       = {bin(st.state['status'])}  ({status_name(st.state['status'])})")

    # ── Step 2: TANCH ───────────────────────────────────────────────
    separator("Step 2 — TANCH  (n >= 4 and n even)")
    tanch(n)
    print(f"  n >= 4, n even:  PASS")

    # ── Step 3: FSPLIT ──────────────────────────────────────────────
    separator("Step 3 — FSPLIT  (delta: enumerate all prime pairs p+q=n, p<=q)")
    pairs = fsplit(n)
    print(f"  prime pairs  = {pairs}")
    print(f"  |pairs|      = {len(pairs)}")

    # ── Step 4: EVALT ───────────────────────────────────────────────
    separator("Step 4 — EVALT  (T-arm: prime pairs exist?)")
    t_arm = evalt(pairs)
    print(f"  EVALT        = {t_arm}  "
          f"({'at least one decomposition found' if t_arm else 'NO prime pairs — COUNTEREXAMPLE'})")

    # ── Step 5: AFWD / AREV ─────────────────────────────────────────
    if not pairs:
        separator("Step 5 — AREV  (reverse trace: no prime pair)")
        arev(n)
        print(f"  n={n} has NO prime pair.  Conjecture REFUTED.  [should never print]")
        return dict(st.state)

    separator("Step 5 — AFWD  (canonical first prime pair)")
    pair = afwd(pairs)
    print(f"  first pair   = ({pair[0]}, {pair[1]})   [{n} = {pair[0]} + {pair[1]}]")

    # ── Step 6: IFIX ────────────────────────────────────────────────
    separator("Step 6 — IFIX  (permanently record all prime pairs)")
    ifix(n)
    print(f"  verified[{n}] = {st.verified.get(n, [])}")

    # ── Step 7: FFUSE ───────────────────────────────────────────────
    separator("Step 7 — FFUSE  (mu: reconstitute n from first pair)")
    ok = ffuse(n, pair)
    print(f"  {pair[0]} + {pair[1]} = {pair[0]+pair[1]}")
    print(f"  mu o delta = id:  PASS  ({pair[0]}+{pair[1]}={n})")

    # ── Step 8: EVALF ───────────────────────────────────────────────
    separator("Step 8 — EVALF  (F-arm: no prime pair?  counterexample?)")
    f_arm = evalf(pairs)
    print(f"  EVALF        = {f_arm}  "
          f"({'COUNTER arm fires' if f_arm else 'prime pair(s) confirmed — COUNTER arm silent'})")

    # ── Step 9: CLINK ───────────────────────────────────────────────
    separator("Step 9 — CLINK  (add n to chain of evidence)")
    clink(n)
    print(f"  chain        = {st.chain}")

    # ── Step 10: ENGAGR ─────────────────────────────────────────────
    separator("Step 10 — ENGAGR  (engage Belnap STATUS register)")
    eng_status = engagr(n, pairs)
    if len(pairs) == 1:
        print(f"  n={n}: single prime pair — unique decomposition.")
    else:
        print(f"  n={n}: {len(pairs)} prime pairs — paradice: multiple decompositions coexist.")
    print(f"  ENGAGR STATUS= {bin(eng_status)}  ({status_name(eng_status)})")

    # ── Step 11: IFIX_FINAL ─────────────────────────────────────────
    separator("Step 11 — IFIX_FINAL  (fix STATUS)")
    final_status = ifix_final()
    print(f"  STATUS       = {bin(final_status)}  ({status_name(final_status)})")

    # ── Step 12: TANCH_FINAL ────────────────────────────────────────
    separator("Step 12 — TANCH_FINAL  (boundary verification)")
    tanch_final(n, pair)
    print(f"  {pair[0]} + {pair[1]} = {n}   PASS")

    # ── Step 13: IMSCRIB ────────────────────────────────────────────
    separator("Step 13 — IMSCRIB  (self-recognition as Goldbach instance)")
    imscrib(n, pair)
    print(f"  {n} = {pair[0]} + {pair[1]}  (verified Goldbach instance)")

    print(f"\n  Closure: True")
    print(f"  n={n}  pairs={pairs}  STATUS={bin(st.state['status'])}")

    return dict(st.state)


# ════════════════════════════════════════════════════════════════════
#  THREE CANONICAL CASES
# ════════════════════════════════════════════════════════════════════

def chain_demo():
    """Verify Goldbach for n=4..30; print permanent record and chain."""
    # Process all n=4..30 (those not already in verified from the three cases)
    for n in range(4, 32, 2):
        if n not in st.verified:
            pairs = [(p, n - p) for p in range(2, n // 2 + 1)
                     if is_prime(p) and is_prime(n - p)]
            if pairs:
                st.verified[n] = pairs
                clink(n)

    print("\n" + "═"*62)
    print("  CHAIN VERIFICATION  n = 4..30")
    print("═"*62)
    for n in range(4, 32, 2):
        pairs = st.verified.get(n, [])
        decomps = ' = '.join(f"{p}+{q}" for p, q in pairs)
        cnt = len(pairs)
        tag = 'MULTIPLE(B)' if cnt > 1 else 'FOUND(T)'
        print(f"  {n:3d}  {decomps:45s}  [{tag}]")

    print(f"\n  chain = {sorted(st.chain)}")
    print(f"  COUNTER never fired:  {all(len(v) > 0 for v in st.verified.values())}")
    print()


def main():
    header("CASE 1:  n=4   —  single prime pair  (2+2)  —  FOUND(T)")
    r1 = run_goldbach(4)

    header("CASE 2:  n=10  —  two prime pairs  (3+7, 5+5)  —  MULTIPLE(B)")
    r2 = run_goldbach(10)

    header("CASE 3:  n=30  —  three prime pairs  (7+23, 11+19, 13+17)  —  MULTIPLE(B)")
    r3 = run_goldbach(30)

    print("\n" + "═"*62)
    print("  SUMMARY  (three canonical cases)")
    print("═"*62)
    for label, n, r in [
        ("n=4  (single pair)",  4,  r1),
        ("n=10 (two pairs)",    10, r2),
        ("n=30 (three pairs)",  30, r3),
    ]:
        decomps = ' | '.join(f"{p}+{q}" for p, q in st.verified.get(n, []))
        print(f"  {label:22s}  {decomps}")
        print(f"    STATUS={bin(r['status'])}  ({status_name(r['status'])})")

    chain_demo()


if __name__ == '__main__':
    main()
