# אפליקציית ניטור תנועה חכם - Smart Traffic Monitor App

אפליקציית Flask לניטור תנועה בזמן אמת והתראות חכמות לנסיעות דרך WhatsApp.

## התקנה

### 1. התקנת תלויות

```bash
pip install -r requirements.txt
```

### 2. הגדרת משתני סביבה

צור קובץ `.env` בתיקיית הפרויקט עם התוכן הבא:

```
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
SECRET_KEY=your-secret-key-here-change-this-in-production
FLASK_ENV=development
USE_NGROK=true
```

### 3. הגדרת Twilio

1. צור חשבון ב-[Twilio](https://www.twilio.com/)
2. קנה מספר WhatsApp או השתמש ב-Sandbox
3. העתק את `ACCOUNT_SID`, `AUTH_TOKEN`, ו-`WHATSAPP_NUMBER` לקובץ `.env`

### 4. הגדרת Google Maps API

1. צור פרויקט ב-[Google Cloud Console](https://console.cloud.google.com/)
2. הפעל את ה-APIs הבאים:
   - Directions API
   - Geocoding API
   - Distance Matrix API
3. צור API Key והעתק אותו לקובץ `.env`

## הפעלה

```bash
python app.py
```

האפליקציה תרוץ על `http://localhost:5000`

אם `USE_NGROK=true`, Ngrok יתחיל אוטומטית ותקבל URL לחשיפת השרת לאינטרנט.

## הגדרת Twilio Webhook

לאחר הפעלת האפליקציה:

1. העתק את ה-Ngrok URL שהודפס בקונסול
2. לך ל-Twilio Console → WhatsApp Sandbox (או WhatsApp Numbers)
3. הגדר Webhook URL: `https://YOUR_NGROK_URL.ngrok.io/webhook/whatsapp`
4. Method: POST

## שימוש

שלח הודעות WhatsApp למספר Twilio שלך:

- **הגדרת כתובת בית**: "הבית שלי זה Rothschild 45, Tel Aviv"
- **שמירת יעד**: "שמור Weizmann Institute בתור עבודה"
- **יצירת נסיעה**: "רוצה להגיע לעבודה ב-10:00"
- **ביטול נסיעה**: "בטל נסיעה"
- **היסטוריה**: "הראה לי היסטוריה"

## מבנה הפרויקט

```
traffic_monitor_app/
├── app.py                 # Flask application + routes
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── models/                # Database models
├── agents/                # NLP parser, traffic monitor, notifier
├── services/              # Business logic
├── utils/                 # Utilities (Google Maps, time, Hebrew)
└── data/                  # SQLite database
```

## בדיקת תקינות

```bash
curl http://localhost:5000/health
```

## לוגים

הלוגים נשמרים בקובץ `traffic_monitor.log`

