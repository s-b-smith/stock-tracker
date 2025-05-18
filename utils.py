import os
import threading
from pynput import keyboard

seconds_in_an_hour = 3600
seconds_in_a_day = seconds_in_an_hour * 24

def printn(string: str):
    print(string + "\n")

def create_ctrl_c_exit_listener(with_web_socket: bool = False):
    def on_key_press(key):
        try:
            if key.char == '\x03':
                print("\nQuitting...")
                if (with_web_socket):
                    global ws
                    if ws is not None:
                        ws.close()
                os._exit(0)
        except AttributeError:
            pass

    def start_listener():
        with keyboard.Listener(on_press=on_key_press) as listener:
            listener.join()
    
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.daemon = True
    listener_thread.start()