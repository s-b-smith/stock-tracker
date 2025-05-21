import sys
import pytz
import time
import copy

from datetime import datetime, timedelta
from typing import List

from vwap_calculator import Agg, get_aggregate_data
from stock_secrets import *
from utils import printn, create_esc_exit_listener
from twilio_send_sms import send_SMS_message
from send_email import send_email_to_myself
from dates import *

TARGET_AVG = 251.00
  
class VWAP:
  date: datetime
  value: float

  def __init__(self, date: datetime, value: float):
    self.date = date
    self.value = value

class VWAPResult:
  vwaps: List[VWAP]
  avg: float

  def __init__(self, vwaps: List[VWAP], avg: float):
    self.vwaps = vwaps
    self.avg = avg

def calculate_VWAP_result(aggs: List[Agg]) -> VWAPResult:
  vwap_objs = []
  count = 0
  total = 0
  for agg in aggs:
    vwap_date = datetime.fromtimestamp(agg.timestamp / 1000.0).astimezone(pytz.utc)
    vwap_value = agg.vwap
    vwap_obj = VWAP(vwap_date, vwap_value)
    vwap_objs.append(vwap_obj)

    count += 1
    total += vwap_value

  if (count > 0):
    avg = total / count
  else:
    avg = 0.0

  return VWAPResult(vwap_objs, avg)

def calculate_vest_date(count: int) -> str:
  est_vest_date = datetime.today()
  while (count < 20):
    is_weekend = is_a_weekend(est_vest_date)
    is_holiday = is_us_holiday(est_vest_date)

    est_vest_date = est_vest_date + timedelta(days=1)
    if (not is_weekend and not is_holiday):
      count += 1
  
  return est_vest_date.strftime("%m/%d")

def get_VWAP_data_string(vwap_result: VWAPResult) -> str:
  data = ''

  count = 0
  for vwap in vwap_result.vwaps:
    vwap_date = vwap.date
    vwap_date_formatted = vwap_date.strftime("%m/%d")
    vwap_value = vwap.value

    count += 1
    data += f"{count}. {vwap_date_formatted} - ${vwap_value}\n"

  data += f"\nAVG: ${vwap_result.avg}"

  estimated_vest_date = calculate_vest_date(count)
  data += f"\nEST VEST DATE: {estimated_vest_date}"

  return data

if __name__ == "__main__":
  create_esc_exit_listener()

  if len(sys.argv) > 1:
    start_date = sys.argv[1]
  else:
    start_date = input("Enter the start date: ")
  start_date = datetime.strptime(start_date, "%Y-%m-%d")

  print()
  while (True):
    iteration_timestamp = datetime.now()
    iteration_time_string = iteration_timestamp.strftime("%m/%d/%Y %H:%M:%S")

    is_weekend = is_a_weekend(iteration_timestamp)
    is_after_10AM = iteration_timestamp.hour >= 10
    if (is_weekend or is_after_10AM):
      time_in_seconds_until_midnight = get_time_in_seconds_until_target_time(iteration_timestamp, JUST_BEFORE_MIDNIGHT) + 1

      print(iteration_time_string)
      printn("Waiting til tomorrow...")
      time.sleep(time_in_seconds_until_midnight)
      continue

    time_in_seconds_until_10AM = get_time_in_seconds_until_target_time(iteration_timestamp, TEN_AM)
    print(iteration_time_string)
    printn("Waiting til 10am...")
    time.sleep(time_in_seconds_until_10AM)

    avg_has_dropped_below_target = None
    avg_found = True

    staged_result = VWAPResult([], TARGET_AVG)
    while (staged_result.avg >= TARGET_AVG):
      if (avg_has_dropped_below_target is None):
        avg_has_dropped_below_target = True
      elif (avg_has_dropped_below_target):
        avg_has_dropped_below_target = False

      final_result = copy.deepcopy(staged_result)

      agg_data = get_aggregate_data(start_date.strftime("%Y-%m-%d"))
      staged_result = calculate_VWAP_result(agg_data)
      start_date = start_date - timedelta(days=1)
    start_date = start_date + timedelta(days=2)

    if (avg_has_dropped_below_target):
      staged_result = VWAPResult([], TARGET_AVG)
      final_result = copy.deepcopy(staged_result)
      # Only check 2 days after original start date, quit if target avg isn't found
      avg_found = False
      for i in range(2):
        agg_data = get_aggregate_data(start_date.strftime("%Y-%m-%d"))
        staged_result = calculate_VWAP_result(agg_data)
        if (staged_result.avg >= TARGET_AVG):
          avg_found = True
          final_result = copy.deepcopy(staged_result)
          break

        start_date = start_date + timedelta(days=1)

    if (not avg_found):
      string_result = "Couldn't calculate date range with target average...please evaluate and restart"
    else:
      string_result = get_VWAP_data_string(final_result)
    print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
    printn(string_result)
    # TODO: Waiting on verification for this to work
    # send_SMS_message(string_result, twilio_to_phone_number)
    send_email_to_myself(string_result, f"{iteration_timestamp.strftime("%m/%d")} VWAP Update")