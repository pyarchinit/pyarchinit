#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix unmatched parenthesis in commented set_editing_lock blocks
"""

import os

# List of files to fix
files_to_fix = [
    'tabs/Detsesso.py',
    'tabs/Deteta.py',
    'tabs/Documentazione.py',
    'tabs/Inv_Materiali.py',
    'tabs/Periodizzazione.py',
    'tabs/Site.py',
    'tabs/Tma.py',
    'tabs/US_USM.py',
    'tabs/pyarchinit_Pottery_mainapp.py'
]

def fix_unmatched_parenthesis(filepath):
    """Fix unmatched closing parenthesis in commented blocks"""

    print(f"Processing {filepath}...")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Fix the unmatched parenthesis
    fixed_lines = []
    changes = 0

    for i, line in enumerate(lines):
        # Check if this is a standalone closing parenthesis after a comment block
        if line.strip() == ')' and i > 0:
            # Check if the previous line contains a comment with set_editing_lock or current_user
            if i > 0 and '#' in lines[i-1]:
                # Comment out this closing parenthesis
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + '# )\n')
                changes += 1
                print(f"  Fixed unmatched parenthesis at line {i+1}")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    # Write back
    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        print(f"  Fixed {changes} unmatched parenthesis")
    else:
        print(f"  No changes needed")

    return changes > 0

def main():
    """Main function"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    fixed_count = 0
    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            if fix_unmatched_parenthesis(full_path):
                fixed_count += 1
        else:
            print(f"File not found: {full_path}")

    print(f"\nFixed {fixed_count} files!")

if __name__ == '__main__':
    main()