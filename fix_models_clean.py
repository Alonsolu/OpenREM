#!/usr/bin/env python3

import re

# Read the models.py file
with open(r'C:\Users\aloys\OneDrive\Documents\For Alonso\OpenREM\openrem\remapp\models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# First, remove any duplicate on_delete parameters
content = re.sub(r'(on_delete=models\.\w+),\s*on_delete=models\.\w+', r'\1', content)
content = re.sub(r'(on_delete=models\.\w+),\s*on_delete=models\.\w+,\s*on_delete=models\.\w+', r'\1', content)

# Now fix ForeignKeys that don't have on_delete at all
# Pattern to match ForeignKey without any on_delete parameter
pattern = r'models\.ForeignKey\(([^,)]+)([^)]*)\)'

def fix_foreignkey(match):
    first_param = match.group(1).strip()
    rest_params = match.group(2).strip()
    
    # Skip if already has on_delete
    if 'on_delete=' in rest_params:
        return match.group(0)
    
    # Determine appropriate on_delete behavior based on nullable fields
    if 'blank=True' in rest_params and 'null=True' in rest_params:
        on_delete = 'on_delete=models.SET_NULL'
    else:
        on_delete = 'on_delete=models.CASCADE'
    
    if rest_params:
        if rest_params.startswith(','):
            return f'models.ForeignKey({first_param}, {on_delete}{rest_params})'
        else:
            return f'models.ForeignKey({first_param}, {on_delete}, {rest_params})'
    else:
        return f'models.ForeignKey({first_param}, {on_delete})'

# Apply the fix
new_content = re.sub(pattern, fix_foreignkey, content)

# Write back to file
with open(r'C:\Users\aloys\OneDrive\Documents\For Alonso\OpenREM\openrem\remapp\models.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed ForeignKey fields in models.py")
