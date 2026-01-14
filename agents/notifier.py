from twilio.rest import Client
from config import Config
from models import Trip
from utils.time_calculator import format_datetime_hebrew
import logging

logger = logging.getLogger(__name__)

class Notifier:
    """
    Agent for sending WhatsApp notifications via Twilio.
    """
    
    def __init__(self):
        self.client = None
        if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
    
    def send_departure_notification(self, trip: Trip, travel_info: dict) -> bool:
        """
        Send departure notification to user via WhatsApp.
        Returns True if successful, False otherwise.
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            # Build message
            message = self._build_notification_message(trip, travel_info)
            
            # Send via Twilio
            message_obj = self.client.messages.create(
                body=message,
                from_=Config.TWILIO_WHATSAPP_NUMBER,
                to=trip.user.phone_number
            )
            
            logger.info(f"Notification sent to {trip.user.phone_number}, SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
    
    def _build_notification_message(self, trip: Trip, travel_info: dict) -> str:
        """
        Build the notification message in Hebrew.
        """
        # Traffic level in Hebrew
        traffic_levels = {
            'light': 'קלה 🟢',
            'moderate': 'בינונית 🟡',
            'heavy': 'כבדה 🔴',
            'severe': 'חמורה מאוד 🔴🔴'
        }
        
        traffic_hebrew = traffic_levels.get(travel_info.get('traffic_level', 'moderate'), 'בינונית 🟡')
        
        # Format arrival time
        arrival_time_str = format_datetime_hebrew(trip.desired_arrival_time)
        
        # Build message
        message = "🚨 זמן לצאת עכשיו!\n\n"
        message += f"📍 יעד: {trip.destination_name or trip.destination}\n"
        message += f"🕐 זמן הגעה רצוי: {arrival_time_str}\n"
        message += f"⏱️ זמן נסיעה צפוי: {travel_info.get('duration_minutes', 0)} דקות\n"
        message += f"📏 מרחק: {travel_info.get('distance_km', 0)} ק\"מ\n"
        message += f"🚦 תנועה: {traffic_hebrew}\n"
        
        route_summary = travel_info.get('route_summary', '')
        if route_summary:
            message += f"🛣️ מסלול מומלץ: {route_summary}\n"
        
        # Add alternative route if available
        alternative_routes = travel_info.get('alternative_routes', [])
        if alternative_routes:
            best_alt = alternative_routes[0]
            if best_alt.get('savings_minutes', 0) > 0:
                message += f"\n💡 מסלול חלופי: {best_alt.get('summary', '')} (מהיר ב-{best_alt.get('savings_minutes', 0)} דקות)\n"
        
        # Add warnings if any
        warnings = travel_info.get('warnings', [])
        if warnings:
            message += "\n⚠️ "
            message += "\n⚠️ ".join(warnings[:3])  # Max 3 warnings
            message += "\n"
        
        message += "\nבהצלחה! 🚗"
        
        return message

