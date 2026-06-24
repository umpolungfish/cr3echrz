#!/usr/bin/env python3
"""Fix _ob3ect.py files with numeric class names by adding 'Ob' prefix."""
import pathlib, re

VAULT = pathlib.Path("/home/mrnob0dy666/imsgct/ob3ect/digital/.vault")

count = 0
for d in sorted(VAULT.iterdir()):
    if not d.is_dir() or d.name.startswith('.'):
        continue
    name = d.name
    py_path = d / f"{name}_ob3ect.py"
    if not py_path.exists():
        continue
    
    content = py_path.read_text()
    # Check if class name starts with digit
    m = re.search(r'class (\w+Ob3ect):', content)
    if m:
        cls = m.group(1)
        if cls and cls[0].isdigit():
            new_cls = 'Ob' + cls
            new_content = content.replace(f'class {cls}:', f'class {new_cls}:')
            if f'{cls}()' in new_content:
                new_content = new_content.replace(f'{cls}()', f'{new_cls}()')
            # Also fix the main guard
            new_content = new_content.replace(f'{cls}.verify()', f'{new_cls}.verify()')
            new_content = new_content.replace(f'{cls}Ob3ect().verify()', f'{new_cls}().verify()')
            py_path.write_text(new_content)
            print(f"  Fixed: {name} -> {new_cls}")
            count += 1

print(f"\nFixed {count} files")
