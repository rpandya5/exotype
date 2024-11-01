import socket
import pyautogui
import time
from collections import deque

localIP = "0.0.0.0"
localPort = 4210
bufferSize = 1024

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Get the screen size
screen_width, screen_height = pyautogui.size()

# Smoothing parameters
smoothing_window = 5
x_buffer = deque(maxlen=smoothing_window)
y_buffer = deque(maxlen=smoothing_window)

# Acceleration parameters
min_speed = 1
max_speed = 20
acceleration_factor = 1.5

def apply_acceleration(value):
    return min(max_speed, max(min_speed, abs(value) ** acceleration_factor)) * (1 if value >= 0 else -1)

def smooth_input(buffer, new_value):
    buffer.append(new_value)
    return sum(buffer) / len(buffer)

last_update_time = time.time()

while True:
    try:
        print("Waiting for data...")
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        
        current_time = time.time()
        dt = current_time - last_update_time
        last_update_time = current_time

        data = message.decode().split(',')
        x = int(data[0])
        y = int(data[1])
        
        # Apply smoothing
        x = smooth_input(x_buffer, x)
        y = smooth_input(y_buffer, y)
        
        # Map joystick values to cursor movement
        dx = (x - 0) / 10  # Assuming x now ranges from -100 to 100
        dy = (y - 0) / 10  # Assuming y now ranges from -100 to 100
        
        # Apply acceleration
        dx = apply_acceleration(dx)
        dy = apply_acceleration(dy)
        
        # Scale movement based on time since last update
        dx *= dt * 60  # Normalize to 60 fps
        dy *= dt * 60
        
        print(f"Raw input: x={x}, y={y}")
        print(f"Mapped movement: dx={dx:.2f}, dy={dy:.2f}")
        
        current_pos = pyautogui.position()
        print(f"Current cursor position: {current_pos}")
        
        # Ensure cursor stays within screen bounds
        new_x = max(0, min(screen_width, current_pos[0] + dx))
        new_y = max(0, min(screen_height, current_pos[1] - dy))
        
        pyautogui.moveTo(new_x, new_y)
        new_pos = pyautogui.position()
        print(f"New cursor position: {new_pos}")
        
    except Exception as e:
        print(f"Error processing data: {e}")
        time.sleep(0.1)  # Avoid rapid error logging