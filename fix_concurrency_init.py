#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to fix concurrency manager and lock indicator initialization
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

def fix_concurrency_init(filepath):
    """Fix ConcurrencyManager and RecordLockIndicator initialization"""

    print(f"Processing {filepath}...")
    changes_made = False

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix ConcurrencyManager initialization
    pattern1 = r'self\.concurrency_manager = ConcurrencyManager\(\)'
    replacement1 = r'self.concurrency_manager = ConcurrencyManager(self)'

    count1 = len(re.findall(pattern1, content))
    if count1 > 0:
        content = re.sub(pattern1, replacement1, content)
        print(f"  Fixed ConcurrencyManager initialization ({count1} occurrence(s))")
        changes_made = True

    # Check if RecordLockIndicator is imported but not initialized
    has_import = 'RecordLockIndicator' in content
    has_init = 'self.lock_indicator = RecordLockIndicator' in content

    if has_import and not has_init:
        # Find where to add it (after ConcurrencyManager initialization)
        pattern2 = r'(self\.concurrency_manager = ConcurrencyManager\(self\))'
        replacement2 = r'\1\n        self.lock_indicator = RecordLockIndicator(self)'

        content = re.sub(pattern2, replacement2, content)
        print(f"  Added RecordLockIndicator initialization")
        changes_made = True

    if changes_made:
        # Write back the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print(f"  No changes needed")
        return False

def main():
    """Main function"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    success_count = 0
    for form_file in form_files:
        filepath = os.path.join(base_dir, form_file)
        if os.path.exists(filepath):
            if fix_concurrency_init(filepath):
                success_count += 1
        else:
            print(f"File not found: {filepath}")

    print(f"\nFixed {success_count} files")

if __name__ == '__main__':
    main()