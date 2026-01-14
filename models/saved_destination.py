from .database import db
from datetime import datetime

class SavedDestination(db.Model):
    __tablename__ = 'saved_destination'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint on (user_id, name)
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='uq_user_destination_name'),)
    
    def __repr__(self):
        return f'<SavedDestination {self.name}: {self.address}>'

