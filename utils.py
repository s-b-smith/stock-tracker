import os
import threading
from pynput import keyboard

CTRL_C = '\x03'

seconds_in_an_hour = 3600
seconds_in_a_day = seconds_in_an_hour * 24

def printn(string: str) -> None:
    print(string + "\n")

def create_esc_exit_listener(with_web_socket: bool = False) -> None:
    def on_key_press(key) -> None:
        try:
            if key == keyboard.Key.esc:
                print("\nQuitting...")
                if (with_web_socket):
                    global ws
                    if ws:
                        ws.close()
                os._exit(0)
        except AttributeError:
            pass

    def start_listener() -> None:
        with keyboard.Listener(on_press=on_key_press) as listener:
            listener.join()
    
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.daemon = True
    listener_thread.start()