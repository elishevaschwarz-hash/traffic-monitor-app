from models import db, User, SavedDestination
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_or_create_user(phone_number: str) -> User:
        """
        Get existing user or create a new one.
        """
        user = User.query.filter_by(phone_number=phone_number).first()
        
        if not user:
            user = User(
                phone_number=phone_number,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {phone_number}")
        else:
            user.last_active = datetime.utcnow()
            db.session.commit()
        
        return user
    
    @staticmethod
    def set_home_address(user: User, address: str, home_number: int = 1) -> tuple:
        """
        Set home address (1 or 2) for a user.
        Returns (success, message)
        """
        if home_number not in [1, 2]:
            return (False, "❌ מספר כתובת לא תקין. השתמשי ב-1 או 2.")
        
        if home_number == 1:
            user.home_address_1 = address
        else:
            user.home_address_2 = address
        
        # If this is the first address, set it as active
        if not user.get_active_home_address():
            user.active_home = home_number
        
        db.session.commit()
        
        logger.info(f"Set home address {home_number} for user {user.phone_number}: {address}")
        
        # Build response message
        message = f"✅ כתובת בית {home_number} נשמרה!\n\n"
        
        if user.home_address_1 and user.home_address_2:
            active_indicator_1 = " (פעילה)" if user.active_home == 1 else ""
            active_indicator_2 = " (פעילה)" if user.active_home == 2 else ""
            message += f"1️⃣ {user.home_address_1}{active_indicator_1}\n"
            message += f"2️⃣ {user.home_address_2}{active_indicator_2}\n\n"
            message += "כדי להחליף, שלחי: 'החלף לבית 1' או 'החלף לבית 2'"
        else:
            message += f"כתובת הבית שלך: {address}\n"
            message += "עכשיו את יכולה לבקש ממני לעקוב אחרי נסיעות. נסי:\n"
            message += "'רוצה להגיע לעבודה ב-10:00'"
        
        return (True, message)
    
    @staticmethod
    def switch_active_home(user: User, home_number: int) -> tuple:
        """
        Switch active home address (1 or 2).
        Returns (success, message)
        """
        if home_number not in [1, 2]:
            return (False, "❌ מספר כתובת לא תקין. השתמשי ב-1 או 2.")
        
        if home_number == 1 and not user.home_address_1:
            return (False, "❌ כתובת בית 1 לא מוגדרת.")
        if home_number == 2 and not user.home_address_2:
            return (False, "❌ כתובת בית 2 לא מוגדרת.")
        
        user.active_home = home_number
        db.session.commit()
        
        active_address = user.get_active_home_address()
        logger.info(f"Switched active home to {home_number} for user {user.phone_number}")
        
        return (True, f"✅ החלפתי!\n\nכתובת הבית הפעילה שלך עכשיו:\n{active_address}")
    
    @staticmethod
    def save_destination(user: User, name: str, address: str) -> tuple:
        """
        Save a destination for a user.
        If destination with same name exists, update it.
        Returns (destination_object, message)
        """
        # Check if destination with this name already exists
        existing = SavedDestination.query.filter_by(user_id=user.id, name=name).first()
        
        if existing:
            existing.address = address
            db.session.commit()
            logger.info(f"Updated destination '{name}' for user {user.phone_number}")
            return (existing, f"✅ עדכנתי את '{name}' ← {address}")
        else:
            destination = SavedDestination(
                user_id=user.id,
                name=name,
                address=address
            )
            db.session.add(destination)
            db.session.commit()
            logger.info(f"Saved destination '{name}' for user {user.phone_number}")
            return (destination, f"✅ שמרתי את '{name}' ← {address}")

