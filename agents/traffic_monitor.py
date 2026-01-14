from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from models import db, Trip
from config import Config
from utils.google_maps_client import GoogleMapsClient
from utils.time_calculator import calculate_optimal_departure
from agents.notifier import Notifier
import logging
import pytz

logger = logging.getLogger(__name__)

class TrafficMonitor:
    """
    Background traffic monitoring agent.
    Checks active trips every few minutes and sends notifications when needed.
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.maps_client = GoogleMapsClient()
        self.notifier = Notifier()
        self.is_running = False
    
    def start_monitoring(self):
        """Start the background monitoring scheduler"""
        if self.is_running:
            logger.warning("TrafficMonitor is already running")
            return
        
        # Schedule job to run every TRAFFIC_CHECK_INTERVAL_MINUTES
        trigger = IntervalTrigger(minutes=Config.TRAFFIC_CHECK_INTERVAL_MINUTES)
        self.scheduler.add_job(
            func=self.check_all_active_trips,
            trigger=trigger,
            id='traffic_check',
            name='Check all active trips',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info(f"TrafficMonitor started - checking every {Config.TRAFFIC_CHECK_INTERVAL_MINUTES} minutes")
    
    def stop_monitoring(self):
        """Stop the background monitoring scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("TrafficMonitor stopped")
    
    def check_all_active_trips(self):
        """Check all active trips and send notifications if needed"""
        from app import app
        with app.app_context():
            try:
                active_trips = Trip.query.filter_by(status='active').all()
                logger.info(f"Checking {len(active_trips)} active trips")
                
                for trip in active_trips:
                    try:
                        self.check_single_trip(trip)
                    except Exception as e:
                        logger.error(f"Error checking trip {trip.id}: {str(e)}")
                        continue
            except Exception as e:
                logger.error(f"Error in check_all_active_trips: {str(e)}")
    
    def check_single_trip(self, trip: Trip):
        """
        Check a single trip and send notification if it's time to leave.
        """
        # Skip if notification already sent
        if trip.notification_sent:
            return
        
        # Check if trip has passed desired arrival time
        now = datetime.now(pytz.timezone(Config.TIMEZONE))
        # Make sure desired_arrival_time is timezone-aware for comparison
        arrival_time = trip.desired_arrival_time
        if arrival_time.tzinfo is None:
            arrival_time = pytz.timezone(Config.TIMEZONE).localize(arrival_time)
        
        if arrival_time < now:
            trip.status = 'cancelled'
            db.session.commit()
            logger.info(f"Trip {trip.id} passed desired arrival time, marking as cancelled")
            return
        
        # Get current travel time from Google Maps
        travel_info = self.maps_client.get_directions(
            origin=trip.origin,
            destination=trip.destination
        )
        
        if not travel_info:
            logger.warning(f"Could not get directions for trip {trip.id}")
            return
        
        # Update trip with latest travel info
        trip.last_check_time = datetime.utcnow()
        trip.last_travel_duration = travel_info['duration_minutes']
        
        # Calculate optimal departure time
        optimal_departure = calculate_optimal_departure(
            desired_arrival=arrival_time,
            travel_duration_minutes=travel_info['duration_minutes'],
            buffer_minutes=Config.DEPARTURE_BUFFER_MINUTES
        )
        
        # Check if it's time to send notification
        # Send notification if we're within NOTIFICATION_ADVANCE_MINUTES of optimal departure
        notification_time = optimal_departure - timedelta(minutes=Config.NOTIFICATION_ADVANCE_MINUTES)
        
        if now >= notification_time:
            # Time to send notification!
            logger.info(f"Sending notification for trip {trip.id}")
            
            success = self.notifier.send_departure_notification(trip, travel_info)
            
            if success:
                trip.notification_sent = True
                trip.status = 'notified'
                
                # Save to history
                from services.trip_service import TripService
                TripService.save_trip_to_history(trip, travel_info)
                
                db.session.commit()
                logger.info(f"Notification sent for trip {trip.id}")
            else:
                logger.error(f"Failed to send notification for trip {trip.id}")
        else:
            # Not time yet, just update the trip
            db.session.commit()
            logger.debug(f"Trip {trip.id}: optimal departure in {optimal_departure - now}")

# Global instance
traffic_monitor = TrafficMonitor()

