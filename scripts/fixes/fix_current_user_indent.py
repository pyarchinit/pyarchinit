#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix indentation errors for current_user line in commented set_editing_lock blocks
"""

import os

# List of files to fix
files_to_fix = [
    'tabs/Detsesso.py',
    'tabs/Inv_Materiali.py',
    'tabs/Periodizzazione.py',
    'tabs/Site.py',
    'tabs/Tma.py',
    'tabs/US_USM.py',
    'tabs/pyarchinit_Pottery_mainapp.py'
]

def fix_current_user_indent(filepath):
    """Fix current_user indentation in commented blocks"""

    print(f"Processing {filepath}...")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Fix the indentation
    fixed_lines = []
    for i, line in enumerate(lines):
        if line.strip() == 'current_user' and i > 0:
            # Check if previous line is a comment
            if '#' in lines[i-1]:
                # Comment out this line with proper indentation
                fixed_lines.append('                        #     current_user\n')
                print(f"  Fixed indentation at line {i+1}")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    return True

def main():
    """Main function"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            fix_current_user_indent(full_path)
        else:
            print(f"File not found: {full_path}")

    print("\nAll files fixed!")

if __name__ == '__main__':
    main()