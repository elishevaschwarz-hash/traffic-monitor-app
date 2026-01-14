from .database import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class Trip(db.Model):
    __tablename__ = 'trip'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    origin = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    destination_name = db.Column(db.String(50))
    desired_arrival_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_check_time = db.Column(db.DateTime)
    last_travel_duration = db.Column(db.Integer)  # minutes
    notification_sent = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')
    
    __table_args__ = (
        CheckConstraint("status IN ('active', 'notified', 'cancelled')", name='check_trip_status'),
    )
    
    def __repr__(self):
        return f'<Trip {self.id}: {self.origin} -> {self.destination}>'

