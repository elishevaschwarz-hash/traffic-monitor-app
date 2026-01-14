from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from config import Config
from models import db, init_db
from models.user import User
from services.user_service import UserService
from services.trip_service import TripService
from agents.parser_agent import ParserAgent
from agents.traffic_monitor import traffic_monitor
from utils.google_maps_client import GoogleMapsClient
from utils.time_calculator import format_datetime_hebrew
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize Google Maps client
maps_client = GoogleMapsClient()

# Track if app is initialized
_app_initialized = False

def ensure_initialized():
    """Ensure app is initialized (database + monitoring)"""
    global _app_initialized
    if not _app_initialized:
        try:
            with app.app_context():
                init_db(app)
                logger.info("Database initialized")

            traffic_monitor.start_monitoring()
            logger.info("Traffic monitoring started")
            _app_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize: {str(e)}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ensure_initialized()
    from models.trip import Trip
    active_trips_count = Trip.query.filter_by(status='active').count()

    return {
        'status': 'ok',
        'active_trips': active_trips_count,
        'timestamp': str(datetime.now())
    }

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages from Twilio"""
    ensure_initialized()
    try:
        # Get incoming message
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '').strip()
        
        logger.info(f"Received message from {from_number}: {incoming_msg}")
        
        if not incoming_msg or not from_number:
            return _send_twilio_response("❌ שגיאה: לא הצלחתי לקרוא את ההודעה")
        
        # Get or create user
        user = UserService.get_or_create_user(from_number)
        
        # Parse message
        parser = ParserAgent()
        parsed = parser.parse_message(incoming_msg, user)
        
        intent = parsed.get('intent', 'help')
        
        # Route based on intent
        if intent == 'create_trip':
            response = handle_create_trip(user, parsed)
        elif intent == 'cancel_trip':
            response = handle_cancel_trip(user)
        elif intent == 'set_home':
            response = handle_set_home(user, parsed)
        elif intent == 'save_destination':
            response = handle_save_destination(user, parsed)
        elif intent == 'switch_home':
            response = handle_switch_home(user, parsed)
        elif intent == 'show_history':
            response = handle_show_history(user)
        else:
            response = get_help_message()
        
        return _send_twilio_response(response)
        
    except Exception as e:
        logger.error(f"Error in whatsapp_webhook: {str(e)}", exc_info=True)
        return _send_twilio_response("❌ שגיאה: משהו השתבש. נסי שוב מאוחר יותר.")

def handle_create_trip(user, parsed):
    """Handle create_trip intent"""
    destination = parsed.get('destination')
    destination_name = parsed.get('destination_name')
    desired_time = parsed.get('time')
    
    if not destination:
        return "❌ לא הצלחתי לזהות את היעד. נסי:\n'רוצה להגיע לעבודה ב-10:00'"
    
    if not desired_time:
        return "❌ לא הצלחתי לזהות את הזמן. נסי:\n'רוצה להגיע לעבודה ב-10:00'"
    
    # Get initial travel time estimate
    origin = user.get_active_home_address()
    if not origin:
        return "❌ לא הגדרת כתובת בית!\nשלחי הודעה כמו:\n'הבית שלי זה [כתובת]'"
    
    travel_info = maps_client.get_directions(origin, destination)
    if not travel_info:
        return "❌ לא הצלחתי למצוא מסלול ליעד. בדקי את הכתובת."
    
    # Create trip
    trip, message = TripService.create_trip(
        user=user,
        destination=destination,
        desired_arrival_time=desired_time,
        destination_name=destination_name
    )
    
    if not trip:
        return message
    
    # Add initial travel time to message
    message += f"\n⏱️ זמן נסיעה נוכחי: {travel_info.get('duration_minutes', 0)} דקות"
    
    return message

def handle_cancel_trip(user):
    """Handle cancel_trip intent"""
    success, message = TripService.cancel_active_trip(user)
    return message

def handle_set_home(user, parsed):
    """Handle set_home intent"""
    address = parsed.get('address')
    home_number = parsed.get('home_number', 1)
    
    if not address:
        return "❌ לא הצלחתי לזהות את הכתובת. נסי:\n'הבית שלי זה [כתובת]'"
    
    success, message = UserService.set_home_address(user, address, home_number)
    return message

def handle_save_destination(user, parsed):
    """Handle save_destination intent"""
    address = parsed.get('address')
    name = parsed.get('destination_name')
    
    if not address or not name:
        return "❌ לא הצלחתי לזהות את הכתובת או השם. נסי:\n'שמור [כתובת] בתור [שם]'"
    
    destination, message = UserService.save_destination(user, name, address)
    return message

def handle_switch_home(user, parsed):
    """Handle switch_home intent"""
    home_number = parsed.get('home_number')
    
    if not home_number:
        return "❌ לא הצלחתי לזהות את מספר הכתובת. נסי:\n'החלף לבית 1' או 'החלף לבית 2'"
    
    success, message = UserService.switch_active_home(user, home_number)
    return message

def handle_show_history(user):
    """Handle show_history intent"""
    history = TripService.get_trip_history(user, limit=10)
    
    if not history:
        return "📊 אין לך נסיעות קודמות."
    
    message = "📊 10 הנסיעות האחרונות שלך:\n\n"
    
    traffic_levels = {
        'light': 'קלה 🟢',
        'moderate': 'בינונית 🟡',
        'heavy': 'כבדה 🔴',
        'severe': 'חמורה מאוד 🔴🔴'
    }
    
    for i, trip in enumerate(history, 1):
        date_str = trip.completed_at.strftime('%d/%m/%Y')
        time_str = trip.desired_arrival_time.strftime('%H:%M')
        traffic_hebrew = traffic_levels.get(trip.traffic_conditions, 'בינונית 🟡')
        
        message += f"{i}️⃣ {date_str} - {trip.destination_name or trip.destination}\n"
        message += f"   🕐 {time_str} | ⏱️ {trip.estimated_travel_duration} דק' | 🚦 {traffic_hebrew}\n\n"
    
    return message

def get_help_message():
    """Return help message"""
    return """👋 שלום! אני בוט ניטור תנועה חכם.

