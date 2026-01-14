from datetime import datetime
import pytz

tz_stl = pytz.timezone('America/Chicago')
now_stl = datetime.now(tz_stl)
print(f'Current St. Louis time: {now_stl.strftime("%Y-%m-%d %H:%M:%S")}')
print(f'Current hour in St. Louis: {now_stl.hour}:{now_stl.minute:02d}')

