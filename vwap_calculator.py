import sys
from typing import Optional, List
from polygon import RESTClient
from datetime import date, timedelta
from stock_secrets import polygon_key

class Agg:
  "Contains aggregate data for a given ticker symbol over a given date range in a custom time window size."
  open: Optional[float] = None
  high: Optional[float] = None
  low: Optional[float] = None
  close: Optional[float] = None
  volume: Optional[float] = None
  vwap: Optional[float] = None
  timestamp: Optional[int] = None
  transactions: Optional[int] = None
  otc: Optional[bool] = None

  @staticmethod
  def from_dict(d):
    return Agg(
      d.get("o", None),
      d.get("h", None),
      d.get("l", None),
      d.get("c", None),
      d.get("v", None),
      d.get("vw", None),
      d.get("t", None),
      d.get("n", None),
      d.get("otc", None),
    )

def getAggregateData(startDate) -> List[Agg]:
  client = RESTClient(polygon_key)
  today = date.today()

  aggs = []
  for a in client.list_aggs(
    "PAYC",
    1,
    "day",
    startDate,
    today,
    sort="asc",
  ):
    aggs.append(a)

  return aggs

def printVWAPData(aggs: List[Agg]):
  count = 0
  total = 0
  for agg in aggs:
    vwapDate = date.fromtimestamp(agg.timestamp / 1000) + timedelta(days=1)
    vwapDateFormatted = vwapDate.strftime("%m/%d")
    vwapValue = agg.vwap

    count += 1
    total += vwapValue
    print(f"{count}. {vwapDateFormatted} - ${vwapValue}")

  if (count > 0):
    print(f"\nAVG: ${total / count}")


if __name__ == "__main__":
  if len(sys.argv) > 1:
    start_date = sys.argv[1]
  else:
    start_date = input("Enter the start date: ")

  data = getAggregateData(start_date)
  printVWAPData(data)