#!/usr/bin/env python3
"""
frobenius.py — Frobenius verification: μ∘δ = id

Tracks FSPLIT/FFUSE pairs and verifies the recomposition identity.
For each operationalization, every split/fuse pair must satisfy:

    FFUSE(FSPLIT(x)) == x

This is the universal structural invariant ensuring the operationalization
is information-conserving and dialetheically sound.

Author: Lando⊗⊙perator
"""
from typing import Any, List, Tuple


class FrobeniusVerifier:
    """Verification of μ∘δ = id at every FSPLIT/FFUSE pair."""

    def __init__(self, tol: float = 1e-12):
        self.tol = tol
        self.pair_count: int = 0
        self.verifications: List[Tuple[int, bool, str, str]] = []

    def verify(self, original: Any, reconstructed: Any, tol: float = None) -> bool:
        """Verify μ∘δ = id for one FSPLIT/FFUSE pair.

        Handles nested structures (lists of lists of floats) with tolerance
        for floating-point comparisons.
        """
        if tol is None:
            tol = self.tol
        self.pair_count += 1
        ok = self._approx_equal(original, reconstructed, tol)
        self.verifications.append(
            (self.pair_count, ok, str(original)[:120], str(reconstructed)[:120])
        )
        return ok

    @staticmethod
    def _approx_equal(a: Any, b: Any, tol: float = 1e-12) -> bool:
        """Recursive approximate equality for nested structures."""
        if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
            if len(a) != len(b):
                return False
            return all(
                FrobeniusVerifier._approx_equal(ai, bi, tol)
                for ai, bi in zip(a, b)
            )
        elif isinstance(a, float) and isinstance(b, float):
            if a == b:
                return True
            return abs(a - b) < tol
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return abs(float(a) - float(b)) < tol
        else:
            return a == b

    def all_pass(self) -> bool:
        return all(v[1] for v in self.verifications)

    def passing_count(self) -> int:
        return sum(1 for v in self.verifications if v[1])

    def report(self) -> str:
        lines = [
            f"Frobenius Verifier: {self.passing_count()}/{len(self.verifications)} passing"
        ]
        for idx, ok, orig, recon in self.verifications:
            status = "PASS" if ok else "FAIL"
            lines.append(f"  Pair {idx}: {status}")
            if not ok:
                lines.append(f"    Original:      {orig}")
                lines.append(f"    Reconstructed: {recon}")
        return "\n".join(lines)

    def summary(self) -> dict:
        return {
            "pairs": self.pair_count,
            "passing": self.passing_count(),
            "all_pass": self.all_pass(),
        }
