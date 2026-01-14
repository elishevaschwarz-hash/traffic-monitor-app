import os
from dotenv import load_dotenv

load_dotenv()

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

