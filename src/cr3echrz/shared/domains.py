#!/usr/bin/env python3
"""
domains.py — Domain classification for ob3ect/theorem dispatch

Maps domain_type strings to exec/symbolic categories.
Determines whether an operationalization uses numerical state vectors
(exec domains: mathematical, physical, computational...) or symbolic
Belnap registers (symbolic domains: magical, divinatory, alchemical...).

Author: Lando⊗⊙perator
"""
from typing import Dict, Set

# ── Domain classification ────────────────────────────────────────────

EXEC_DOMAINS: Set[str] = {
    'mathematical', 'computational', 'physical', 'algebraic',
    'geometric', 'algebraic-geometric', 'topological', 'formal',
    'proof', 'proofs', 'witness', 'witnesses_and_proofs',
    'witnesses and proofs', 'ontological', 'ontic',
    'logical-physical', 'meta-mathematical', 'legal',
    'paleographic', 'hermeneutic',
}

SYMBOLIC_DOMAINS: Set[str] = {
    'magical', 'divinatory', 'alchemical', 'mystical', 'gnostic',
    'ceremonial', 'ritual', 'ritual-operational', 'ritual-cosmological',
    'shamanic', 'poetic', 'poetry', 'theological', 'sacramental',
    'spiritualist', 'oneiric', 'thermodynamic-oneiric', 'tantric',
    'cosmological', 'esoteric', 'gnostic_cosmogony', 'glyphic',
    'necromantic', 'astrological', 'psychological', 'philosophical',
    'anthropological', 'geological', 'semiotic', 'semiotic-editorial',
    'canonical', 'thermodynamic',
}


def domain_category(domain_type: str) -> str:
    """Return 'exec' or 'symbolic' for a domain type string."""
    dt = domain_type.lower().strip()
    if dt in EXEC_DOMAINS:
        return 'exec'
    if dt in SYMBOLIC_DOMAINS:
        return 'symbolic'
    return 'symbolic'


def infer_domain(name: str, ig_tuple: str = "", content: str = "") -> str:
    """Heuristically infer domain type from ob3ect name, IG tuple, and source."""
    name_lower = name.lower()

    # Check against explicit keywords
    math_keywords = ['theorem', 'conjecture', 'connes', 'collatz', 'goldbach',
                     'galois', 'kaplansky', 'burnside', 'jacobson', 'fuglede',
                     'hadamard', 'hilbert', 'köthe', 'erdos', 'straus', 'baum',
                     'herzog', 'schönheim', 'three_body', 'threebody', 'pythagorean',
                     'square', 'subspace', 'invariant']
    physical_keywords = ['quantum', 'mechanics', 'hilbert_space', 'wavefunction',
                         'particle', 'field_theory', 'gravity', 'cosmology',
                         'black_hole', 'neutrino', 'gauge', 'higgs']
    alchemical_keywords = ['alembic', 'stone', 'lapis', 'elixir', 'rebis',
                           'philosopher', 'hermetic', 'alchemical', 'phytoglyphic']
    magical_keywords = ['magic', 'servitor', 'sigil', 'goetic', 'pentagram',
                        'chaos_magic', 'apotropaic']
    computational_keywords = ['kernel', 'operating', 'compiler', 'protocol',
                              'gödel', 'incompleteness', 'proof_assistant',
                              'virtual_machine']
    divinatory_keywords = ['tarot', 'i_ching', 'hexagram', 'geomancy', 'scrying',
                           'bibliomancy', 'necromantic', 'pendulum', 'lithomancy',
                           'rune', 'futhark']

    for kw in math_keywords:
        if kw in name_lower:
            return 'mathematical'
    for kw in physical_keywords:
        if kw in name_lower:
            return 'physical'
    for kw in alchemical_keywords:
        if kw in name_lower:
            return 'alchemical'
    for kw in magical_keywords:
        if kw in name_lower:
            return 'magical'
    for kw in computational_keywords:
        if kw in name_lower:
            return 'computational'
    for kw in divinatory_keywords:
        if kw in name_lower:
            return 'divinatory'

    return 'symbolic'
