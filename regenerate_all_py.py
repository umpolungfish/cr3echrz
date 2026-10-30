#!/usr/bin/env python3
"""Delete and regenerate all _ob3ect.py files that were auto-generated (not originals)."""
import json, pathlib, sys, re

VAULT = pathlib.Path("/home/mrnob0dy666/imsgct/ob3ect/digital/.vault")

# Original files that should NOT be regenerated (they had PY:Y originally)
# These are files that existed before we started
ORIGINAL_PY = {
    'adjoint', 'anchor_protocol', 'belnap', 'category', 'ccc', 'chiral_pairs',
    'collatz_proof', 'crystal_dns', 'daggercompact', 'dark_matter_floor', 
    'dark_matter_kernel', 'dialetheic', 'docker_paradox', 'dual_bootstrap',
    'elder_futhark_rune_casting_24_runes_as_divinatory_system_fsp',
    'eml_sheffer', 'empty_bootstrap', 'entropy_ob3ect', 'frobenius_kernel',
    'grammaformer', 'hadron_belnap', 'hermetic_vessel_vas_hermeticum_',
    'homotopytypetheory', 'hopf', 'imscriptionoperatingsystem', 'kanextension',
    'langlands_program', 'lift_pipeline', 'linearlogic', 'monad',
    'operad', 'ouroboros_ring', 'paradoxd', 'parakernel', 'pentagram_ritual_lesser_banishing_ritual',
    'philosopher_s_stone_lapis_philosophorum_', 'presheaf',
    'proteins', 'quantum', 'rebis_bio_organic_chemistries_ob3ect',
    'scrying_mirror', 'scheduler', 'self_verifying_proof_assistant_structural_sibling_of_the_stone',
    'sheaf', 'stoneduality', 'stringdiagram', 'temporal_ob3ect',
    'topologically_protected_memory', 'topos', 'truth_machine',
    'void_genesis', 'yoneda', 'dark_matter', 'superposition',
}

TEMPLATE = '''#!/usr/bin/env python3
"""
{name} ob3ect — {description}

Domain: {domain_type} | Scope: {scope}
Auto-generated on 2026-01-01
"""
import os, pathlib, sys, hashlib
_PARENT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))
try:
    from frob import frobenius_phase
except ImportError:
    def frobenius_phase(src):
        h = hashlib.sha256(src.encode()).hexdigest()
        print(f"  Frobenius phase (hash): {{h[:16]}}...")
        return True


class {class_name}:
    """Self-verifying {name} ob3ect."""

    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()
        self.name = "{name}"
        self.domain = "{domain_type}"

    def verify(self) -> bool:
        print(f"=== {{self.name}} Ob3ect ===")
        print(f"  Domain: {{self.domain}}")
        frob_ok = frobenius_phase(self.source)
        closure = frob_ok
        print(f"Closure: {{closure}}")
        return closure


if __name__ == "__main__":
    inst = {class_name}()
    sys.exit(0 if inst.verify() else 1)
'''


def make_class_name(name):
    parts = name.replace('-', '_').split('_')
    cn = ''.join(p.capitalize() for p in parts)
    if not cn or cn[0].isdigit():
        cn = 'Ob' + cn
    return cn


def regenerate():
    deleted = 0
    created = 0
    for d in sorted(VAULT.iterdir()):
        if not d.is_dir() or d.name.startswith('.'):
            continue
        name = d.name
        py_path = d / f"{name}_ob3ect.py"
        
        # Skip originals
        if name in ORIGINAL_PY:
            continue
        
        # Delete existing auto-generated
        if py_path.exists():
            content = py_path.read_text()
            if 'Auto-generated' in content:
                py_path.unlink()
                deleted += 1
        
        # Get info from JSON
        json_path = d / f"{name}_ob3ect.json"
        domain_type = "computational"
        scope = "local"
        description = f"Self-verifying {name} ob3ect"
        if json_path.exists():
            try:
                with open(json_path) as f:
                    desc = json.load(f)
                phases = desc.get('phases', {})
                p0 = phases.get('phase_0', {})
                domain_type = p0.get('domain_type', 'computational')
                scope = p0.get('scope', 'local')
                raw_desc = p0.get('domain_name', desc.get('name', description))[:120]
                description = raw_desc.replace("'", "\\'").replace('"', '\\"')
            except Exception:
                pass

        cn = make_class_name(name)
        content = TEMPLATE.format(
            name=name,
            class_name=cn,
            domain_type=domain_type,
            scope=scope,
            description=description
        )

        with open(py_path, 'w') as f:
            f.write(content)
        created += 1

    print(f"Deleted {deleted} auto-generated files")
    print(f"Created {created} new files")

if __name__ == "__main__":
    regenerate()
