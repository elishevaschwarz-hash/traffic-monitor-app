import re
from typing import Dict, Optional
from datetime import datetime
from models import User
from utils.time_calculator import parse_time_from_text
from utils.hebrew_utils import normalize_hebrew_text, extract_destination_name, hebrew_number_words_to_digits

class ParserAgent:
    """
    NLP parser for Hebrew WhatsApp messages.
    Extracts intent and entities from user messages.
    """
    
    @staticmethod
    def parse_message(message_text: str, user: User) -> Dict:
        """
        Parse incoming message and extract intent + entities.
        Returns dict with intent, destination, time, etc.
        """
        if not message_text:
            return {'intent': 'help', 'confidence': 0.0}
        
        normalized = normalize_hebrew_text(message_text)
        
        # Try to parse different intents
        result = ParserAgent._parse_create_trip(normalized, user)
        if result:
            return result
        
        result = ParserAgent._parse_cancel_trip(normalized)
        if result:
            return result
        
        result = ParserAgent._parse_set_home(normalized)
        if result:
            return result
        
        result = ParserAgent._parse_save_destination(normalized)
        if result:
            return result
        
        result = ParserAgent._parse_switch_home(normalized)
        if result:
            return result
        
        result = ParserAgent._parse_show_history(normalized)
        if result:
            return result
        
        # Default to help
        return {'intent': 'help', 'confidence': 0.0}
    
    @staticmethod
    def _parse_create_trip(text: str, user: User) -> Optional[Dict]:
        """
        Parse "create_trip" intent.
        Patterns: "רוצה להגיע ל-X ב-Y:Z", "צריכה להיות ב-X ב-Y:Z"
        """
        # Pattern: (רוצה|צריכה?|להגיע)\s+(ל)?(.+?)\s+(ב|בשעה)[-:]?\s*(\d{1,2}):?(\d{2})?
        pattern = r'(רוצה|צריכה?|להגיע|להיות)\s+(ל|ב)?(.+?)\s+(ב|בשעה|עד)[-:]?\s*(\d{1,2}):?(\d{2})?'
        match = re.search(pattern, text)
        
        if not match:
            return None
        
        destination_text = match.group(3).strip()
        hour = int(match.group(5))
        minute = int(match.group(6)) if match.group(6) else 0
        
        # Parse time
        time_str = f"{hour}:{minute:02d}"
        time_obj = parse_time_from_text(time_str)
        
        if not time_obj:
            return None
        
        # Check if destination is a saved destination
        destination_address = extract_destination_name(destination_text, user.saved_destinations)
        destination_name = None
        
        if destination_address:
            # Find the name
            for dest in user.saved_destinations:
                if normalize_hebrew_text(dest.name) in normalize_hebrew_text(destination_text):
                    destination_name = dest.name
                    break
        else:
            # Check for special cases
            if 'ביתה' in destination_text or 'הבית' in destination_text:
                destination_address = user.get_active_home_address()
                destination_name = "בית"
            else:
                # Use the text as-is (might be a full address)
                destination_address = destination_text
        
        return {
            'intent': 'create_trip',
            'destination': destination_address,
            'destination_name': destination_name,
            'time': time_obj,
            'confidence': 0.9
        }
    
    @staticmethod
    def _parse_cancel_trip(text: str) -> Optional[Dict]:
        """
        Parse "cancel_trip" intent.
        Patterns: "בטל", "ביטול", "לא צריכה"
        """
        cancel_patterns = [
            r'בטל',
            r'ביטול',
            r'לא\s+צריכה?',
            r'תבטלי',
            r'תבטל'
        ]
        
        for pattern in cancel_patterns:
            if re.search(pattern, text):
                return {
                    'intent': 'cancel_trip',
                    'confidence': 0.95
                }
        
        return None
    
    @staticmethod
    def _parse_set_home(text: str) -> Optional[Dict]:
        """
        Parse "set_home" intent.
        Patterns: "הבית שלי הוא X", "כתובת 1: X", "כתובת 2: X"
        """
        # Pattern 1: "הבית שלי הוא X" or "בית זה X"
        pattern1 = r'(בית|הבית\s+שלי|כתובת)\s*(1|2|ראשון|שני)?\s*(הוא|זה|:)?\s*(.+)'
        match = re.search(pattern1, text)
        
        if match:
            home_text = match.group(2) if match.group(2) else None
            address = match.group(4).strip()
            
            # Determine home number
            home_number = 1
            if home_text:
                if '2' in home_text or 'שני' in home_text:
                    home_number = 2
                elif '1' in home_text or 'ראשון' in home_text:
                    home_number = 1
            
            return {
                'intent': 'set_home',
                'address': address,
                'home_number': home_number,
                'confidence': 0.9
            }
        
        return None
    
    @staticmethod
    def _parse_save_destination(text: str) -> Optional[Dict]:
        """
        Parse "save_destination" intent.
        Patterns: "שמור X בתור Y", "תשמור את X כ-Y"
        """
        # Pattern: (שמור|תשמור|לשמור)\s+(את\s+)?(.+?)\s+(בתור|כ)[-:]?\s*(.+)
        pattern = r'(שמור|תשמור|לשמור)\s+(את\s+)?(.+?)\s+(בתור|כ)[-:]?\s*(.+)'
        match = re.search(pattern, text)
        
        if match:
            address = match.group(3).strip()
            name = match.group(5).strip()
            
            return {
                'intent': 'save_destination',
                'address': address,
                'destination_name': name,
                'confidence': 0.9
            }
        
        return None
    
    @staticmethod
    def _parse_switch_home(text: str) -> Optional[Dict]:
        """
        Parse "switch_home" intent.
        Patterns: "החלף לבית 1", "עבור לכתובת 2"
        """
        # Pattern: (החלף|שנה|עבור)\s*(ל)?(בית|כתובת)?\s*(1|2)
        pattern = r'(החלף|שנה|עבור)\s*(ל)?(בית|כתובת)?\s*(1|2)'
        match = re.search(pattern, text)
        
        if match:
            home_number = int(match.group(4))
            
            return {
                'intent': 'switch_home',
                'home_number': home_number,
                'confidence': 0.95
            }
        
        return None
    
    @staticmethod
    def _parse_show_history(text: str) -> Optional[Dict]:
        """
        Parse "show_history" intent.
        Patterns: "היסטוריה", "הראה לי נסיעות קודמות"
        """
        history_patterns = [
            r'היסטוריה',
            r'הראה\s+לי',
            r'נסיעות\s+קודמות',
            r'נסיעות\s+קודמות'
        ]
        
        for pattern in history_patterns:
            if re.search(pattern, text):
                return {
                    'intent': 'show_history',
                    'confidence': 0.9
                }
        
        return None

