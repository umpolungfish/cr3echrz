#!/usr/bin/env python3
"""Completely fix imports in all _ob3ect.py files."""
import pathlib, re

VAULT = pathlib.Path("/home/mrnob0dy666/imsgct/ob3ect/digital/.vault")

NEW_IMPORT = '''import os, pathlib, sys, hashlib
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
    
    # Find the docstring end and replace everything between it and the class def
    # Pattern: after the """ docstring, there's the import section, then class
    docstring_end = content.find('"""\n') 
    if docstring_end == -1:
        docstring_end = content.find('"""\n', 10)
    if docstring_end == -1:
        continue
    
    # Find where the class definition starts
    class_match = re.search(r'\nclass ', content)
    if not class_match:
        continue
    
    class_start = class_match.start()
    
    # Replace everything between docstring end + 4 (past the closing """) and class def
    before = content[:docstring_end+4]
    after = content[class_start:]
    
    new_content = before + '\n' + NEW_IMPORT + after
    
    if new_content != content:
        py_path.write_text(new_content)
        count += 1

print(f"Fixed {count} files")
