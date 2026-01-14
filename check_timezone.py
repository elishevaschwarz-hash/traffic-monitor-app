#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check timezone issues"""

from datetime import datetime
import pytz
import time

print("System time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("System timezone:", time.tzname)

tz_il = pytz.timezone('Asia/Jerusalem')
tz_stl = pytz.timezone('America/Chicago')

now_utc = datetime.utcnow()
now_il = pytz.utc.localize(now_utc).astimezone(tz_il)
now_stl = pytz.utc.localize(now_utc).astimezone(tz_stl)

print(f"Israel time (Asia/Jerusalem): {now_il.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"St. Louis time (America/Chicago): {now_stl.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"UTC time: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "="*60)
print("The app is configured to use: Asia/Jerusalem")
print("Current app time would be:", now_il.strftime('%Y-%m-%d %H:%M:%S'))

