#!/usr/bin/env python3
"""
Patch script to modify pyarchinit_pyqgis.py to handle SpatiaLite view column issues.
This will make the system use explicit column selection when loading views.
"""

import os
import sys
import shutil
from datetime import datetime

def patch_pyqgis_file(file_path):
    """Patch the pyarchinit_pyqgis.py file to fix view loading issues"""
    
    # Create backup
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup at: {backup_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the patch - we'll add a method to fix the layer after loading
    patch_method = '''
    def fix_spatialite_view_columns(self, layer, view_name):
        """
        Fix SpatiaLite view columns issue where QGIS loads all columns from joined tables
        instead of just the view columns.
        """
        if view_name == 'pyarchinit_us_view':
            # Define the columns that should be visible
            expected_columns = [
                'gid', 'the_geom', 'tipo_us_s', 'scavo_s', 'area_s', 'us_s',
                'stratigraph_index_us', 'id_us', 'sito', 'area', 'us', 
                'struttura', 'd_stratigrafica', 'd_interpretativa', 
                'descrizione', 'interpretazione', 'rapporti', 
                'periodo_iniziale', 'fase_iniziale', 'periodo_finale', 
                'fase_finale', 'anno_scavo'
            ]
            
            # Get all fields
            fields = layer.fields()
            field_indices = []
            
            # Find indices of fields we want to keep
            for i in range(fields.count()):
                field_name = fields.at(i).name()
                if field_name not in expected_columns:
                    field_indices.append(i)
            
            # Hide unwanted fields
            if field_indices:
                layer.setExcludeAttributesWms(field_indices)
                layer.setExcludeAttributesWfs(field_indices)
                
                # Also try to set field configuration to hide them
                for idx in field_indices:
                    config = layer.attributeTableConfig()
                    columns = config.columns()
                    for col in columns:
                        if col.name == fields.at(idx).name():
                            col.hidden = True
                    config.setColumns(columns)
                    layer.setAttributeTableConfig(config)
'''
    
    # Find a good place to insert the method (after __init__ method)
    import re
    init_pattern = r'(def __init__.*?\n(?:.*?\n)*?)\n(\s*)def'
    match = re.search(init_pattern, content, re.MULTILINE)
    
    if match:
        # Insert the new method after __init__
        insertion_point = match.end(1)
        indent = match.group(2)
        content = content[:insertion_point] + '\n' + patch_method + '\n' + content[insertion_point:]
    else:
        # If we can't find __init__, add it after class definition
        class_pattern = r'(class\s+\w+.*?:\n)'
        match = re.search(class_pattern, content)
        if match:
            insertion_point = match.end()
            content = content[:insertion_point] + patch_method + '\n' + content[insertion_point:]
    
    # Now patch the places where pyarchinit_us_view is loaded
    # We need to call our fix method after creating the layer
    
    # Pattern to find where layers are created from pyarchinit_us_view
    layer_pattern = r"(layerUS = QgsVectorLayer\(uri\.uri\(\), [^,]+, 'spatialite'\))\n(\s+)(###|if layerUS\.isValid)"
    
    def replace_layer_creation(match):
        layer_creation = match.group(1)
        indent = match.group(2)
        next_line = match.group(3)
        
        # Add the fix call
        fix_call = f"\n{indent}# Fix SpatiaLite view columns issue\n{indent}self.fix_spatialite_view_columns(layerUS, 'pyarchinit_us_view')"
        
        return f"{layer_creation}{fix_call}\n{indent}{next_line}"
    
    content = re.sub(layer_pattern, replace_layer_creation, content)
    
    # Also handle the specific pyarchinit_us_view loading
    specific_pattern = r"(uri\.setDataSource\('', 'pyarchinit_us_view'.*?\n\s*layerUS = QgsVectorLayer.*?\n)"
    
    def add_fix_after_layer(match):
        original = match.group(0)
        # Extract indentation
        lines = original.split('\n')
        indent = ''
        for line in lines:
            if 'layerUS = ' in line:
                indent = line[:len(line) - len(line.lstrip())]
                break
        
        # Add the fix call
        fix_line = f"{indent}self.fix_spatialite_view_columns(layerUS, 'pyarchinit_us_view')\n"
        return original + fix_line
    
    # Apply the specific pattern fix
    content = re.sub(specific_pattern, add_fix_after_layer, content)
    
    # Write the patched content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("File patched successfully!")
    print("\nThe patch adds a method to filter out unwanted columns from SpatiaLite views.")
    print("This should resolve the issue where all columns from joined tables are shown.")

def main():
    # Find the pyarchinit_pyqgis.py file
    plugin_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pyqgis_path = os.path.join(plugin_path, 'modules', 'gis', 'pyarchinit_pyqgis.py')
    
    if not os.path.exists(pyqgis_path):
        print(f"Error: Could not find pyarchinit_pyqgis.py at {pyqgis_path}")
        sys.exit(1)
    
    print(f"Patching: {pyqgis_path}")
    patch_pyqgis_file(pyqgis_path)
    
    print("\nPatch applied! Restart QGIS for the changes to take effect.")
    print("\nNote: If this doesn't fully resolve the issue, you may also need to run")
    print("fix_spatialite_view_registration.py to properly register the view in SpatiaLite.")

if __name__ == "__main__":
    main()