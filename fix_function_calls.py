#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix function calls that have their closing parenthesis incorrectly commented
"""

import os

# Dictionary of files and line numbers where we need to uncomment closing parenthesis
fixes_needed = {
    'tabs/Detsesso.py': [827],
    'tabs/Inv_Materiali.py': [4321],
    'tabs/Site.py': [799],
    'tabs/Tma.py': [3571, 5243]
}

def fix_function_parenthesis(filepath, line_numbers):
    """Uncomment specific closing parenthesis lines"""

    print(f"Processing {filepath}...")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    changes = 0
    for line_num in line_numbers:
        # Convert to 0-based index
        idx = line_num - 1

        if idx < len(lines):
            line = lines[idx]
            # Check if this is a commented closing parenthesis
            if '# )' in line and 'insert_values' in ''.join(lines[max(0, idx-60):idx]):
                # Uncomment it
                lines[idx] = line.replace('# )', ')')
                print(f"  Fixed closing parenthesis at line {line_num}")
                changes += 1
            elif line.strip() == '# )':
                # Replace the whole line
                indent = len(line) - len(line.lstrip())
                lines[idx] = ' ' * indent + ')\n'
                print(f"  Fixed closing parenthesis at line {line_num}")
                changes += 1

    # Write back
    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  Fixed {changes} parenthesis")
    else:
        print(f"  No changes made")

    return changes > 0

def main():
    """Main function"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    fixed_count = 0
    for file_path, line_numbers in fixes_needed.items():
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            if fix_function_parenthesis(full_path, line_numbers):
                fixed_count += 1
        else:
            print(f"File not found: {full_path}")

    print(f"\nFixed {fixed_count} files!")

if __name__ == '__main__':
    main()