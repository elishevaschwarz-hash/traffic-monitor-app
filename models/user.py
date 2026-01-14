from .database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    home_address_1 = db.Column(db.String(200))
    home_address_2 = db.Column(db.String(200))
    active_home = db.Column(db.Integer, default=1)  # 1 or 2
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    saved_destinations = db.relationship('SavedDestination', backref='user', lazy=True, cascade='all, delete-orphan')
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')
    trip_history = db.relationship('TripHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def get_active_home_address(self):
        """Returns the currently active home address"""
        if self.active_home == 1:
            return self.home_address_1
        elif self.active_home == 2:
            return self.home_address_2
        return None
    
    def __repr__(self):
        return f'<User {self.phone_number}>'

