import googlemaps
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GoogleMapsClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.GOOGLE_MAPS_API_KEY
        if not self.api_key:
            raise ValueError("Google Maps API key is required")
        self.client = googlemaps.Client(key=self.api_key)
    
    def get_directions(self, origin: str, destination: str, arrival_time: datetime = None) -> dict:
        """
        Get directions from origin to destination.
        Returns dict with duration, distance, route info, and traffic level.
        """
        try:
            # Use departure_time='now' to get current traffic conditions
            directions_result = self.client.directions(
                origin=origin,
                destination=destination,
                mode="driving",
                departure_time="now",
                alternatives=True,
                language="he"
            )
            
            if not directions_result:
                logger.warning(f"No directions found for {origin} -> {destination}")
                return None
            
            # Get primary route
            primary_route = directions_result[0]
            leg = primary_route['legs'][0]
            
            # Extract duration (in seconds)
            duration_seconds = leg['duration']['value']
            duration_in_traffic_seconds = leg.get('duration_in_traffic', {}).get('value', duration_seconds)
            
            duration_minutes = duration_seconds // 60
            duration_in_traffic_minutes = duration_in_traffic_seconds // 60
            
            # Extract distance (in meters)
            distance_meters = leg['distance']['value']
            distance_km = distance_meters / 1000
            
            # Extract route summary
            route_summary = primary_route.get('summary', '')
            
            # Calculate traffic level
            if duration_seconds > 0:
                ratio = duration_in_traffic_seconds / duration_seconds
                if ratio < 1.2:
                    traffic_level = 'light'
                elif ratio < 1.5:
                    traffic_level = 'moderate'
                elif ratio < 2.0:
                    traffic_level = 'heavy'
                else:
                    traffic_level = 'severe'
            else:
                traffic_level = 'light'
            
            # Extract warnings from steps
            warnings = []
            for step in leg.get('steps', []):
                if 'warnings' in step:
                    warnings.extend(step['warnings'])
            
            # Process alternative routes
            alternative_routes = []
            for alt_route in directions_result[1:4]:  # Max 3 alternatives
                alt_leg = alt_route['legs'][0]
                alt_duration = alt_leg.get('duration_in_traffic', {}).get('value', alt_leg['duration']['value']) // 60
                alt_summary = alt_route.get('summary', '')
                savings = duration_in_traffic_minutes - alt_duration
                
                if savings > 0:  # Only include if it's faster
                    alternative_routes.append({
                        'summary': alt_summary,
                        'duration_minutes': alt_duration,
                        'savings_minutes': savings
                    })
            
            # Sort alternatives by savings
            alternative_routes.sort(key=lambda x: x['savings_minutes'], reverse=True)
            
            return {
                'duration_minutes': duration_in_traffic_minutes,
                'duration_in_traffic_minutes': duration_in_traffic_minutes,
                'distance_km': round(distance_km, 1),
                'route_summary': route_summary,
                'traffic_level': traffic_level,
                'alternative_routes': alternative_routes[:2],  # Top 2 alternatives
                'warnings': warnings
            }
            
        except Exception as e:
            logger.error(f"Error getting directions: {str(e)}")
            return None
    
    def geocode_address(self, address: str) -> tuple:
        """
        Convert address to coordinates (lat, lng).
        Returns (latitude, longitude) or None if geocoding fails.
        """
        try:
            geocode_result = self.client.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return (location['lat'], location['lng'])
            return None
        except Exception as e:
            logger.error(f"Error geocoding address {address}: {str(e)}")
            return None

