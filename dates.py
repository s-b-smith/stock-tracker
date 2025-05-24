from datetime import datetime
from typing import List
from enum import Enum
import holidays

FIVE_PM = '17:00:00'
TEN_AM = '10:00:00'
ONE_SECOND_BEFORE_MIDNIGHT = '23:59:59'

US_ISO_CODE = 'US'

class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

def is_a_weekend(date: datetime) -> bool:
  return is_a_day_of_week(date, [DayOfWeek.SATURDAY, DayOfWeek.SUNDAY])

def is_a_day_of_week(date: datetime, days_of_week: List[DayOfWeek]):
  return date.weekday() in [day.value for day in days_of_week]

def is_us_holiday(date: datetime) -> bool:
  us_holidays = holidays.country_holidays(US_ISO_CODE)

  return date in us_holidays

def get_time_in_seconds_until_target_time(current_time: datetime, target_time_string: str) -> float:
  target_time = datetime.strptime(target_time_string, "%H:%M:%S").time()
  target_datetime = datetime.combine(current_time.date(), target_time)
  
  return (target_datetime - current_time).total_seconds()