📋 פקודות זמינות:

🏠 הגדרת כתובת בית:
   "הבית שלי זה [כתובת]"
   "כתובת 1: [כתובת]"
   "כתובת 2: [כתובת]"

📍 שמירת יעד:
   "שמור [כתובת] בתור [שם]"
   דוגמה: "שמור Weizmann Institute בתור עבודה"

🚗 יצירת נסיעה:
   "רוצה להגיע ל-[יעד] ב-[שעה]"
   דוגמה: "רוצה להגיע לעבודה ב-10:00"

🔄 החלפת כתובת בית:
   "החלף לבית 1" או "החלף לבית 2"

❌ ביטול נסיעה:
   "בטל נסיעה"

📊 היסטוריה:
   "הראה לי היסטוריה"

אני אעדכן אותך מתי לצאת! 🚗"""

def _send_twilio_response(message):
    """Create and return Twilio MessagingResponse"""
    resp = MessagingResponse()
    resp.message(message)
    return str(resp)

def start_ngrok():
    """Start Ngrok tunnel if enabled"""
    if not Config.USE_NGROK:
        return None

    try:
        from pyngrok import ngrok
        import os

        # Set authtoken if provided in environment
        ngrok_authtoken = os.getenv('NGROK_AUTHTOKEN')
        if ngrok_authtoken:
            ngrok.set_auth_token(ngrok_authtoken)

        # Start tunnel
        tunnel = ngrok.connect(5000)
        ngrok_url = tunnel.public_url

        logger.info(f"Ngrok tunnel started: {ngrok_url}")
        logger.info(f"Set Twilio webhook to: {ngrok_url}/webhook/whatsapp")

        return ngrok_url
    except Exception as e:
        logger.error(f"Failed to start Ngrok: {str(e)}")
        return None

if __name__ == '__main__':
    # Initialize for development
    ensure_initialized()
    # Start Ngrok only in development
    ngrok_url = start_ngrok()

    # Run Flask app in development mode
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)

