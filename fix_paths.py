#!/usr/bin/env python3
import os
import re

# Fix all template paths from "rough imgs" to "rough_imgs"
templates_dir = "templates"

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace all instances of "rough imgs" with "rough_imgs"
            new_content = content.replace('rough imgs', 'rough_imgs')
            
            if content != new_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed: {file_path}")

print("All paths fixed!")
