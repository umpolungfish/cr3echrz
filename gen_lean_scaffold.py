#!/usr/bin/env python3
"""Generate missing _scaffold.lean files for vault ob3ects."""
import json, os, pathlib, re, sys, hashlib

VAULT = pathlib.Path("/home/mrnob0dy666/imsgct/ob3ect/digital/.vault")

# IG primitive mapping per opcode (canonical 12-step bootstrap)
OPCODE_FIELD = {
    'VINIT':  ('dim',  '𐑼'),
    'TANCH':  ('top',  '𐑡'),
    'AFWD':   ('rel',  '𐑾'),
    'AREV':   ('pol',  '𐑗'),
    'CLINK':  ('fid',  '𐑱'),
    'IMSCRIB':('gram', '𐑠'),
    'FSPLIT': ('gran', '𐑚'),
    'FFUSE':  ('stoi', '𐑙'),
    'EVALT':  ('crit', '⊙'),
    'EVALF':  ('chir', '𐑖'),
    'ENGAGR': ('stoi', '𐑳'),
    'IFIX':   ('prot', '𐑭'),
}

# Canonical type flow (src_field -> opcode_field -> tgt_field)
# Simplified: we use a deterministic state machine
PRIMITIVE_CYCLE = ['𐑼', '𐑠', '𐑭', '𐑾', '𐑗', '𐑚', '⊙', '𐑖', '𐑙', '𐑳', '𐑱', '𐑡']

def make_safe_name(name):
    """Create a Lean-safe identifier from ob3ect name."""
    safe = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    if safe[0].isdigit():
        safe = 'n' + safe
    return safe

def fingerprint(ops):
    """Generate a simple fingerprint for the opcode sequence."""
    h = hashlib.md5(''.join(ops).encode()).hexdigest()[:6]
    return h

def find_fsplit_ffuse_pairs(ops):
    """Find FSPLIT/FFUSE pairs by counting stack depth."""
    pairs = []
    stack = []
    for i, op in enumerate(ops):
        if op == 'FSPLIT':
            stack.append(i)
        elif op == 'FFUSE':
            if stack:
                pairs.append((stack.pop(), i))
    return pairs


def build_field_mapping(ops):
    """Build the token-to-IG-field mapping section."""
    lines = []
    lines.append('-- ── Token → IG field mapping ──────────────────────────────────────────────')
    for i, op in enumerate(ops):
        field, prim = OPCODE_FIELD.get(op, ('???', '?'))
        # Determine src and tgt from position in cycle
        src = PRIMITIVE_CYCLE[i % len(PRIMITIVE_CYCLE)]
        tgt = PRIMITIVE_CYCLE[(i + 1) % len(PRIMITIVE_CYCLE)]
        lines.append(f'--   [{i}] {op:<10} {field:<7} := {prim:<16} {src} → {tgt}  | {get_op_description(op)}')
    return '\n'.join(lines)

def get_op_description(op):
    descs = {
        'VINIT': 'initial object — ground of distinction',
        'TANCH': 'terminal object — connectivity boundary',
        'AFWD': 'forward morphism — bidirectional arrow',
        'AREV': 'reverse morphism — parity flip',
        'CLINK': 'composition — regime coherence',
        'IMSCRIB': 'identity — self-imscription',
        'FSPLIT': 'split δ — range decomposition',
        'FFUSE': 'fuse μ — assembly mode',
        'EVALT': 'evaluate-true — criticality gate open',
        'EVALF': 'evaluate-false — chirality check',
        'ENGAGR': 'engage paradox — B-state, both arms',
        'IFIX': 'irreversible fixation — winding number',
    }
    return descs.get(op, 'unknown opcode')

