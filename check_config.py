#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to check configuration"""

from config import Config

print("=" * 50)
print("Checking Configuration...")
print("=" * 50)

checks = {
    'Twilio Account SID': Config.TWILIO_ACCOUNT_SID,
    'Twilio Auth Token': Config.TWILIO_AUTH_TOKEN,
    'Twilio WhatsApp Number': Config.TWILIO_WHATSAPP_NUMBER,
    'Google Maps API Key': Config.GOOGLE_MAPS_API_KEY,
    'Secret Key': Config.SECRET_KEY,
}

all_ok = True

for name, value in checks.items():
    if not value:
        print(f"[X] {name}: Missing")
        all_ok = False
    elif 'your_' in str(value) or 'here' in str(value):
        print(f"[!] {name}: Still has placeholder value")
        all_ok = False
    else:
        # Show first/last few chars for security
        if 'Token' in name or 'Key' in name:
            masked = f"{str(value)[:4]}...{str(value)[-4:]}" if len(str(value)) > 8 else "***"
            print(f"[OK] {name}: {masked}")
        else:
            print(f"[OK] {name}: Set")

print("=" * 50)
if all_ok:
    print("[OK] All configuration values are set correctly!")
else:
    print("[!] Some values need to be updated in .env file")
print("=" * 50)

