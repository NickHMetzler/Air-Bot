# Naval_Bot.py
# Plays War Thunder Naval to automatically generate Silver Lions (In Game Currency)
# 2023-06-01
# Nicolas Metzler

# Import Statements
from pyautogui import *
import pyautogui
import time
import keyboard
import numpy as np
import win32api, win32con
import ctypes
import random
import os
import threading
import requests
import json
import math
import tkinter as tk
from tkinter import messagebox
import datetime

# Allow the use of relative paths
os.chdir(os.path.dirname(__file__))
script_folder = os.path.dirname(__file__)
# Change the permissions of all files in the script's folder to allow all users to read and write to them
for file in os.listdir(script_folder):
    file_path = os.path.join(script_folder, file)
    os.chmod(file_path, 0o666)

# PyAutoGui Failsafe off
pyautogui.FAILSAFE = False


###############################
#          Constants          #
###############################

# Char/Str to Scancode for Bot Game Inputs
# https://kbdlayout.info/kbdusx/scancodes
with open('data/keycodes.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Evaluate the contents as Python code
KEYS = eval(contents)

# Cruising Altitude for each Map
with open('data/heights.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Evaluate the contents as Python code
HEIGHTS = eval(contents)

# Bombing Distances for each Map
with open('data/distances.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Evaluate the contents as Python code
DISTANCES = eval(contents)

# Get User's KeyBinds from file
with open('data/keybinds.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Evaluate the contents as Python code
KEYBINDS = eval(contents)

###############################
#   C Struct Redefinitions    #
###############################

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def pressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def releaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, 
ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


#######################
#   Image Functions   #
#######################

# Temp Function (Screenshots the screen)
def screenshot_screen():
    folder_path = 'assets/screenshots/'
    # Get a list of existing files in the folder
    existing_files = os.listdir(folder_path)
    # Find the maximum number in the existing file names
    max_number = 0
    for file_name in existing_files:
        if file_name.startswith('screenshot') and file_name.endswith('.png'):
            try:
                number = int(file_name[10:14])  # Extract the number part
                max_number = max(max_number, number)
            except ValueError:
                pass
    # Increment the number and format it with leading zeros
    new_number = str(max_number + 1).zfill(4)
    # Create the new file name
    file_name = f'screenshot{new_number}.png'
    # Take the screenshot
    myScreenshot = pyautogui.screenshot()
    # Save the screenshot with the new file name
    myScreenshot.save(os.path.join(folder_path, file_name))

# Check if given image is on the screen
def is_image_on_screen(image_path, grayscale=True, confidence=0.7):
    try:
        position = pyautogui.locateOnScreen(image_path, grayscale=grayscale, confidence=confidence)
        if position is not None:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Wait on - Waiting on the image to leave
def wait_on(image_path, grayscale=True, confidence=0.7):
    while is_image_on_screen(image_path, grayscale, confidence):
        time.sleep(0.2)

# Wait for - Waiting for the image to appear
def wait_for(image_path, grayscale=True, confidence=0.7):
    while is_image_on_screen(image_path, grayscale, confidence) == False:
        time.sleep(0.2)

# Function to calculate the elapsed time
def get_elapsed_time(startTime):
    current_time = time.time()
    elapsed_time = current_time - startTime
    return elapsed_time

#######################
#   Query Functions   #
#######################

def calculate_ec_base():
    url = 'http://localhost:8111/map_obj.json'
    response = requests.get(url)
    
    if response.status_code == 200:
        json_data = json.loads(response.text)
        # Extract x and y values where icon is "Player"
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        
        if player:
            x = player["x"]
            y = player["y"]
            dx = player["dx"]
            dy = player["dy"]
        else:
            # Handle the case when player is None
            x = 0  # Set default x coordinate
            y = 0  # Set default y coordinate
            dx = 0  # Set default x velocity
            dy = 0  # Set default y velocity
        
        points = []
        for obj in json_data:
            if obj["type"] == "bombing_point":
                point_loc = (obj["x"], obj["y"])
                points.append(point_loc)

        if x is not None:
            min_index = 0
            min_angle = 180.0
            index = 0
            for point in points:
                angle = math.atan2(point[1] - y, point[0] - x)
                # Calculate the plane's facing angle
                facing_angle = math.atan2(dy, dx)
                # Calculate the angle to turn towards the airfield
                turn_angle = angle - facing_angle
                # Convert the angle from radians to degrees
                angle_degrees = math.degrees(turn_angle)

                # Check if the angle is within the desired range
                if -180 <= angle_degrees <= 180:
                    # Calculate the absolute difference between the current angle and 0
                    abs_difference = abs(angle_degrees)
                    # Check if the absolute difference is less than the minimum angle found so far
                    if abs_difference < min_angle:
                        min_angle = abs_difference
                        min_index = index
            print(f'Base Chosen')
            return points[min_index]

# Returns the angle toward the enemy airfield
def get_base_info(map, base, ec=False):
    url = 'http://localhost:8111/map_obj.json'  
    response = requests.get(url)
    base_loc = base
    if response.status_code == 200:
        json_data = json.loads(response.text)
        # Extract x and y values where icon is "Player"
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        if player:
            x = player["x"]
            y = player["y"]
            dx = player["dx"]
            dy = player["dy"]
        else:
            # Handle the case when player is None
            x = 0  # Set default x coordinate
            y = 0  # Set default y coordinate
            dx = 0  # Set default x velocity
            dy = 0  # Set default y velocity
        points = []
        for obj in json_data:
            if obj["type"] == "bombing_point":
                points.append(obj["x"])
        points_sorted = sorted(set(points))
        if x is not None:
            if base_loc == []:
            # Pick the index based on map
                if map == 'CityALT':
                    index = 2
                elif map == 'GolanHeightsALT' or map == 'SpainALT' or map == 'SinaiALT' or map == 'VietnamALT':
                    index = 3
                else:
                    index = 1
                if index < len(points_sorted):
                    chosen_point = points_sorted[index] 
                    point_x = None
                    point_y = None
                    for obj in json_data:
                        if obj["type"] == "bombing_point" and obj["x"] == chosen_point:
                            point_x = obj["x"]
                            point_y = obj["y"]
                            base_loc = (point_x, point_y)
            
            angle = math.atan2(base_loc[1] - y, base_loc[0] - x)

            # Calculate the plane's facing angle
            facing_angle = math.atan2(dy, dx)

            # Calculate the angle to turn towards the airfield
            turn_angle = angle - facing_angle

            # Convert the angle from radians to degrees
            angle_degrees = math.degrees(turn_angle)
            distance = math.sqrt((x - base_loc[0])**2 + (y - base_loc[1])**2)
            print(f'Base is heading: {angle_degrees}')
            print(f'Base distance is: {distance}')
            return angle_degrees, distance, base_loc
         
        
def get_field_info():
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
            field_x = (field["sx"] + field["ex"])/2
            field_y = (field["sy"] + field["ey"])/2
            
            # Calculate the angle between the current direction and the target location
            angle = math.atan2(field_y - y, field_x - x)

            # Calculate the plane's facing angle
            facing_angle = math.atan2(dy, dx)

            # Calculate the angle to turn towards the airfield
            turn_angle = angle - facing_angle

            # Convert the angle from radians to degrees
            angle_degrees = math.degrees(turn_angle)
            distance = math.sqrt((x - field_x)**2 + (y - field_y)**2)
            print(f'Airfield is heading: {angle_degrees}')
            print(f'Airfield distance is: {distance}')
            return angle_degrees, distance
            

# Returns the current Height and Rate of Climb
def get_attitude():
    url = 'http://localhost:8111/state'
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON string
        json_data = json.loads(response.text)

        # Access the value of "H, m"
        return_data = (json_data["H, m"], json_data["Vy, m/s"])
        # print(f'Height is: {return_data[0]}m\nRate of Climb is: {return_data[1]}')
        return return_data


# Returns the speed in Mach
def get_mach():
    url = 'http://localhost:8111/indicators'
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON string
        json_data = json.loads(response.text)

        # Access the value of "H, m"
        return_data = json_data["mach"]
        #print(f'Plane is at Mach {return_data}')
        return return_data

#########################
#   Control Functions   #
#########################

# Controls the pitch/attitude of the plane
def pitch_control(target_height, curr_height, attitude):
    if curr_height > target_height + 100 and attitude > 20.0:
        move_mouse_by(0, 60)
    elif curr_height < target_height and attitude < -20.0:
        move_mouse_by(0, -60)
    elif curr_height > target_height + 100 and attitude > 10.0:
        move_mouse_by(0, 30)
    elif curr_height < target_height and attitude < -10.0:
        move_mouse_by(0, -30)
    elif curr_height > target_height + 100 and attitude > 5.0:
        move_mouse_by(0, 20)
    elif curr_height < target_height and attitude < -5.0:
        move_mouse_by(0, -20)
    elif curr_height > target_height + 25 and attitude > 0.0:
        move_mouse_by(0, 7)
    elif curr_height < target_height and attitude < 0.0:
        move_mouse_by(0, -7)
    elif curr_height < target_height + 25 and attitude > target_height and attitude > 0.1:
        move_mouse_by(0, 7)
    elif curr_height < target_height + 25 and attitude > target_height and attitude < -0.1:
        move_mouse_by(0, -7)

# Click mouse
def click_mouse():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0) 
    time.sleep(np.random.uniform(0.7,1.2)) 
    win32api.mouse_event(win32con. MOUSEEVENTF_LEFTUP, 0, 0)

# Move mouse to given X, Y Coordinates
def move_mouse_to(x, y):
    pyautogui.moveTo(x, y)

# Move mouse by a given X, Y Value
def move_mouse_by(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)

# Move the Mouse to a given image
def move_mouse_to_image(image_path):
    image = pyautogui.locateCenterOnScreen(image_path, grayscale=False, confidence=0.75)
    if image != None:
        move_mouse_to(image[0], image[1])
        time.sleep(np.random.uniform(0.9,1.2))
        return True
    else:
        return False

# Hold a given key
def hold(key):
    pressKey(KEYS[key])

# Release a given key
def release(key):
    releaseKey(KEYS[key])

# Press a given Key
def press(key):
    hold(key)
    time.sleep(np.random.uniform(0.3,0.7)) 
    release(key)

# Hold a given key for a specified amount of time
def holdFor(key, seconds):
    hold(key)
    time.sleep(seconds) 
    release(key)

# Type a given key
# Function is faster, designed for typing messages
def type(key):
    hold(key)
    time.sleep(np.random.uniform(0.1,0.3)) 
    release(key)

#########################
#   General Functions   #
#########################

# End Program
def end_program():
    # Send the signal to terminate the program
    os.kill(os.getpid(), 9)

# Bot Loop
def bot():
    while True:
        # Click 'To Battle' Button in Main Menu
        while pyautogui.locateOnScreen('assets/in_queue.png', grayscale=False, confidence=0.75) == None:
            # Do not click if the vehicle needs to be repaired
            if pyautogui.locateOnScreen('assets/trophy.png', grayscale=False, confidence=0.95) != None:
                press(KEYBINDS['enter'])
            if pyautogui.locateOnScreen('assets/repaired.png', grayscale=False, confidence=0.95) != None:
                press(KEYBINDS['enter'])
            time.sleep(0.5)
        print("CONSOLE: To Battle!")

        # Wait to Join Battle
        print('CONSOLE: Waiting in Qeue...')
        wait_for('assets/spawn.png', grayscale=False, confidence=0.8)
        
        # Check which map match is taking place on
        move_mouse_to(100, 100)
        # Temp Variable
        screenshot_val = False
        city = False
        ec = False
        if pyautogui.locateOnScreen('assets/vietnam.png', grayscale=False, confidence=0.97) != None:
            map = 'Vietnam'
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/vietnamALT.png', grayscale=False, confidence=0.96) != None:
            map = 'VietnamALT'
        elif pyautogui.locateOnScreen('assets/vietnamEC.png', grayscale=False, confidence=0.97) != None:
            map = 'VietnamEC'
            ec = True
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/spain.png', grayscale=False, confidence=0.99) != None:
            map = 'Spain'
        elif pyautogui.locateOnScreen('assets/spainALT.png', grayscale=False, confidence=0.99) != None:
            map = 'SpainALT'
        elif pyautogui.locateOnScreen('assets/spainEC.png', grayscale=False, confidence=0.97) != None:
            map = 'SpainEC'
            ec = True
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/golan_heights.png', grayscale=False, confidence=0.99) != None:
            map = 'GolanHeights'
        elif pyautogui.locateOnScreen('assets/golan_heightsALT.png', grayscale=False, confidence=0.99) != None:
            map = 'GolanHeightsALT'
        elif pyautogui.locateOnScreen('assets/sinai.png', grayscale=False, confidence=0.98) != None:
            map = 'Sinai'
        elif pyautogui.locateOnScreen('assets/sinaiALT.png', grayscale=False, confidence=0.98) != None:
            map = 'SinaiALT'
        elif pyautogui.locateOnScreen('assets/city.png', grayscale=False, confidence=0.97) != None:
            map = 'City'
            city = True
        elif pyautogui.locateOnScreen('assets/cityALT.png', grayscale=False, confidence=0.97) != None:
            map = 'CityALT'
            city = True
        elif pyautogui.locateOnScreen('assets/rocky_canyonALT.png', grayscale=False, confidence=0.97) != None:
            map = 'RockyCanyonALT'
            ec = True
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/afghanistan.png', grayscale=False, confidence=0.97) != None:
            ec = True
            map = 'RockyCanyonALT'
        else:
            screenshot_val = True
        # Temp condition
        if screenshot_val == True: 
            screenshot_screen()

        
        # In Battle, click the Spawn In button
        press(KEYBINDS['enter'])
        print("CONSOLE: Spawn Button Clicked") 
        time.sleep(1)
            

        print(f'CONSOLE: Map is {map}')

        # Pitch values
        pitch_value = 184
        downVal = int(pitch_value/8)

        # Take off/spawn procedure
        battle_time = time.time()
        if city == False:
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn on Airfield')
            wait_on('assets/cancel_spawn.png')
            print('CONSOLE: Spawned in')
            # Throttle up, then pitch up
            holdFor(KEYBINDS['throttleUp'], 4)
            move_mouse_by(0, -pitch_value)
        
            # Start CCRP and choose base
            print('CONSOLE: Activating CCRP')
            press(KEYBINDS['ccrp'])

            # Retract gear when taken off
            ground = get_attitude()[0]
            height = get_attitude()[0]
            while height <= ground + 10:
                height = get_attitude()[0]
            print('CONSOLE: Retracting Landing Gear')
            press(KEYBINDS['gear'])

            # Choose base target
            print('CONSOLE: Choosing Target Base')
            press(KEYBINDS['ccrp'])
            while pyautogui.locateOnScreen('assets/centreline.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/j_out.png', grayscale=False, confidence=0.95) == None and height < HEIGHTS[map]/2:
                height = get_attitude()[0]
                time.sleep(0.1)
            # Pitch down a few times
            for i in range(3):
                    move_mouse_by(0, downVal + 5)
                    time.sleep(1)
        # Air Spawn
        elif city == True:
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn In Airspawn')
            wait_on('assets/cancel_spawn.png', 0.7)
            # Afterburner
            press('w')
            # Start CCRP and choose base
            time.sleep(5)
            print('CONSOLE: Activating CCRP')
            press(KEYBINDS['ccrp'])
            time.sleep(5)
            print('CONSOLE: Choosing Target Base')
            press(KEYBINDS['ccrp'])

        # Set variables for game loop
        battle_time = time.time()
        zoom_time = 0
        base_loc = []
        zoom_flag = False
        brake_flag = False
        if city == True:
            pitch_flag = True
        else:
            pitch_flag = False
        mach_flag = False
        map_distance = DISTANCES[map]
        height = HEIGHTS[map]
        
        # Hold down the bombing button
        hold(KEYBINDS['bomb'])

        # Bombing loop
        while pyautogui.locateOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/j_out.png', grayscale=False, confidence=0.95) == None:
            # Temp Condition
            if screenshot_val == True and zoom_time == 6 and ec == True:
                screenshot_screen()
                hold(KEYBINDS['map'])
                screenshot_screen()
                release(KEYBINDS['map'])
                screenshot_val = False

            # Locate the CCRP line and move the mouse towards it
            base_info = get_base_info(map, base_loc)
            location = pyautogui.locateOnScreen('assets/centreline.png', grayscale=False, confidence=0.7)
            if location is not None:
                center_x, center_y= pyautogui.center(location)
                
                # Get the screen's center coordinates
                screen_width, screen_height = pyautogui.size()
                screen_center_x = screen_width // 2
                
                # Calculate the distance between the target center and the screen's center
                distance_x = int((center_x - screen_center_x)/2)
                move_mouse_by(distance_x, 0)
            elif brake_flag == True and base_info[1] > last_dist:
                # Release the bombing button
                release(KEYBINDS['bomb'])
                break
            elif base_info is not None and pitch_flag == True:
                move_mouse_by(int(base_info[0] * 10), 0)
            last_dist = base_info[1]

            # Wait 6 cycles before zooming in
            if zoom_time >= 6 and zoom_flag == False:
                press(KEYBINDS['zoom'])
                zoom_flag = True
            elif zoom_time >= 13 and ec == True:
                base_loc = calculate_ec_base()
            zoom_time += 1
            
            # Release flares while subsonic
            if brake_flag == True:
                print('CONSOLE: Popping Flares')
                pyautogui.scroll(-2)
                pyautogui.scroll(2)
                
            # Check if the airbrake can be deactivated
            if brake_flag == True and mach_flag == False:
                mach = get_mach()
                if mach < 1.0:
                    print('CONSOLE: Retracting Airbrake')
                    press(KEYBINDS['airbrake'])
                    mach_flag = True

            # Slowly pitch the plane back to level
            attitude = get_attitude()
            if city == False and pitch_flag == False and attitude[0] > height - 10:
                for i in range(2):
                    move_mouse_by(0, downVal + 5)
                    time.sleep(1)
                pitch_flag = True

            # Hit the airbrake and turn off afterburner when close to the base
            if base_info is not None:
                base_loc = base_info[2]
                if brake_flag == False and base_info[1] <= map_distance:
                    print('CONSOLE: Deploying Airbrake')
                    press(KEYBINDS['airbrake'])
                    pyautogui.scroll(-2) 
                    brake_flag = True

            # Maintain level flight
            if pitch_flag == True and brake_flag == False:
                pitch_control(height, attitude[0], attitude[1])
            
        # After Bombing pitch up, throttle down, and bait enemies
        time.sleep(1)
        if mach_flag == False:
            press(KEYBINDS['airbrake'])
        brake_flag = False
        press(KEYBINDS['smoke'])
        time.sleep(np.random.uniform(1.2,1.7))

        # Turn right until dead
        while pyautogui.locateOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/j_out.png', grayscale=False, confidence=0.95) == None:
            attitude = get_attitude()
            pitch_control(height + 1000, attitude[0], attitude[1])
            field_data = get_field_info()
            if field_data is not None:
                move_mouse_by(int(field_data[0] * 10), 0)
                if field_data[1] <= 0.07 and brake_flag == False:
                    press(KEYBINDS['airbrake'])
                    move_mouse_by(0, 200)
                    brake_flag = True
            elapsed_time = get_elapsed_time(battle_time)
            # J out if 10 minutes have passed
            if elapsed_time >= 600:
                holdFor('j', 4)

        # Vehicle has been destroyed
        if pyautogui.locateOnScreen('assets/j_out.png', grayscale=False, confidence=0.95) != None:
            holdFor('j', 4)
            print('CONSOLE: Aircraft Downed, Returning to Hangar')

            # Click 'Return To Hangar' Button
            wait_for('assets/return_to_hangar.png', False, 0.75)
            while pyautogui.locateCenterOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/return_to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(2)
            
            # Wait for 'To Hangar' Button
            wait_for('assets/to_hangar.png', False, 0.75)
            # Click 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(2)
                
            
        elif pyautogui.locateCenterOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.75) != None:
            print('CONSOLE: Aircraft Downed, Returning to Hangar')
            while pyautogui.locateCenterOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/return_to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(2)

            # Wait for 'To Hangar' Button
            wait_for('assets/to_hangar.png', False, 0.75)
            # Click 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(2)

        # Match has ended
        else:
            print('CONSOLE: Match Ended, Returning to Hangar')
            # Click 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(2)

# Main function
def main():
    # Function to start the bot
    def start_bot():
        # Prompt the user to Alt + Tab to War Thunder
        messagebox.showinfo("Alt + Tab", "Please Alt + Tab to War Thunder")

        # Allow time for user to Alt + Tab
        time.sleep(5)

        # Create a thread for the bot
        bot_thread = threading.Thread(target=bot)

        # Start the bot
        bot_thread.start()

        launch_time = time.time()

        # Check if the user presses key 'q' then quit the program
        while True:
            if keyboard.is_pressed('q'):
                # handle the 'q' key press
                print("CONSOLE: Exiting program")
                # Quit the program
                time.sleep(1)
                elapsed_time = get_elapsed_time(launch_time)
                # Convert the elapsed time into a timedelta object
                time_delta = datetime.timedelta(seconds=elapsed_time)

                # Get the hours, minutes, and seconds from the timedelta object
                hours = time_delta.seconds // 3600
                minutes = (time_delta.seconds % 3600) // 60
                seconds = time_delta.seconds % 60

                # Format the time as HH:MM:SS
                formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                # Print the formatted time
                print(f'Bot was running for: {formatted_time}')
                end_program()

    # Create the main window
    window = tk.Tk()
    window.title("Nicks War Thunder Air Bot 1.6")
    window.geometry("800x500")
    window.configure(bg="#333333")

    # Load the image
    image_path = "assets/icons/icon.png"
    image = tk.PhotoImage(file=image_path)

    # Create a label widget for the image
    image_label = tk.Label(window, image=image, bg="#333333")
    image_label.pack(pady=20)

    # Create the title label
    title_label = tk.Label(window, text="Welcome to Nicks War Thunder Air Bot 1.6", font=("Arial", 20), bg="#333333", fg="#ffffff")
    title_label.pack(pady=10)

    # Create the setup instructions label
    instructions_label = tk.Label(window, text="Setup Instructions:\n1. Check the KeyBinds file and ensure that your keybinds are set up correctly\n2. Go to Hangar and have the Kfir Canard (Israel) selected\n3. Select 'Air Realistic Battles'\n\nTo end the program, press and hold 'q' at any time", font=("Arial", 16), bg="#333333", fg="#ffffff")
    instructions_label.pack(pady=7)

    # Create the Start Bot button
    start_button = tk.Button(window, text="Start Bot", font=("Arial", 16), command=start_bot)
    start_button.pack(pady=10)

    # Start the GUI main loop
    window.mainloop()


# Start the main thread
if __name__ == "__main__":
    main()
     
            