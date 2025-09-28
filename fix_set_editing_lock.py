#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to comment out set_editing_lock calls which are causing errors
"""

import os
import re

# List of files to fix
files_to_fix = [
    'tabs/Site.py',
    'tabs/Tma.py',
    'tabs/Tomba.py',
    'tabs/Struttura.py',
    'tabs/Schedaind.py',
    'tabs/Periodizzazione.py',
    'tabs/Inv_Materiali.py',
    'tabs/Documentazione.py',
    'tabs/US_USM.py',
    'tabs/Archeozoology.py',
    'tabs/Deteta.py',
    'tabs/Detsesso.py',
    'tabs/pyarchinit_Pottery_mainapp.py'
]

def comment_set_editing_lock(filepath):
    """Comment out set_editing_lock calls"""

    print(f"Processing {filepath}...")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    changes_made = False
    modified_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line contains set_editing_lock
        if 'self.DB_MANAGER.set_editing_lock(' in line and not line.strip().startswith('#'):
            # Comment out this line and the next few lines that are part of the call
            modified_lines.append('                        # ' + line[24:])  # Preserve indentation
            changes_made = True

            # Check the next lines for continuation
            j = i + 1
            while j < len(lines) and (',' in lines[j] or ')' in lines[j]):
                if not lines[j].strip().startswith('#'):
                    modified_lines.append('                        # ' + lines[j][24:])
                else:
                    modified_lines.append(lines[j])
                j += 1
            i = j
        else:
            modified_lines.append(line)
            i += 1

    if changes_made:
        # Write back the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        print(f"  Commented out set_editing_lock calls")
        return True
    else:
        print(f"  No changes needed")
        return False

def main():
    """Main function"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    success_count = 0
    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            if comment_set_editing_lock(full_path):
                success_count += 1
        else:
            print(f"File not found: {full_path}")

    print(f"\nFixed {success_count} files")

if __name__ == '__main__':
    main()