import math
import requests
import json
import time
import win32api
import win32con

# Move mouse by a given X, Y Value
def move_mouse_by(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)

def get_field_heading():
    url = 'http://localhost:8111/map_obj.json'  
    response = requests.get(url)

    if response.status_code == 200:
        json_data = json.loads(response.text)
        # Extract x and y values where icon is "Player"
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        field = next((obj for obj in json_data if obj["type"] == "airfield" and obj["color"] == "#fa0C00"), None)
        if player and field:
            x = player["x"]
            y = player["y"]
            dx = player["dx"]
            dy = player["dy"]
            field_x = field["sx"]
            field_y = field["sy"]
            
            # Calculate the angle between the current direction and the target location
            angle = math.atan2(field_y - y, field_x - x)

            # Calculate the plane's facing angle
            facing_angle = math.atan2(dy, dx)

            # Calculate the angle to turn towards the airfield
            turn_angle = angle - facing_angle

            # Convert the angle from radians to degrees
            angle_degrees = math.degrees(turn_angle)

            print(angle_degrees)

        
        # Adjust your heading by moving the mouse
        #move_mouse_by(int(0 - angle_degrees * 5), 0)  # Replace with your mouse control function

def adjust_heading():
    vals = get_field_heading()
    if vals:
        x, y, dx, dy, field_x, field_y = get_field_heading()

        

# Example usage
while True:
    adjust_heading()
    time.sleep(0.5)
