from .database import db
from datetime import datetime

class TripHistory(db.Model):
    __tablename__ = 'trip_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    origin = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    destination_name = db.Column(db.String(50))
    desired_arrival_time = db.Column(db.DateTime, nullable=False)
    actual_notification_time = db.Column(db.DateTime, nullable=False)
    estimated_travel_duration = db.Column(db.Integer, nullable=False)  # minutes
    route_used = db.Column(db.String(500))
    traffic_conditions = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TripHistory {self.id}: {self.destination_name}>'

