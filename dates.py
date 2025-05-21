from datetime import datetime
import holidays

FIVE_PM = '17:00:00'
TEN_AM = '10:00:00'
ONE_SECOND_BEFORE_MIDNIGHT = '23:59:59'

US_ISO_CODE = 'US'

def is_a_weekend(date: datetime) -> bool:
  return date.weekday() in [5, 6]

def is_us_holiday(date: datetime) -> bool:
  us_holidays = holidays.country_holidays(US_ISO_CODE)

  return date in us_holidays

def get_time_in_seconds_until_target_time(current_time: datetime, target_time_string: str) -> float:
  target_time = datetime.strptime(target_time_string, "%H:%M:%S").time()
  target_datetime = datetime.combine(current_time.date(), target_time)
  
  return (target_datetime - current_time).total_seconds()