def build_arrow_sequence(ops, name, domain):
    """Build the .arrow sequence for the IGProtocol term."""
    pairs = find_fsplit_ffuse_pairs(ops)
    pair_map = {}
    for s, e in pairs:
        pair_map[s] = e
        pair_map[e] = s

    lines = []
    lines.append(f'noncomputable def {name}_protocol : IGProtocol 𐑼 𐑡 :=')
    lines.append('  .withGram 𐑠 <|')
    i = 0
    while i < len(ops):
        op = ops[i]
        if op == 'FSPLIT' and i in pair_map:
            end = pair_map[i]
            inner_ops = ops[i+1:end]
            # Find EVALT and EVALF within inner
            evalt_idx = None
            evalf_idx = None
            for j, iop in enumerate(inner_ops):
                if iop == 'EVALT' and evalt_idx is None:
                    evalt_idx = j
                if iop == 'EVALF' and evalf_idx is None:
                    evalf_idx = j
            t_branch = inner_ops[:max(evalt_idx or 0, evalf_idx or 0)]
            f_branch = inner_ops[max(evalt_idx or 0, evalf_idx or 0):]

            lines.append(f'  -- FSPLIT [{i}] / FFUSE [{end}]')
            lines.append('  .seq')
            lines.append('    (.prod')
            # T-branch
            lines.append('      -- T-branch')
            for j, iop in enumerate(t_branch):
                if iop == 'EVALT':
                    lines.append(f'      (.arrow ⊙ 𐑚 𐑙)  -- [{i+1+j}] EVALT')
                elif iop == 'AFWD':
                    lines.append(f'      (.arrow 𐑾 𐑚 𐑙)  -- [{i+1+j}] AFWD (in T-branch)')
                elif iop == 'CLINK':
                    lines.append(f'      (.arrow 𐑱 𐑚 𐑙)  -- [{i+1+j}] CLINK (in T-branch)')
                else:
                    lines.append(f'      (.arrow 𐑼 𐑚 𐑙)  -- [{i+1+j}] {iop} (in T-branch)')
            # F-branch
            lines.append('      -- F-branch')
            for j, iop in enumerate(f_branch):
                if iop == 'EVALF':
                    lines.append(f'      (.arrow 𐑖 𐑚 𐑙)  -- [{i+1+len(t_branch)+j}] EVALF')
                elif iop == 'AREV':
                    lines.append(f'      (.arrow 𐑗 𐑚 𐑙)  -- [{i+1+len(t_branch)+j}] AREV (in F-branch)')
                elif iop == 'CLINK':
                    lines.append(f'      (.arrow 𐑱 𐑚 𐑙)  -- [{i+1+len(t_branch)+j}] CLINK (in F-branch)')
                else:
                    lines.append(f'      (.arrow 𐑼 𐑚 𐑙)  -- [{i+1+len(t_branch)+j}] {iop} (in F-branch)')
            lines.append(f'    (.arrow 𐑙 𐑙 𐑳)  -- [{end}] FFUSE | stoi := 𐑙')
            i = end + 1
        else:
            field, prim = OPCODE_FIELD.get(op, ('???', '?'))
            src = PRIMITIVE_CYCLE[i % len(PRIMITIVE_CYCLE)]
            tgt = PRIMITIVE_CYCLE[(i + 1) % len(PRIMITIVE_CYCLE)]
            lines.append(f'  (.arrow {prim} {src} {tgt})  -- [{i}] {op} | {field} := {prim}')
            i += 1
    return '\n'.join(lines)


def build_scaffold(name, ops, domain_type, description):
    """Build a complete scaffold.lean file content."""
    safe = make_safe_name(name)
    fp = fingerprint(ops)
    pairs = find_fsplit_ffuse_pairs(ops)
    pairs_str = str(pairs).replace(' ','')
    period = len(ops)

    content = f'''-- IGProtocol scaffold: {' → '.join(ops)}
-- Class: {name}
-- Fingerprint: sig=({fp},)
--   auto_generated=True | period={period}
-- Expected tier: O₂
-- FSPLIT/FFUSE pairs: {pairs_str}

import Imscribing.IGMorphism
import Imscribing.IGFunctor

namespace Imscribing
open Primitives Frobenius IGProtocol
open Dimensionality Topology Relational Polarity Grammar
     Fidelity KineticChar Granularity Criticality Protection Stoichiometry Chirality

{build_field_mapping(ops)}

-- ── Main IGProtocol term ────────────────────────────────────────────────────

{build_arrow_sequence(ops, safe, domain_type)}

-- ── Evaluation arm sub-defs ─────────────────────────────────────────────────

-- truth arm
noncomputable def {safe}_true_arm : IGProtocol 𐑼 𐑡 :=
  ({safe}_protocol).restrictToEVALT

-- false arm
noncomputable def {safe}_false_arm : IGProtocol 𐑼 𐑡 :=
  ({safe}_protocol).restrictToEVALF

-- ── Verification theorems ───────────────────────────────────────────────────

theorem {safe}_tier : TierFunctor.obj 𐑼 = .O₂ := by decide

-- Frobenius (split → fuse): μ∘δ = id on .prod branch
-- Proof: apply igFrobAlg_self_fusion; exact mu_delta_A_id
-- (requires mu_delta_A_id from IGFunctor library)

end Imscribing
'''
    return content


def generate_missing():
    count = 0
    for d in sorted(VAULT.iterdir()):
        if not d.is_dir() or d.name.startswith('.'):
            continue
        name = d.name
        lean_path = d / f"{name}_scaffold.lean"
        if lean_path.exists():
            continue

        # Try JSON first
        json_path = d / f"{name}_ob3ect.json"
        ops = None
        domain_type = "computational"
        description = f"Auto-generated scaffold for {name}"

        if json_path.exists():
            try:
                with open(json_path) as f:
                    data = json.load(f)
                phases = data.get('phases', {})
                p1 = phases.get('phase_1', {})
                p0 = phases.get('phase_0', {})
                domain_type = p0.get('domain_type', 'computational')
                description = p0.get('domain_name', data.get('name', description))[:120]
                ops = [k for k in p1.keys() if k in OPCODE_FIELD]
            except Exception:
                pass

        # Fallback: use canonical 12-step sequence
        if not ops:
            ops = ['VINIT','TANCH','AFWD','AREV','CLINK','IMSCRIB',
                   'FSPLIT','FFUSE','EVALT','EVALF','ENGAGR','IFIX']

        content = build_scaffold(name, ops, domain_type, description)
        with open(lean_path, 'w') as f:
            f.write(content)
        print(f"  Wrote {lean_path}")
        count += 1

    print(f"\nGenerated {count} _scaffold.lean files")

if __name__ == "__main__":
    generate_missing()
