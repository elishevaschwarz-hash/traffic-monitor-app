import re
from typing import List, Optional
from models.saved_destination import SavedDestination

def normalize_hebrew_text(text: str) -> str:
    """
    Normalize Hebrew text: remove diacritics, normalize whitespace, lowercase.
    """
    if not text:
        return ""
    
    # Remove Hebrew diacritics (nikud)
    # Basic Hebrew characters range: \u0590-\u05FF
    # Remove combining diacritical marks: \u0591-\u05C7 (most nikud)
    text = re.sub(r'[\u0591-\u05C7]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip and lowercase
    text = text.strip().lower()
    
    return text

def extract_destination_name(text: str, saved_destinations: List[SavedDestination]) -> Optional[str]:
    """
    Extract destination name from text by matching against saved destinations.
    Returns the address if found, None otherwise.
    """
    if not text or not saved_destinations:
        return None
    
    normalized_text = normalize_hebrew_text(text)
    
    # Try exact match first
    for dest in saved_destinations:
        normalized_name = normalize_hebrew_text(dest.name)
        if normalized_name == normalized_text or normalized_name in normalized_text:
            return dest.address
    
    # Try partial match
    for dest in saved_destinations:
        normalized_name = normalize_hebrew_text(dest.name)
        if normalized_name in normalized_text or normalized_text in normalized_name:
            return dest.address
    
    return None

def hebrew_number_words_to_digits(text: str) -> str:
    """
    Convert Hebrew number words to digits.
    Examples: "עשר" -> "10", "חצי עשר" -> "09:30"
    """
    if not text:
        return text
    
    # Hebrew number words mapping
    number_map = {
        'אחת': '1', 'אחד': '1',
        'שתיים': '2', 'שניים': '2',
        'שלוש': '3', 'שלושה': '3',
        'ארבע': '4', 'ארבעה': '4',
        'חמש': '5', 'חמישה': '5',
        'שש': '6', 'שישה': '6',
        'שבע': '7', 'שבעה': '7',
        'שמונה': '8', 'שמונה': '8',
        'תשע': '9', 'תשעה': '9',
        'עשר': '10', 'עשרה': '10',
        'אחת עשרה': '11', 'אחד עשר': '11',
        'שתים עשרה': '12', 'שניים עשר': '12',
        'שלוש עשרה': '13', 'שלושה עשר': '13',
        'ארבע עשרה': '14', 'ארבעה עשר': '14',
        'חמש עשרה': '15', 'חמישה עשר': '15',
        'שש עשרה': '16', 'שישה עשר': '16',
        'שבע עשרה': '17', 'שבעה עשר': '17',
        'שמונה עשרה': '18', 'שמונה עשר': '18',
        'תשע עשרה': '19', 'תשעה עשר': '19',
        'עשרים': '20',
        'חצי': '30'
    }
    
    normalized = normalize_hebrew_text(text)
    
    # Check for "חצי [hour]"
    half_match = re.search(r'חצי\s+(\w+)', normalized)
    if half_match:
        hour_word = half_match.group(1)
        if hour_word in number_map:
            hour = int(number_map[hour_word])
            if hour > 0:
                # Return as "HH:30" format
                return f"{hour-1:02d}:30"
    
    # Direct number word replacement
    for word, digit in number_map.items():
        if word in normalized:
            normalized = normalized.replace(word, digit)
    
    return normalized

