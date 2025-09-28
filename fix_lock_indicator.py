#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to fix RecordLockIndicator initialization in all forms
"""

import os
import re

# List of form files to check
form_files = [
    'tabs/Site.py',
    'tabs/Tma.py',
    'tabs/Tomba.py',
    'tabs/Struttura.py',
    'tabs/Schedaind.py',
    'tabs/Periodizzazione.py',
    'tabs/Inv_Materiali.py',
    'tabs/Documentazione.py'
]

def fix_lock_indicator(filepath):
    """Fix RecordLockIndicator initialization to include parent widget"""

    print(f"Processing {filepath}...")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find incorrect initialization
    pattern = r'self\.lock_indicator = RecordLockIndicator\(\)'
    replacement = r'self.lock_indicator = RecordLockIndicator(self)'

    # Count replacements
    count = len(re.findall(pattern, content))

    if count > 0:
        # Replace the pattern
        content = re.sub(pattern, replacement, content)

        # Write back the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  Fixed {count} occurrence(s)")
        return True
    else:
        print(f"  Already correct or not found")
        return False

def main():
    """Main function"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    success_count = 0
    for form_file in form_files:
        filepath = os.path.join(base_dir, form_file)
        if os.path.exists(filepath):
            if fix_lock_indicator(filepath):
                success_count += 1
        else:
            print(f"File not found: {filepath}")

    print(f"\nFixed {success_count} files")

if __name__ == '__main__':
    main()