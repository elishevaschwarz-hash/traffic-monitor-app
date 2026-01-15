import os
from dotenv import load_dotenv

load_dotenv()

# Debug: Print environment variable status (will appear in Railway logs)
print(f"[CONFIG DEBUG] GOOGLE_MAPS_API_KEY present: {bool(os.getenv('GOOGLE_MAPS_API_KEY'))}")
if os.getenv('GOOGLE_MAPS_API_KEY'):
    print(f"[CONFIG DEBUG] API key starts with: {os.getenv('GOOGLE_MAPS_API_KEY')[:15]}...")
else:
    print("[CONFIG DEBUG] GOOGLE_MAPS_API_KEY is None or empty!")
    print(f"[CONFIG DEBUG] All environment variables: {list(os.environ.keys())}")

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///traffic_monitor.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
    
    # Google Maps
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Monitoring
    TRAFFIC_CHECK_INTERVAL_MINUTES = 3
    DEPARTURE_BUFFER_MINUTES = 10
    NOTIFICATION_ADVANCE_MINUTES = 5
    
    # Timezone
    TIMEZONE = 'America/Chicago'  # St. Louis timezone
    
    # Ngrok
    USE_NGROK = os.getenv('USE_NGROK', 'false').lower() == 'true'
    NGROK_AUTHTOKEN = os.getenv('NGROK_AUTHTOKEN')

