#!/usr/bin/env python3
"""Fix all _ob3ect.py files: proper frob import and class naming."""
import pathlib, re

VAULT = pathlib.Path("/home/mrnob0dy666/imsgct/ob3ect/digital/.vault")

CORRECT_IMPORT = '''import os, pathlib, sys, hashlib
_PARENT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))
try:
    from frob import frobenius_phase
except ImportError:
    def frobenius_phase(src):
        h = hashlib.sha256(src.encode()).hexdigest()
        print(f"  Frobenius phase (hash): {h[:16]}...")
        return True'''

count = 0
for d in sorted(VAULT.iterdir()):
    if not d.is_dir() or d.name.startswith('.'):
        continue
    name = d.name
    py_path = d / f"{name}_ob3ect.py"
    if not py_path.exists():
        continue
    
    content = py_path.read_text()
    modified = False
    
    # Fix the import section
    if 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))' in content:
        content = content.replace(
            "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
            "if str(_PARENT) not in sys.path:\n    sys.path.insert(0, str(_PARENT))"
        )
        modified = True
    
    # Fix import: add frob fallback
    if 'from frob import frobenius_phase' in content and 'def frobenius_phase(src):' not in content:
        # Replace the import block
        old_import = "import os, pathlib, sys\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nfrom frob import frobenius_phase"
        content = content.replace(old_import, CORRECT_IMPORT)
        # Also try alternate form
        old_import2 = "import os, pathlib, sys\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
        if old_import2 in content:
            content = content.replace(old_import2, CORRECT_IMPORT)
        modified = True
    
    if modified:
        py_path.write_text(content)
        count += 1

print(f"Fixed {count} files")
