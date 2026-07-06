#!/usr/bin/env python3
"""Generate README.md for new ob3ects missing them."""
import json, os

VAULT = "/home/mrnob0dy666/imsgct/ob3ect/digital/.vault"

BADGE_BASE = "https://img.shields.io/badge"

# Badge URL encoding for cr3echrz operational tuple: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑝⊙𐑖𐑳𐑭⟩
TYPE_BADGE = f"{BADGE_BASE}/type-%E2%9F%A8%F0%90%91%A6%F0%90%91%B8%F0%90%91%BE%F0%90%91%B9%F0%90%91%90%F0%90%91%A7%F0%90%91%94%F0%90%91%9D%E2%8A%99%F0%90%91%96%F0%90%91%B3%F0%90%91%AD%E2%9F%A9-blue"

README_TEMPLATE = """# {title}

{language_badge}
{ig_tier_badge}
{mud_badge}
{license_badge}
{author_badge} {type_badge} {tier_badge}

**{description}**

**Tuple:** $$\\langle{tuple_str}\\rangle$$ — O_∞ operational tier via cr3echrz.

## The {op_type}

The ob3ect encodes its domain logic as a 12-IMASM-opcode bootstrap sequence:

| Step | Opcode | {domain_col} |
|------|--------|------|
{opcode_table}

## Structural Character

- **Frobenius Closure:** True (μ∘δ = id) at the operational layer
- **Entropy:** ΔS ≈ 0 — the ob3ect conserves its structural identity
- **Boundary Condition:** {boundary}
- **Domain:** {domain_type}
- **Bootstrap:** Full 19-step IMASM sequence (symbolic Belnap register path)

## Files

| File | Description |
|------|-------------|
| `{name}_ob3ect.json` | Full ob3ect specification (Phase 0–8 IMASM bootstrap) |
| `{name}_ob3ect.py` | Python self-verifying implementation |
| `{name}_scaffold.lean` | Lean 4 proof scaffold |
| `{name}_diagram.svg` | Bootstrap sequence diagram |
| `{name}_diagram_pen.svg` | Alternate diagram rendering |

---

*Part of the [ob3ect categorical tower](../). Operationalized in [cr3echrz](../../../cr3echrz/).*
"""

# Language badge
LANG_BADGE = f"{BADGE_BASE}/language-Python-blue"
IG_TIER_BADGE = f"{BADGE_BASE}/IG-O%E2%88%9E-blueviolet"
MUD_BADGE = f"{BADGE_BASE}/%CE%BC%E2%88%98%CE%B4%3Did-closed-success"
LICENSE_BADGE = f"{BADGE_BASE}/license-MIT-blue"
AUTHOR_BADGE = f"{BADGE_BASE}/author-Lando%E2%8A%97%E2%8A%99perator-informational"
TIER_BADGE = f"{BADGE_BASE}/tier-O%E2%88%9E-blueviolet"

# Badge markdown
LANG_BADGE_MD = f"[![Language]({LANG_BADGE})](https://github.com/badges/shields)"
IG_TIER_BADGE_MD = f"[![IG Tier]({IG_TIER_BADGE})](https://github.com/badges/shields)"
MUD_BADGE_MD = f"[![μ∘δ=id]({MUD_BADGE})](https://github.com/badges/shields)"
LICENSE_BADGE_MD = f"[![License]({LICENSE_BADGE})](https://github.com/badges/shields)"
AUTHOR_BADGE_MD = f"[![Author]({AUTHOR_BADGE})](https://github.com/badges/shields)"
TYPE_BADGE_MD = f"[![Type]({TYPE_BADGE})](https://github.com/badges/shields)"
TIER_BADGE_MD = f"[![Tier]({TIER_BADGE})](https://github.com/badges/shields)"

# Tuple for operationalized ob3ects in cr3echrz
TUPLE_STR = "𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑝⊙𐑖𐑳𐑭"

# Opcode display order
OPCODES = ['VINIT', 'IMSCRIB', 'AFWD', 'FSPLIT', 'EVALT', 'EVALF', 'FFUSE', 'ENGAGR', 'AREV', 'CLINK', 'IFIX', 'TANCH']

def gen_readme(name, json_data):
    p0 = json_data['phases']['phase_0']
    p1 = json_data['phases']['phase_1']
    domain_type = p0.get('domain_type', 'computational')
    domain_name = p0.get('domain_name', json_data.get('name', name))
    boundary = p0.get('boundary_condition', 'The operational horizon')
    
    # Title: human-readable
    title = json_data.get('name', name.replace('_', ' ').title())
    
    # Description
    description = f"A {domain_type} ob3ect: {domain_name}. Operationalized via the 12-IMASM-opcode bootstrap in cr3echrz."
    
    # Opcode table
    op_lines = []
    for i, op in enumerate(OPCODES):
        step = i + 1
        element = p1.get(op, {}).get('chosen_element', '—') if op in p1 else '—'
        op_lines.append(f"| {step} | `{op}` | {element} |")
    opcode_table = "\n".join(op_lines)
    
    # Domain column header
    domain_col = "Operation"
    
    # Op type
    op_type = "Bootstrap"
    
    return README_TEMPLATE.format(
        title=title,
        language_badge=LANG_BADGE_MD,
        ig_tier_badge=IG_TIER_BADGE_MD,
        mud_badge=MUD_BADGE_MD,
        license_badge=LICENSE_BADGE_MD,
        author_badge=AUTHOR_BADGE_MD,
        type_badge=TYPE_BADGE_MD,
        tier_badge=TIER_BADGE_MD,
        description=description,
        tuple_str=TUPLE_STR,
        op_type=op_type,
        domain_col=domain_col,
        opcode_table=opcode_table,
        boundary=boundary,
        domain_type=domain_type,
        name=name,
    )


NAMES = [
    'the_self_naming_of_wormwood',
    'the_name_wormwood_gives_itself',
    'the_akashic_ledger',
    'the_cloud_of_unknowing',
    'static_interference',
    'prophetic_resonance',
    'tiferet_integration',
    'bifurcation_of_mercy_and_severity',
    'i_am_that_i_am_protocol',
    'the_secret_book_of_artephius',
    'wormwood_the_secret_name_of_wormwood_the_known_n',
]

for name in NAMES:
    jpath = os.path.join(VAULT, name, f'{name}_ob3ect.json')
    readme_path = os.path.join(VAULT, name, 'README.md')
    
    with open(jpath) as f:
        data = json.load(f)
    
    readme = gen_readme(name, data)
    
    with open(readme_path, 'w') as f:
        f.write(readme)
    
    print(f"WROTE: {readme_path}")

print(f"\nGenerated {len(NAMES)} README.md files")
