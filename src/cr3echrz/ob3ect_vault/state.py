#!/usr/bin/env python3
"""
state.py — VINIT, IMSCRIB, Belnap status register, and ob3ect loader

Loads any ob3ect from ob3ect/digital/.vault/ by name. Each ob3ect's
.json descriptor provides the IMASM opcode assignments (Phase 1).
The state vector X carries the ob3ect's runtime data.

Domain types and their state representations:
  mathematical    — numerical state (scalar, vector, or tuple)
  computational   — Belnap register + token stack
  physical        — phase-space vector (positions + momenta)
  symbolic*       — Belnap register + symbolic token (magical, divinatory,
                     alchemical, mystical, gnostic, ceremonial, ritual,
                     shamanic, poetic, theological, etc.)

Author: Lando⊗⊙perator
"""
import json, os, sys, re
import numpy as np
import sys as _sys, os as _os
from cr3echrz.shared import BelnapRegister, FrobeniusVerifier
from typing import Any, Dict, List, Tuple, Optional
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
VAULT_PATH = Path("/home/mrnob0dy666/imsgct/ob3ect/digital/.vault")

# ═══════════════════════════════════════════════════════════════════════
#  BELNAP FOUR STATUS REGISTER
# ═══════════════════════════════════════════════════════════════════════

STATUS = 0b00
VOID  = 0b00; TRUE  = 0b01; FALSE = 0b10; BOTH  = 0b11
REG_NAMES = {VOID: "VO⌀", TRUE: "T", FALSE: "F", BOTH: "B⬡"}

# ═══════════════════════════════════════════════════════════════════════
#  DOMAIN CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════

EXEC_DOMAINS = {
    'mathematical', 'computational', 'physical', 'algebraic',
    'geometric', 'algebraic-geometric', 'topological', 'formal',
    'proof', 'proofs', 'witness', 'witnesses_and_proofs',
    'witnesses and proofs', 'ontological', 'ontic',
}

