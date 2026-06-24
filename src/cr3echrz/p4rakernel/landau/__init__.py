"""
cr3echrz.p4rakernel.landau — Landau's Theorems

"For normalized holomorphic f on D = {|z|<1}, if f omits a finite value,
then |f'(0)| ≤ L where L ≈ 0.5433 is Landau's constant." Landau (1904).

Implements the omission dichotomy as FSPLIT, with Picard essential singularity
as the native Belnap BOTH-state (both T and F arms simultaneously active).
"""
from cr3echrz.p4rakernel.landau.main import run_landau
from cr3echrz.p4rakernel.landau.state import state, status_name, LANDAU_L, KOEBE_K, BLOCH_B, VOID, BOUNDED, UNBOUNDED, PICARD
