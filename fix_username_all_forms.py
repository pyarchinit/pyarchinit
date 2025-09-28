#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to fix username detection in all forms with concurrency management
"""

import os
import re

# List of form files to update
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

def fix_connection_method(filepath):
    """Fix the connection method to set database username in concurrency manager"""

    print(f"Processing {filepath}...")

    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find the connection method
    pattern = r'(def on_pushButton_connect_pressed\(self\):.*?\n.*?conn = Connection\(\).*?\n.*?conn_str = conn\.conn_str\(\).*?\n.*?test_conn = conn_str\.find\([\'"]sqlite[\'"]\).*?\n.*?if test_conn == 0:.*?\n.*?self\.DB_SERVER = [\'"]sqlite[\'"].*?\n.*?try:.*?\n.*?self\.DB_MANAGER = Pyarchinit_db_management\(conn_str\).*?\n.*?self\.DB_MANAGER\.connection\(\))'

    # Find all matches
    matches = list(re.finditer(pattern, content, re.DOTALL))

    if not matches:
        print(f"  Warning: Could not find connection method pattern in {filepath}")
        return False

    # Process matches in reverse order to preserve positions
    for match in reversed(matches):
        # Check if username setting already exists
        check_text = content[match.end():match.end()+500]
        if 'set_username' in check_text:
            print(f"  Already has username setting, skipping...")
            continue

        # Insert the username setting code after connection()
        insertion_point = match.end()

        # Get proper indentation
        lines = match.group(0).split('\n')
        for line in lines:
            if 'self.DB_MANAGER.connection()' in line:
                indent = len(line) - len(line.lstrip())
                break
        else:
            indent = 12  # default

        new_code = f"""

{' ' * indent}# Get database username and set it in the concurrency manager
{' ' * indent}user_info = conn.datauser()
{' ' * indent}db_username = user_info.get('user', 'unknown')
{' ' * indent}if hasattr(self, 'concurrency_manager'):
{' ' * (indent + 4)}self.concurrency_manager.set_username(db_username)
"""

        # Insert the new code
        content = content[:insertion_point] + new_code + content[insertion_point:]
        print(f"  Added username setting code")

    # Write back the file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    """Main function"""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    success_count = 0
    for form_file in form_files:
        filepath = os.path.join(base_dir, form_file)
        if os.path.exists(filepath):
            if fix_connection_method(filepath):
                success_count += 1
        else:
            print(f"File not found: {filepath}")

    print(f"\nFixed {success_count} out of {len(form_files)} files")

if __name__ == '__main__':
    main()