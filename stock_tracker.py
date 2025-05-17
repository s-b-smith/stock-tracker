import websocket
import json
from pynput import keyboard
import threading
import datetime

# MESSAGE RECEIVED FORMAT
#   {
#   "data": [
#     {
#       "p": 7296.89,
#       "s": "BINANCE:BTCUSDT",
#       "t": 1575526691134,
#       "v": 0.011467
#     }
#   ],
#   "type": "trade"
# }

api_key = "FILL IN KEY"
stock_ticker = None
url = f"wss://ws.finnhub.io?token={api_key}"

previousPrice = 0.0
ws = None

def printn(message):
   print(f"{message}\n")

def extractPrice(messageRaw):
  message = json.loads(messageRaw)
  if (message['type'] is None or message['type'] != 'trade'):
     if (message['type'] == 'ping'):
        printn("Pinged...")
     return None
  
  data = message['data']
  if (not isinstance(data, list) or data.count == 0):
     return None
  
  return float(data[-1]['p']);

def on_message(ws, message):
  global previousPrice
  # printn("DEBUG, message: " + message)
  
  price = extractPrice(message)
  if (price is None):
    return

  now = datetime.datetime.now()
  currentTime12hr = now.strftime("%I:%M:%S %p")
  print(currentTime12hr)
  if (price > previousPrice):
    print("💲💲💲💲💲💲")
  elif (price == previousPrice):
    print("----------")
  else:
    print("🔻🔻🔻🔻🔻🔻")

  previousPrice = price
  printn(price)

def on_open(ws):
  subscribe_event = {
    "type": "subscribe",
    "symbol": stock_ticker
  }
  ws.send(json.dumps(subscribe_event))
  printn("Connected and subscribed")

def on_close(ws, close_status_code, close_msg):
  print("Closed connection")
  if close_status_code or close_msg:
        print("Close status code: " + str(close_status_code))
        print("Close message: " + str(close_msg))

def on_error(ws, error):
  printn(f"Error: {error}")

def on_key_press(key):
    global ws
    if key == keyboard.Key.ctrl_r:
        print("Quitting...")
        if ws:
            ws.close()
        return False
    
def create_websocket_thread():
  global ws
   # websocket.enableTrace(True)
  ws = websocket.WebSocketApp(url,
                           on_message = on_message,
                           on_open = on_open,
                           on_close = on_close,
                           on_error = on_error)
  ws.run_forever()


if __name__ == "__main__":
  stock_ticker = input("Enter the stock symbol to track: ")

  websocket_thread = threading.Thread(target=create_websocket_thread)
  websocket_thread.daemon = True
  websocket_thread.start()

  with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()

  print("Program terminated gracefully")
    