SYMBOLIC_DOMAINS = {
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
    dt = domain_type.lower().strip()
    if dt in EXEC_DOMAINS: return 'exec'
    if dt in SYMBOLIC_DOMAINS: return 'symbolic'
    return 'symbolic'

# ═══════════════════════════════════════════════════════════════════════
#  OB3ECT DISCOVERY & LOADING
# ═══════════════════════════════════════════════════════════════════════

def discover_ob3ects() -> Dict[str, Dict]:
    ob3ects = {}
    for d in sorted(VAULT_PATH.iterdir()):
        if not d.is_dir() or d.name.startswith('.') or d.name.startswith('_'):
            continue
        json_path = d / f"{d.name}_ob3ect.json"
        py_path = d / f"{d.name}_ob3ect.py"
        lean_path = d / f"{d.name}_scaffold.lean"
        entry = {'name': d.name, 'dir': str(d), 'has_py': py_path.exists(),
                 'has_lean': lean_path.exists(), 'descriptor': None}
        if json_path.exists():
            try:
                with open(json_path) as f:
                    entry['descriptor'] = json.load(f)
            except Exception: pass
        elif py_path.exists():
            entry['descriptor'] = _synthetic_descriptor(d.name, py_path)
        ob3ects[d.name] = entry
    return ob3ects


def load_ob3ect(name: str) -> Optional[Dict]:
    d = VAULT_PATH / name
    if not d.is_dir(): return None
    json_path = d / f"{name}_ob3ect.json"
    if json_path.exists():
        with open(json_path) as f: return json.load(f)
    py_path = d / f"{name}_ob3ect.py"
    if py_path.exists(): return _synthetic_descriptor(name, py_path)
    return None


def _synthetic_descriptor(name: str, py_path) -> Dict:
    """Generate a minimal descriptor from a .py ob3ect's docstring."""
    try:
        with open(py_path) as f: content = f.read()
    except Exception: return _fallback_descriptor(name)
    ig_match = re.search(r'(?:IG Type|ig_type).*?[⟨<](.+?)[⟩>]', content)
    ouro_match = re.search(r'(?:Ouroboricity|ouroboricity).*?(O[_∞₀₁₂†]+)', content)
    desc_match = re.search(r'"""\n(.+?)(?:\n\n|\n""")', content, re.DOTALL)
    if not desc_match:
        desc_match = re.search(r'""".*?\n(.+?)(?:\n|""")', content, re.DOTALL)
    steps_match = re.search(r'steps\s*=\s*\[(.+?)\]', content)
    desc_text = desc_match.group(1).strip() if desc_match else f"Ob3ect: {name}"
    ig_tuple = ig_match.group(1).strip() if ig_match else "???"
    ouro = ouro_match.group(1) if ouro_match else "O?"
    domain_type = _infer_domain(name, ig_tuple, content)
    opcodes = ['VINIT', 'TANCH', 'AFWD', 'AREV', 'CLINK', 'IMSCRIB',
               'FSPLIT', 'FFUSE', 'EVALT', 'EVALF', 'ENGAGR', 'IFIX']
    step_list = []
    if steps_match:
        step_list = [s.strip() for s in steps_match.group(1).split(',')]
    phase1 = {}
    for i, op in enumerate(opcodes):
        element = step_list[i] if i < len(step_list) else f"{op}_generic"
        phase1[op] = {"opcode": op, "chosen_element": element,
                      "justification": "Auto-extracted from .py ob3ect",
                      "rejected_candidates": []}
    return {
        "name": name, "is_valid_ob3ect": True,
        "phases": {
            "phase_0": {"domain_name": name, "domain_type": domain_type,
                        "scope": "local", "surface_tokens": [name],
                        "boundary_condition": desc_text,
                        "justification": "Synthetic descriptor from .py ob3ect"},
            "phase_1": phase1,
            "phase_2": {"split_element": "decomposition", "fuse_element": "recomposition",
                        "frobenius_verdict": "PASS"},
            "phase_3": {"entropy_assertion": "ΔS ≅ 0"}
        },
        "_synthetic": True, "_ig_type": ig_tuple, "_ouroboricity": ouro
    }


def _infer_domain(name: str, ig_tuple: str, content: str) -> str:
    n = name.lower()
    if any(kw in n for kw in ['theorem', 'proof', 'conjecture', 'lemma',
            'galois', 'monad', 'hopf', 'topos', 'yoneda', 'sheaf', 'operad',
            'category', 'adjoint', 'presheaf', 'kanextension', 'daggercompact',
            'stoneduality', 'stringdiagram', 'linearlogic', 'homotopy', 'frobenius']):
        return 'mathematical'
    if any(kw in n for kw in ['machine', 'kernel', 'os', 'dns', 'memory',
            'protocol', 'scheduler', 'belnap', 'parakernel', 'paradox', 'imasm',
            'bootstrap', 'ch3mpiler', 'void_genesis', 'truth', 'anchor',
            'dual_bootstrap', 'linear_chain', 'empty_bootstrap', 'rom_burn',
            'chiral_pairs', 'eternal_return']):
        return 'computational'
    if any(kw in n for kw in ['quantum', 'dark_matter', 'photon', 'muon',
            'planck', 'fine_structure', 'er_epr', 'superposition',
            'qg_unified', 'universal_curvature']):
        return 'physical'
    if any(kw in n for kw in ['magic', 'sigil', 'goetic', 'pentagram',
            'chaos_magic', 'apotropaic', 'witch', 'operational_magic', 'gnostic_magic']):
        return 'magical'
    if any(kw in n for kw in ['alembic', 'alchemical', 'philosopher',
            'hermetic', 'zosimos', 'rebis']):
        return 'alchemical'
    if any(kw in n for kw in ['tarot', 'i_ching', 'geomantic', 'rune',
            'scrying', 'bibliomancy', 'lithomancy', 'necromantic', 'pendulum',
            'tasseography', 'natal_chart', 'oracular', 'divination']):
        return 'divinatory'
    if any(kw in n for kw in ['shamanic', 'sufi', 'ecstatic', 'dream',
            'kabbalistic', 'enochian', 'gnostic', 'gematria', 'shavian',
            'tibetan', 'vodou', 'mystical', 'temple']):
        return 'mystical'
    return 'computational'


def _fallback_descriptor(name: str) -> Dict:
    return {
        "name": name, "is_valid_ob3ect": True,
        "phases": {
            "phase_0": {"domain_name": name, "domain_type": "computational",
                        "scope": "local", "surface_tokens": [name],
                        "boundary_condition": "Auto-detected ob3ect boundary"},
            "phase_1": {op: {"opcode": op, "chosen_element": f"{op}_generic"}
                       for op in ['VINIT','TANCH','AFWD','AREV','CLINK','IMSCRIB',
                                   'FSPLIT','FFUSE','EVALT','EVALF','ENGAGR','IFIX']},
            "phase_2": {"frobenius_verdict": "PASS"},
            "phase_3": {"entropy_assertion": "ΔS ≅ 0"}
        }, "_synthetic": True
    }


# ═══════════════════════════════════════════════════════════════════════
#  OPCODE HELPERS
# ═══════════════════════════════════════════════════════════════════════

def get_opcode_map(descriptor: Dict) -> Dict[str, str]:
    phase1 = descriptor.get('phases', {}).get('phase_1', {})
    op_map = {}
    for op in ['VINIT', 'TANCH', 'AFWD', 'AREV', 'CLINK', 'IMSCRIB',
               'FSPLIT', 'FFUSE', 'EVALT', 'EVALF', 'ENGAGR', 'IFIX']:
        if op in phase1:
            op_map[op] = phase1[op].get('chosen_element', f'{op}_generic')
    return op_map


def get_domain_type(descriptor: Dict) -> str:
    return (descriptor.get('phases', {}).get('phase_0', {})
            .get('domain_type', '???'))


def get_boundary(descriptor: Dict) -> str:
    return (descriptor.get('phases', {}).get('phase_0', {})
            .get('boundary_condition', 'unstated'))


# ═══════════════════════════════════════════════════════════════════════
#  VINIT / IMSCRIB
# ═══════════════════════════════════════════════════════════════════════

def vinit():
    global STATUS; STATUS = VOID
    return Ob3ectState()


def imscrib(state, ob3ect_name=None, ob3ect_desc=None):
    global STATUS; STATUS = TRUE
    if ob3ect_desc:
        state.metadata['descriptor'] = ob3ect_desc
        state.metadata['domain_type'] = get_domain_type(ob3ect_desc)
        state.metadata['opcode_map'] = get_opcode_map(ob3ect_desc)
        state.metadata['boundary'] = get_boundary(ob3ect_desc)
        state.metadata['domain_cat'] = domain_category(state.metadata['domain_type'])
    if ob3ect_name:
        state.metadata['name'] = ob3ect_name
    conserved = {}
    if ob3ect_desc:
        phase2 = ob3ect_desc.get('phases', {}).get('phase_2', {})
        conserved['frobenius_verdict'] = phase2.get('frobenius_verdict', 'UNKNOWN')
        conserved['split_element'] = phase2.get('split_element', '')
        conserved['fuse_element'] = phase2.get('fuse_element', '')
        phase3 = ob3ect_desc.get('phases', {}).get('phase_3', {})
        conserved['entropy_assertion'] = phase3.get('entropy_assertion', 'ΔS ≅ 0')
    state.invariants.update(conserved)
    return state, conserved


def compute_conserved(state, masses=None):
    return state.invariants.copy()


# ═══════════════════════════════════════════════════════════════════════
#  OB3ECT STATE
# ═══════════════════════════════════════════════════════════════════════

class Ob3ectState:
    def __init__(self, X=None, metadata=None):
        self.X = X if X is not None else np.zeros(0)
        self.metadata = metadata or {}
        self.invariants = {}
        self.history = []
        self.reg = VOID
        self.token_stack = []

    def copy(self):
        s = Ob3ectState(self.X.copy() if hasattr(self.X, 'copy') else self.X,
                        dict(self.metadata))
        s.invariants = dict(self.invariants)
        s.history = list(self.history)
        s.reg = self.reg
        s.token_stack = list(self.token_stack)
        return s

    def __repr__(self):
        cat = self.metadata.get('domain_cat', '?')
        name = self.metadata.get('name', '?')
        return f"Ob3ectState(name={name}, cat={cat}, reg={REG_NAMES.get(self.reg,'?')})"


# ═══════════════════════════════════════════════════════════════════════
#  OB3ECT-SPECIFIC INITIAL CONDITIONS
# ═══════════════════════════════════════════════════════════════════════

def make_ic(ob3ect_name: str, descriptor: Optional[Dict] = None):
    if descriptor is None:
        descriptor = load_ob3ect(ob3ect_name)
    if descriptor is None:
        raise ValueError(f"Ob3ect '{ob3ect_name}' not found in vault")
    dt = get_domain_type(descriptor)
    cat = domain_category(dt)
    state = Ob3ectState()
    state.metadata['name'] = ob3ect_name
    state.metadata['domain_type'] = dt
    state.metadata['domain_cat'] = cat
    state.metadata['descriptor'] = descriptor
    state.metadata['opcode_map'] = get_opcode_map(descriptor)
    state.metadata['boundary'] = get_boundary(descriptor)
    if cat == 'exec':
        if dt == 'mathematical': _init_mathematical(state, descriptor)
        elif dt == 'computational': _init_computational(state, descriptor)
        elif dt == 'physical': _init_physical(state, descriptor)
        else: _init_generic_exec(state, descriptor)
    else:
        _init_symbolic(state, descriptor)
    return state


def _init_mathematical(state, descriptor):
    boundary = state.metadata.get('boundary', '')
    seed = _extract_seed(boundary, descriptor)
    state.X = np.array([float(seed)])
    state.metadata['seed'] = seed
    state.metadata['trajectory'] = [seed]
    state.metadata['step_count'] = 0
    state.metadata['system'] = 'mathematical'


def _init_computational(state, descriptor):
    state.X = np.array([0.0])
    state.metadata['system'] = 'computational'
    state.reg = VOID


def _init_physical(state, descriptor):
    state.X = np.zeros(6)
    state.metadata['system'] = 'physical'
    state.metadata['n_bodies'] = 2
    state.metadata['masses'] = [1.0, 1.0]


def _init_generic_exec(state, descriptor):
    state.X = np.array([0.0])
    state.metadata['system'] = 'generic_exec'


def _init_symbolic(state, descriptor):
    state.X = np.array([0.0])
    state.metadata['system'] = 'symbolic'
    state.reg = VOID
    state.token_stack = []
    phase0 = descriptor.get('phases', {}).get('phase_0', {})
    tokens = phase0.get('surface_tokens', [])
    state.metadata['surface_tokens'] = tokens


def _extract_seed(boundary: str, descriptor: Dict) -> int:
    nums = re.findall(r'\b\d+\b', boundary)
    if nums: return int(nums[0])
    phase0 = descriptor.get('phases', {}).get('phase_0', {})
    for token in phase0.get('surface_tokens', []):
        nums = re.findall(r'\b\d+\b', token)
        if nums: return int(nums[0])
    return 1


# ── Utility ────────────────────────────────────────────────────────────

def list_ob3ects(domain_filter: Optional[str] = None):
    all_obs = discover_ob3ects()
    result = []
    for name, entry in sorted(all_obs.items()):
        desc = entry.get('descriptor', {})
        dt = get_domain_type(desc) if desc else '???'
        if domain_filter and dt != domain_filter: continue
        result.append((name, dt, desc is not None, entry.get('has_py', False)))
    return result
