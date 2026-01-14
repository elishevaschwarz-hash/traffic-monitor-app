from models import db, Trip, TripHistory
from datetime import datetime
import pytz
from config import Config
import logging

logger = logging.getLogger(__name__)

class TripService:
    @staticmethod
    def create_trip(user, destination: str, desired_arrival_time: datetime, destination_name: str = None) -> tuple:
        """
        Create a new trip for a user.
        If user has an active trip, cancel it first.
        Returns (trip_object, confirmation_message)
        """
        # Check for active trip and cancel it
        active_trip = Trip.query.filter_by(user_id=user.id, status='active').first()
        if active_trip:
            TripService.cancel_active_trip(user)
            logger.info(f"Cancelled existing trip {active_trip.id} for user {user.phone_number}")
        
        # Get origin from user's active home
        origin = user.get_active_home_address()
        if not origin:
            return (None, "❌ לא הגדרת כתובת בית!\nשלחי הודעה כמו:\n'הבית שלי זה [כתובת]'")
        
        # Validate time
        now = datetime.now(pytz.timezone(Config.TIMEZONE))
        # Make sure desired_arrival_time is timezone-aware for comparison
        if desired_arrival_time.tzinfo is None:
            desired_arrival_time = pytz.timezone(Config.TIMEZONE).localize(desired_arrival_time)
        
        if desired_arrival_time < now:
            return (None, "❌ הזמן שציינת כבר עבר!\nציני זמן עתידי.")
        
        # Create new trip
        trip = Trip(
            user_id=user.id,
            origin=origin,
            destination=destination,
            destination_name=destination_name,
            desired_arrival_time=desired_arrival_time,
            status='active',
            notification_sent=False
        )
        
        db.session.add(trip)
        db.session.commit()
        
        logger.info(f"Created trip {trip.id} for user {user.phone_number} to {destination}")
        
        # Format confirmation message
        from utils.time_calculator import format_datetime_hebrew
        time_str = format_datetime_hebrew(desired_arrival_time)
        
        message = f"✅ אני עוקבת אחרי התנועה!\n\n"
        message += f"📍 יעד: {destination_name or destination}\n"
        message += f"🏠 מוצא: {origin}\n"
        message += f"🕐 זמן הגעה רצוי: {time_str}\n"
        message += f"אעדכן אותך מתי לצאת! 🚗"
        
        return (trip, message)
    
    @staticmethod
    def cancel_active_trip(user) -> tuple:
        """
        Cancel the active trip for a user.
        Returns (success, message)
        """
        active_trip = Trip.query.filter_by(user_id=user.id, status='active').first()
        
        if not active_trip:
            return (False, "❌ אין לך נסיעה פעילה כרגע.")
        
        active_trip.status = 'cancelled'
        db.session.commit()
        
        destination = active_trip.destination_name or active_trip.destination
        logger.info(f"Cancelled trip {active_trip.id} for user {user.phone_number}")
        
        return (True, f"✅ ביטלתי את המעקב אחרי הנסיעה ל-{destination}\nאפשר לבקש נסיעה חדשה בכל זמן!")
    
    @staticmethod
    def get_trip_history(user, limit: int = 10):
        """
        Get trip history for a user.
        Returns list of TripHistory objects.
        """
        return TripHistory.query.filter_by(user_id=user.id)\
            .order_by(TripHistory.completed_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def save_trip_to_history(trip, travel_info: dict):
        """
        Save a completed trip to history.
        """
        trip_history = TripHistory(
            user_id=trip.user_id,
            origin=trip.origin,
            destination=trip.destination,
            destination_name=trip.destination_name,
            desired_arrival_time=trip.desired_arrival_time,
            actual_notification_time=datetime.utcnow(),
            estimated_travel_duration=travel_info.get('duration_minutes', 0),
            route_used=travel_info.get('route_summary', ''),
            traffic_conditions=travel_info.get('traffic_level', 'unknown')
        )
        
        db.session.add(trip_history)
        db.session.commit()
        
        logger.info(f"Saved trip {trip.id} to history")

