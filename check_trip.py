#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check active trips status"""
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app import app
from models import db, Trip
from datetime import datetime
import pytz

tz = pytz.timezone('Asia/Jerusalem')
now = datetime.now(tz)

with app.app_context():
    trips = Trip.query.filter_by(status='active').all()
    print(f"Active trips: {len(trips)}")
    print("=" * 60)
    
    for trip in trips:
        arrival_time = trip.desired_arrival_time
        if arrival_time.tzinfo is None:
            arrival_time = tz.localize(arrival_time)
        else:
            arrival_time = arrival_time.astimezone(tz)
        
        time_until_arrival = (arrival_time - now).total_seconds() / 60
        
        print(f"\nTrip ID: {trip.id}")
        dest = trip.destination_name or trip.destination
        print(f"Destination: {dest}")
        print(f"Origin: {trip.origin}")
        print(f"Desired arrival: {arrival_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Time until arrival: {time_until_arrival:.1f} minutes")
        print(f"Last check: {trip.last_check_time}")
        if trip.last_travel_duration:
            print(f"Last travel duration: {trip.last_travel_duration} minutes")
        else:
            print("Last travel duration: Not checked yet")
        print(f"Notification sent: {trip.notification_sent}")
        print("-" * 60)

