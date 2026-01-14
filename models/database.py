from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()

def init_db(app):
    """Initialize the database and create all tables"""
    with app.app_context():
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Create all tables
        db.create_all()
        print("[OK] Database initialized successfully!")

