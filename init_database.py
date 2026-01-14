#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize database separately"""

from app import app
from models import init_db

print("Initializing database...")
with app.app_context():
    init_db(app)
print("[OK] Database initialized successfully!")

