from datetime import datetime, timedelta
import pytz
import re
from config import Config

TIMEZONE = pytz.timezone(Config.TIMEZONE)

def parse_time_from_text(text: str) -> datetime:
    """
    Parse time from Hebrew text.
    Supports formats like: "10:00", "1430", "10:30", etc.
    If time has passed today, adds one day.
    """
    if not text:
        return None
    
    # Remove whitespace
    text = text.strip()
    
    # Pattern for HH:MM or HHMM
    time_pattern = r'(\d{1,2}):?(\d{2})?'
    match = re.search(time_pattern, text)
    
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        
        # Validate hour and minute
        if hour < 0 or hour > 23:
            return None
        if minute < 0 or minute > 59:
            return None
        
        # Get current time in Israel timezone
        now = datetime.now(TIMEZONE)
        
        # Create datetime for today at specified time
        target_time = TIMEZONE.localize(datetime(now.year, now.month, now.day, hour, minute))
        
        # If time has passed, add one day
        if target_time < now:
            target_time += timedelta(days=1)
        
        return target_time
    
    return None

def calculate_optimal_departure(desired_arrival: datetime, travel_duration_minutes: int, buffer_minutes: int = 10) -> datetime:
    """
    Calculate optimal departure time.
    optimal_departure = desired_arrival - travel_duration - buffer
    """
    if not isinstance(desired_arrival, datetime):
        raise ValueError("desired_arrival must be a datetime object")
    
    total_minutes = travel_duration_minutes + buffer_minutes
    optimal_departure = desired_arrival - timedelta(minutes=total_minutes)
    
    return optimal_departure

def format_datetime_hebrew(dt: datetime) -> str:
    """
    Format datetime in Hebrew format.
    Example: "שלישי, 14 בינואר 2026, 10:00"
    """
    if not dt:
        return ""
    
    # Convert to Israel timezone if needed
    if dt.tzinfo is None:
        dt = TIMEZONE.localize(dt)
    else:
        dt = dt.astimezone(TIMEZONE)
    
    # Hebrew day names
    days = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
    day_name = days[dt.weekday()]
    
    # Hebrew month names
    months = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
              'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר']
    month_name = months[dt.month - 1]
    
    # Format: "שלישי, 14 בינואר 2026, 10:00"
    return f"{day_name}, {dt.day} ב{month_name} {dt.year}, {dt.strftime('%H:%M')}"

