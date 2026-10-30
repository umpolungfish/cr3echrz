#!/usr/bin/env python3
"""Generate minimal _ob3ect.py files for vault entries missing them."""
import json, os, pathlib, sys

VAULT = pathlib.Path("/home/mrnob0dy666/imsgct/ob3ect/digital/.vault")
P4RAMILL_PY = pathlib.Path("/home/mrnob0dy666/imsgct/p4rakernel/p4ramill_py")

TEMPLATE = '''#!/usr/bin/env python3
"""
{name} ob3ect — {description}

Domain: {domain_type}
Scope: {scope}
Auto-generated on 2026-01-01
"""
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase


class {class_name}Ob3ect:
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
    sys.exit(0 if {class_name}Ob3ect().verify() else 1)
'''

def class_name(name):
    parts = name.replace('-', '_').split('_')
    return ''.join(p.capitalize() for p in parts)

def generate_missing():
    count = 0
    for d in sorted(VAULT.iterdir()):
        if not d.is_dir() or d.name.startswith('.'):
            continue
        name = d.name
        py_path = d / f"{name}_ob3ect.py"
        if py_path.exists():
            continue

        # Get description from JSON if available
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
                description = p0.get('domain_name', desc.get('name', description))[:120]
            except Exception:
                pass

        cn = class_name(name)
        content = TEMPLATE.format(
            name=name,
            class_name=cn,
            domain_type=domain_type,
            scope=scope,
            description=description.replace("'", "\\'")
        )

        with open(py_path, 'w') as f:
            f.write(content)
        print(f"  Wrote {py_path}")
        count += 1

    print(f"\nGenerated {count} _ob3ect.py files")

if __name__ == "__main__":
    generate_missing()
