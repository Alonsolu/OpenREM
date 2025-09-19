#!/usr/bin/env python3

import re

# Read the models.py file
with open(r'C:\Users\aloys\OneDrive\Documents\For Alonso\OpenREM\openrem\remapp\models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match ForeignKey without on_delete
pattern = r'models\.ForeignKey\(([^,)]+)(\s*,\s*(?!on_delete)[^)]*)?(\s*)\)'

def replace_foreignkey(match):
    first_param = match.group(1)
    other_params = match.group(2) or ''
    whitespace = match.group(3) or ''
    
    # Determine appropriate on_delete behavior
    if 'blank=True' in other_params and 'null=True' in other_params:
        on_delete = ', on_delete=models.SET_NULL'
    else:
        on_delete = ', on_delete=models.CASCADE'
    
    return f'models.ForeignKey({first_param}{on_delete}{other_params}{whitespace})'

# Replace all ForeignKey instances
new_content = re.sub(pattern, replace_foreignkey, content)

# Write back to file
with open(r'C:\Users\aloys\OneDrive\Documents\For Alonso\OpenREM\openrem\remapp\models.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed all ForeignKey fields in models.py")
