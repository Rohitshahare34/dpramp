#!/usr/bin/env python3
"""
Fix CSS parent-related errors
"""

import os
import re

def fix_css_errors():
    """Fix CSS errors in templates"""
    print("🔧 Fixing CSS Errors...")
    
    template_dir = "templates"
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix CSS issues
                # 1. Fix background-clip
                content = re.sub(
                    r'background-clip:\s*text;',
                    'background-clip: text; -webkit-background-clip: text;',
                    content
                )
                
                # 2. Fix gradient syntax
                content = re.sub(
                    r'background-image:\s*linear-gradient\([^)]+\),\s*url\([^)]+\);',
                    lambda m: m.group(0).replace('background-image:', 'background:'),
                    content
                )
                
                # 3. Fix missing semicolons
                content = re.sub(
                    r'background:\s*([^;]+)(?=\s*})',
                    r'background: \1;',
                    content
                )
                
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Fixed: {file_path}")
    
    print("✅ CSS errors fixed!")

if __name__ == "__main__":
    fix_css_errors()
