from typing import Tuple

x_min = 0.0
x_max = 0.0
y_min = 0.0
y_max = 0.0
joystick_val = 50

def convert_joystick_to_motor_speed(x, y) -> Tuple[int, int]:
    # Assuming x and y are in the range of -50 to 50
    # Normalize x and y to the range of -1 to 1
    x_normalized = x / joystick_val
    y_normalized = y / joystick_val

    # Calculate left and right motor speeds
    if y_normalized >= 0:
        L = y_normalized + x_normalized
        R = y_normalized - x_normalized
    else:
        L = y_normalized - x_normalized
        R = y_normalized + x_normalized  

    #scale the normalized speeds to the range of -255 to 255
    L = int(L * 255)
    R = int(R * 255)

    # Ensure the speeds are within the bounds
    L = max(-255, min(255, L))
    R = max(-255, min(255, R))

    # motors need a minimum value to start moving of 0.2.
    threshold = 25 
    if abs(L) < threshold:
        L = 0
    if abs(R) < threshold:
        R = 0

    return L, R
    

# unused funtion that takes in the x and y values
# and sets the min and max variables for debuging.
def get_min_max_vales(x, y):
    global x_min, x_max, y_min, y_max    
    x_min = min(round(x_min,2), x)
    x_max = max(round(x_max,2), x)
    y_min = min(round(y_min,2), y)
    y_max = max(round(y_max,2), y)

    print(f"x_min: {x_min}, x_max: {x_max}, y_min: {y_min}, y_max: {y_max}")
            