#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix .env file BOM issue"""

with open('.env', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Remove BOM if exists
content = content.replace('\ufeff', '')

with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed .env file")

