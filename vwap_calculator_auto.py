import sys
import pytz
import time
import copy

from datetime import datetime, timedelta
from typing import List

from vwap_calculator import Agg, getAggregateData
from stock_secrets import *
from utils import secondsInADay, printn, create_ctrl_c_exit_listener
from twilio_send_sms import send_SMS_message

TARGET_AVG = 251.00
FIVE_PM = '17:00:00'
  
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

def calculateVWAPResult(aggs: List[Agg]) -> VWAPResult:
  vwapObjs = []
  count = 0
  total = 0
  for agg in aggs:
    vwapDate = datetime.fromtimestamp(agg.timestamp / 1000.0).astimezone(pytz.utc)
    vwapValue = agg.vwap
    vwapObj = VWAP(vwapDate, vwapValue)
    vwapObjs.append(vwapObj)

    count += 1
    total += vwapValue

  if (count > 0):
    avg = total / count
  else:
    avg = 0.0

  return VWAPResult(vwapObjs, avg)

def getVWAPDataString(vwapResult: VWAPResult) -> str:
  data = ''

  count = 0
  for vwap in vwapResult.vwaps:
    vwapDate = vwap.date
    vwapDateFormatted = vwapDate.strftime("%m/%d")
    vwapValue = vwap.value

    count += 1
    data += f"{count}. {vwapDateFormatted} - ${vwapValue}\n"

  data += f"\nAVG: ${vwapResult.avg}"

  return data

def getTimeInSecondsUntil5PM(currentTime: datetime) -> float:
  target_time = datetime.strptime(FIVE_PM, "%H:%M:%S").time()
  target_datetime = datetime.combine(currentTime.date(), target_time)
  
  return (target_datetime - currentTime).total_seconds()

if __name__ == "__main__":
  create_ctrl_c_exit_listener()

  if len(sys.argv) > 1:
    start_date = sys.argv[1]
  else:
    start_date = input("Enter the start date: ")
  start_date = datetime.strptime(start_date, "%Y-%m-%d")

  print()
  while (True):
    iterationTimestamp = datetime.now()
    iterationTimeString = iterationTimestamp.strftime("%m/%d/%Y %H:%M:%S")

    isAWeekend = iterationTimestamp.weekday() in [5, 6]
    if (isAWeekend):
      print(iterationTimeString)
      printn("Waiting til Monday...")
      time.sleep(secondsInADay)
      continue

    isAfter5PM = iterationTimestamp.hour >= 17
    if (isAfter5PM):
      print(iterationTimeString)
      printn("Waiting til tomorrow...")
      time.sleep(secondsInADay / 2)
      continue

    timeInSecondsUntil5PM = getTimeInSecondsUntil5PM(iterationTimestamp)
    print(iterationTimeString)
    printn("Waiting til 5pm...")
    time.sleep(timeInSecondsUntil5PM)

    stagedResult = VWAPResult([], TARGET_AVG)
    while (stagedResult.avg >= TARGET_AVG):
      finalResult = copy.deepcopy(stagedResult)

      aggData = getAggregateData(start_date.strftime("%Y-%m-%d"))
      stagedResult = calculateVWAPResult(aggData)
      start_date = start_date - timedelta(days=1)
    start_date = start_date + timedelta(days=2)

    stringResult = getVWAPDataString(finalResult)
    print(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
    printn(stringResult)
    # TODO: Waiting on verification for this to work
    send_SMS_message(stringResult, twilio_to_phone_number)