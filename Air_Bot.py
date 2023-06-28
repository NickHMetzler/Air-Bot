# Naval_Bot.py
# Plays War Thunder Naval to automatically generate Silver Lions (In Game Currency)
# 2023-06-18
# Nicolas Metzler

# Import Statements
from cryptography.fernet import Fernet
from pyautogui import *
import pyautogui
import time
import keyboard
import numpy as np
import win32api, win32con
import ctypes
import os
import threading
import requests
import json
import math
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import datetime
from PIL import Image
import socket
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
import io

# Global Variables
resolution = None
aircraft = None

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
# Load environment variables from .env file
load_dotenv()

# Get the decryption key from the environment variables
decryption_key = os.getenv('decryption_key')
# Char/Str to Scancode for Bot Game Inputs
# https://kbdlayout.info/kbdusx/scancodes
with open('data/keycodes.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Evaluate the contents as Python code
KEYS = eval(contents)

# Create a Fernet cipher object with the key
cipher = Fernet(decryption_key)

# Cruising Heights for each Map
with open('data/heights_encrypted.txt', 'rb') as file:
    encrypted_contents = file.read()
    decrypted_contents = cipher.decrypt(encrypted_contents)

# Evaluate the contents as Python code
HEIGHTS = eval(decrypted_contents)

# Bombing Distances for each Map
with open('data/distances_encrypted.txt', 'rb') as file:
    encrypted_contents = file.read()
    decrypted_contents = cipher.decrypt(encrypted_contents)

# Evaluate the contents as Python code
DISTANCES = eval(decrypted_contents)

# Get User's KeyBinds from file
with open('data/keybinds.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Evaluate the contents as Python code
KEYBINDS = eval(contents)

# Get Map Data from file
with open('data/maps.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Evaluate the contents as Python code
MAPS = eval(contents)

###############################
#      Asset Decryption       #
###############################

# Decrypt the bin files
def decrypt_bin_file(bin_file):
    # Read the binary file
    with open(bin_file, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt the binary data
    global decryption_key
    cipher = Fernet(decryption_key)
    decrypted_data = cipher.decrypt(encrypted_data)

    return decrypted_data

# Convert bin data to png
def convert_to_png(data):
    # Create a PIL Image object from the decrypted data
    image = Image.open(io.BytesIO(data))

    # Convert the image to PNG format
    png_data = io.BytesIO()
    image.save(png_data, format='PNG')
    png_data.seek(0)

    return png_data.read()

# Convert all bin files to png
def process_bin_folder(bin_folder):
    temp_dir = r"assets\temp"

    try:
        # Iterate over the binary files in the folder
        for filename in os.listdir(bin_folder):
            if filename.endswith('.bin'):
                bin_file = os.path.join(bin_folder, filename)

                # Decrypt the binary file and convert it to PNG
                decrypted_data = decrypt_bin_file(bin_file)
                png_data = convert_to_png(decrypted_data)

                # Create a temporary PNG file with the same name as the bin file
                temp_filename = os.path.join(temp_dir, os.path.splitext(filename)[0] + '.png')

                # Write the PNG data to the temporary file
                with open(temp_filename, 'wb') as f:
                    f.write(png_data)
    finally:
        return

# Process the bin folder# Temp Change to after selection
process_bin_folder("assets/bin")

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
    return new_number

# Check if given image is on the screen
def is_image_on_screen(image_path, grayscale=True, confidence=0.7):
    try:
        position = pyautogui.locateOnScreen(image_path, grayscale=grayscale, confidence=confidence)
        if position is not None:
            return True
        else:
            return False
    except Exception as e:
        print(f"CONSOLE: Error in is_image_on_screen(): {e}")
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

# Query localhost for location data
def get_location_data():
    url = os.getenv('map_url')  
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError as e:
            print(f"CONSOLE: get_location_data() Error decoding JSON: {e}")
    return None

# Find the enemy base location
def get_map_info():
    json_data = get_location_data()
    if json_data:
        field = next((obj for obj in json_data if obj["type"] == "airfield" and obj["color"] == "#fa0C00"), None)
        if field:
            field_x = round((field["sx"] + field["ex"]) / 2, 2)
            field_y = round((field["sy"] + field["ey"]) / 2, 2)
            return field_x, field_y
        
def get_spawn_info():
    json_data = get_location_data()
    if json_data:
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        if player:
            return True
        else:
            return False
        
# Calculate which base the plane is facing
def calculate_ec_base():
    json_data = get_location_data()
    points = []
    if json_data:
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        if player:
            x, y, dx, dy = player["x"], player["y"], player["dx"], player["dy"]
        else:
            x = y = dx = dy = 0
        for obj in json_data:
            if obj["type"] == "bombing_point":
                point_x, point_y = obj["x"], obj["y"]
                points.append((point_x, point_y))
        index = 0
        min_index = 0
        min_angle = 180.0
        for point in points:
            angle = math.atan2(point[1] - y, point[0] - x)
            facing_angle = math.atan2(dy, dx)
            turn_angle = angle - facing_angle
            angle_degrees = math.degrees(turn_angle)

            if -180 <= angle_degrees <= 180 and abs(angle_degrees) < min_angle:
                min_angle = abs(angle_degrees)
                min_index = index

            index += 1

        return points[min_index]


# Returns the angle, distance, and location toward the enemy base
def get_base_info(map, base, ec=False):
    json_data = get_location_data()
    base_loc = base
    points = []
    if json_data:
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        if player:
            x, y, dx, dy = player["x"], player["y"], player["dx"], player["dy"]
        else:
            x = y = dx = dy = 0  # Set default values
        for obj in json_data:
            if obj["type"] == "bombing_point":
                points.append(obj["x"])
        points_sorted = sorted(set(points))
        if x is not None:
            if base_loc == [0, 0]:
                if map in ['GolanHeightsALT', 'SpainALT', 'SinaiALT', 'VietnamALT']:
                    index = 3
                elif map == "CityALT":
                    index = 2
                else:
                    index = 1
                if index < len(points_sorted):
                    chosen_point = points_sorted[index]
                    for obj in json_data:
                        if obj["type"] == "bombing_point" and obj["x"] == chosen_point:
                            point_x, point_y = obj["x"], obj["y"]
                            base_loc = (point_x, point_y)
            if base_loc != [0, 0]:
                angle = math.atan2(base_loc[1] - y, base_loc[0] - x)
                facing_angle = math.atan2(dy, dx)
                turn_angle = angle - facing_angle
                angle_degrees = math.degrees(turn_angle)
                distance = math.sqrt((x - base_loc[0])**2 + (y - base_loc[1])**2)
                return angle_degrees, distance, base_loc
            else:
                return 0.0, 2.0, [0, 0]
         
# Returns the angle, distance, and location toward the enemy airfield
def get_field_info():
    json_data = get_location_data()
    if json_data:
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        field = next((obj for obj in json_data if obj["type"] == "airfield" and obj["color"] == "#fa0C00"), None)
        if player and field:
            x, y, dx, dy = player["x"], player["y"], player["dx"], player["dy"]
            field_x = (field["sx"] + field["ex"]) / 2
            field_y = (field["sy"] + field["ey"]) / 2
            angle = math.atan2(field_y - y, field_x - x)
            facing_angle = math.atan2(dy, dx)
            turn_angle = angle - facing_angle
            angle_degrees = math.degrees(turn_angle)
            distance = math.sqrt((x - field_x)**2 + (y - field_y)**2)
            return angle_degrees, distance
            
# Returns the current Height and Rate of Climb
def get_attitude():
    url = os.getenv('att_url')
    response = requests.get(url)
    if response.status_code == 200:
        json_data = json.loads(response.text)
        try:
            return_data = (json_data["H, m"], json_data["Vy, m/s"])
        except:
            return_data = (1000, 0.0)
        return return_data

# Returns the speed in Mach
def get_mach():
    url = os.getenv('indi_url')
    response = requests.get(url)
    if response.status_code == 200:
        json_data = json.loads(response.text)
        return_data = json_data["mach"]
        return return_data

#########################
#   Control Functions   #
#########################

# Change the pitch of the plane based on height and RoC
def pitch_control(target_height, curr_height, attitude):
    height_diff = curr_height - target_height

    # Calculate the scaling factor based on the resolution
    global resolution
    scaling_factor = 1.0
    if resolution == 1440:
        scaling_factor = 1.333
    elif resolution == 2160:
        scaling_factor = 2.0

    if height_diff > 100 and attitude > 20.0:
        move_mouse_by(0, int(60 * scaling_factor))
    elif height_diff < 0 and attitude < -20.0:
        move_mouse_by(0, int(-60 * scaling_factor))
    elif height_diff > 100 and attitude > 10.0:
        move_mouse_by(0, int(30 * scaling_factor))
    elif height_diff < 0 and attitude < -10.0:
        move_mouse_by(0, int(-30 * scaling_factor))
    elif height_diff > 100 and attitude > 5.0:
        move_mouse_by(0, int(20 * scaling_factor))
    elif height_diff < 0 and attitude < -5.0:
        move_mouse_by(0, int(-20 * scaling_factor))
    elif height_diff > 25 and attitude > 0.0:
        move_mouse_by(0, int(7 * scaling_factor))
    elif height_diff < 0 and attitude < 0.5:
        move_mouse_by(0, int(-7 * scaling_factor))


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

#########################
#   General Functions   #
#########################

# End Program
def end_program():
    # Send the signal to terminate the program
    os.kill(os.getpid(), 9)

# Delete temp files when the program ends
def delete_temp_files():
    folder_path = r'assets\temp'
    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Check if the current path is a file (not a subdirectory)
        if os.path.isfile(file_path):
            # Delete the file
            os.remove(file_path)

# Bot Loop
def bot():
    global aircraft
    while True:
        # Click 'To Battle' Button in Main Menu
        while pyautogui.locateOnScreen('assets/temp/in_queue.png', grayscale=False, confidence=0.75) == None:
            # Check for battle trophy, to hangar button, and if the plane is repaired
            if pyautogui.locateOnScreen(f'assets/temp/{aircraft}_repaired.png', grayscale=False, confidence=0.97) != None or pyautogui.locateOnScreen('assets/temp/trophy.png', grayscale=False, confidence=0.95) != None or pyautogui.locateOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.85) != None or pyautogui.locateOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.85) != None or pyautogui.locateOnScreen(f'assets/temp/invitation.png', grayscale=False, confidence=0.97) != None:
                press(KEYBINDS['enter'])
            time.sleep(0.5)

        print("\n\nCONSOLE: To Battle!")

        # Wait to Join Battle
        print('CONSOLE: Waiting in Qeue...')
        wait_for('assets/temp/spawn.png', grayscale=False, confidence=0.7)
        print('CONSOLE: In Spawn Screen')
        
        # Check which map match is taking place on
        move_mouse_to(100, 100)
        # Temp Variable
        city = False
        ec = False
        map = ''
        inc = 0
        exception_flag = False
        while map == '' and inc <= 5:
            map_coords=get_map_info()
            try:
                map = MAPS[map_coords]
                if map == 'City' or map == 'CityALT':
                    city = True
                elif map == 'VietnamEC' or map == 'SpainEC' or map == 'Afghanistan' or map == 'RockyCanyon' or map == 'RockyCanyonALT':
                    ec = True
                break
            except:
                print(f"CONSOLE: Map not found; map_coords are {map_coords}")
                exception_flag = True
            if pyautogui.locateOnScreen('assets/temp/rocky_canyonALT.png', grayscale=False, confidence=0.97) != None:
                map = 'RockyCanyonALT'
                ec = True
            inc += 1
            time.sleep(0.5)
        if map == '':
            ec = True
            map = 'RockyCanyonALT'

        # Temp condition
        if exception_flag:
            screenshot_num = screenshot_screen()
            with open("data/checker.txt", "a") as file:
                file.write(f"\nInfo:{map_coords} : 'Screenshot #{screenshot_num}'")
        print(f'CONSOLE: Map is {map}') 
        
        # In Battle, click the Spawn In button
        press(KEYBINDS['enter'])
        print("CONSOLE: Spawn Button Clicked")
        time.sleep(1)
            

        # Pitch values
        pitch_value = 245
        downVal = int(pitch_value/8)

        # Take off/spawn procedure
        battle_time = time.time()
        if not city:
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn on Airfield')
            wait_on('assets/temp/cancel_spawn.png')
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
            while pyautogui.locateOnScreen('assets/temp/centreline.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/j_out.png', grayscale=False, confidence=0.95) == None and height < HEIGHTS[map]/2:
                height = get_attitude()[0]
                time.sleep(0.1)
            # Pitch down a few times
            for i in range(3):
                    move_mouse_by(0, downVal + 5)
                    time.sleep(1)
        # Air Spawn
        elif city:
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn In Airspawn')
            wait_on('assets/temp/cancel_spawn.png')
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
        base_loc = [0, 0]
        zoom_flag = False
        brake_flag = False
        if city:
            pitch_flag = True
        else:
            pitch_flag = False
        mach_flag = False
        map_distance = DISTANCES[map]
        height = HEIGHTS[map]
        
        # Hold down the bombing button
        hold(KEYBINDS['bomb'])

        # Bombing loop
        while pyautogui.locateOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/j_out.png', grayscale=False, confidence=0.95) == None:

            base_info = get_base_info(map, base_loc)
            centreline_location = pyautogui.locateOnScreen('assets/temp/centreline.png', grayscale=False, confidence=0.7)
            if centreline_location:
                center_x, center_y = pyautogui.center(centreline_location)
                
                screen_width, screen_height = pyautogui.size()
                screen_center_x = screen_width // 2
                
                distance_x = int((center_x - screen_center_x) / 2)
                move_mouse_by(distance_x, 0)
            elif brake_flag and base_info[1] > last_dist:
                release(KEYBINDS['bomb'])
                break
            elif base_info and pitch_flag and not brake_flag:
                move_mouse_by(int(base_info[0] * 10), 0)
            last_dist = base_info[1]

            if zoom_time >= 6 and not zoom_flag:
                press(KEYBINDS['zoom'])
                zoom_flag = True
            elif zoom_time == 10 and ec:
                base_loc = calculate_ec_base()
            zoom_time += 1

            if brake_flag:
                print('CONSOLE: Popping Flares')
                pyautogui.scroll(-2)
                pyautogui.scroll(2)

            if brake_flag and not mach_flag:
                mach = get_mach()
                if mach < 1.0:
                    print('CONSOLE: Retracting Airbrake')
                    press(KEYBINDS['airbrake'])
                    mach_flag = True

            attitude = get_attitude()
            if not city and not pitch_flag and attitude[0] > height - 10:
                move_mouse_by(0, downVal + 5)
                move_mouse_by(0, downVal + 5)
                time.sleep(1)
                pitch_flag = True

            if base_info and zoom_time != 11:
                base_loc = base_info[2]
                if not brake_flag and base_info[1] <= map_distance:
                    print('CONSOLE: Deploying Airbrake')
                    press(KEYBINDS['airbrake'])
                    pyautogui.scroll(-2)
                    if aircraft in ["F-4F", "MiG-23BN"]:
                        press(KEYBINDS['airbrake'])
                        print('CONSOLE: Retracting Airbrake')
                        mach_flag = True
                    brake_flag = True

            if pitch_flag and not brake_flag:
                pitch_control(height, attitude[0], attitude[1])
            
            
        # After Bombing pitch up, throttle down, and bait enemies
        time.sleep(1)
        cruising_height = height + 1500
        if not mach_flag:
            press(KEYBINDS['airbrake'])
        brake_flag = False
        press(KEYBINDS['smoke'])
        time.sleep(1)
        # Turn right until dead
        while pyautogui.locateOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/j_out.png', grayscale=False, confidence=0.95) == None:
            attitude = get_attitude()
            field_data = get_field_info()
            if not brake_flag:
                pitch_control(cruising_height, attitude[0], attitude[1])
            if field_data is not None:
                move_mouse_by(int(field_data[0] * 10), 0)
                if field_data[1] <= 0.065 and not brake_flag:
                    press(KEYBINDS['airbrake'])
                    if cruising_height >= 2000:
                        move_mouse_by(0, int(cruising_height/12))
                    brake_flag = True
            # J out if 10 minutes have passed
            elapsed_time = get_elapsed_time(battle_time)
            if elapsed_time >= 600:
                holdFor('j', 4)

        # Vehicle has been destroyed
        if pyautogui.locateOnScreen('assets/temp/j_out.png', grayscale=False, confidence=0.95) != None:
            holdFor('j', 4)
            print('CONSOLE: Aircraft Downed, Returning to Hangar')

            # Click 'Return To Hangar' Button
            wait_for('assets/temp/return_to_hangar.png', False, 0.75)
            while pyautogui.locateCenterOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/temp/return_to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)
            
            while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) == None:
                if pyautogui.locateOnScreen('assets/temp/trophy.png', grayscale=False, confidence=0.95) != None:
                    press(KEYBINDS['enter'])
            # Click 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/temp/to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)
                
            
        elif pyautogui.locateCenterOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.75) != None:
            print('CONSOLE: Aircraft Downed, Returning to Hangar')
            while pyautogui.locateCenterOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/temp/return_to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)

            # Wait for 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) == None:
                if pyautogui.locateOnScreen('assets/temp/trophy.png', grayscale=False, confidence=0.95) != None:
                    press(KEYBINDS['enter'])
            # Click 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/temp/to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)

        # Match has ended
        else:
            print('CONSOLE: Match Ended, Returning to Hangar')
            # Wait for 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) == None:
                if pyautogui.locateOnScreen('assets/temp/trophy.png', grayscale=False, confidence=0.95) != None:
                    press(KEYBINDS['enter'])
            # Click 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) != None:
                move_mouse_to_image('assets/temp/to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)

# Main function
def main():
    # Create the main window
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    checkbox_var = tk.BooleanVar()
    key_var = tk.StringVar()

    # Function to handle the window close event
    def on_window_close():
        delete_temp_files()
        end_program()

    # Function to update the variable when the text changes
    def update_key_var(event):
        key_var.set(key_entry.get())
    
    def key_exists(key):
        key_var.set(key)


    def check_key(key):
        # Get the user's IP address
        ip_address = get_ip_address()

        if ip_address:
            url = os.getenv('server_ip')

            # JSON payload for the request
            payload = {
                'users_key': key,
                'users_ip': ip_address
            }

            response = requests.post(url, json=payload)

            if response.text == "True":
                return True
            return False

        else:
            print("CONSOLE: Unable to retrieve the IP address")
            return False

    def get_ip_address():
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.connect(("8.8.8.8", 80))
            ip_address = sock.getsockname()[0]
            return ip_address
        except socket.error:
            return None
        finally:
            sock.close()

    # Function to start the bot
    def start_bot():
        key = key_var.get()
        global resolution
        global aircraft
        if checkbox_var.get() and check_key(key) and resolution is not None and aircraft is not None:
            # Prompt the user to Alt + Tab to War Thunder
            messagebox.showinfo("Alert", "Please Alt + Tab to War Thunder")
            root.destroy()
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
                    print(f'CONSOLE: Bot was running for: {formatted_time}')

                    delete_temp_files()
                    end_program()
        elif resolution is None:
            messagebox.showinfo("Error", "Please Choose a Resolution")
        elif aircraft is None:
            messagebox.showinfo("Error", "Please Choose an Aircraft")
        elif not checkbox_var.get():
            # Checkbox is not checked, show an error message
            messagebox.showinfo("Error", "Please agree to use responsibly.")
        else:
            messagebox.showinfo("Error", "Incorrect Key")

    root.protocol("WM_DELETE_WINDOW", on_window_close)
    root.geometry("800x700")
    root.title("War Thunder Air Bot 1.0")

    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    logo = ctk.CTkImage(Image.open("assets/icons/icon.png"), size=[164, 139])
    logo_label = ctk.CTkLabel(frame, text="", image=logo)
    logo_label.pack(pady=12, padx=10)

    label = ctk.CTkLabel(master=frame, text="Nicks War Thunder Air Bot 1.0", font=("Roboto", 24))
    label.pack(pady=12, padx=10)

    # Create the setup instructions label
    instructions_label = ctk.CTkLabel(master=frame,
                                      text="Setup Instructions:\n1. Check the KeyBinds file and ensure that your keybinds are set up correctly\n2. Go to Hangar and have the appropriate aircraft selected\n3. Select 'Air Realistic Battles'\n4. Ensure you are using Red and Blue default colors\n\nTo end the program, press and hold 'q' at any time",
                                      font=("Roboto", 15))
    instructions_label.pack(pady=12, padx=10)

    key_entry = ctk.CTkEntry(master=frame, placeholder_text="Activation Key", show="*")
    key_entry.pack(pady=12, padx=10)

    # Get key from .env
    activation_key = os.getenv("activation_key")

    if activation_key:
        key_entry.insert(0, activation_key)
        key_exists(activation_key)

    # Bind the function to the text change event of the entry widget
    key_entry.bind("<KeyRelease>", update_key_var)

    # Resolution drop down
    resolution_var = ctk.StringVar(value="Select Resolution")  # set initial value

    def choose_resolution(choice):
        print("Resolution currently chosen is: ", choice)
        resolutions = {
            '1920x1080': 1080,
            '2560x1440': 1440,
            '3840x2160': 2160
        }
        global resolution
        resolution = resolutions[choice]


    resolution_box = ctk.CTkComboBox(master=frame,
                                        values=["1920x1080", "2560x1440", "3840x2160"],
                                        command=choose_resolution,
                                        variable=resolution_var)
    resolution_box.pack(padx=20, pady=10)

    # Aircraft drop down
    aircraft_var = ctk.StringVar(value="Select Aircraft")  # set initial value

    def choose_aircraft(choice):
        print("Aircraft Chosen: ", choice)
        aircrafts = {
            'Kfir Canard (IS)': 'Kfir',
            'F-4F (GR)': 'F-4F',
            'MiG-23BN (GR)': 'MiG-23BN'
        }
        global aircraft
        aircraft = aircrafts[choice]

    aircraft_box = ctk.CTkComboBox(master=frame,
                                        values=["Kfir Canard (IS)", "F-4F (GR)", "MiG-23BN (GR)"],
                                        command=choose_aircraft,
                                        variable=aircraft_var)
    aircraft_box.pack(padx=20, pady=10)

    start_button = ctk.CTkButton(master=frame, text="Start Bot", command=start_bot)
    start_button.pack(pady=12, padx=10)

    checkbox = ctk.CTkCheckBox(master=frame, text="I agree to use responsibly", variable=checkbox_var)
    checkbox.pack(pady=12, padx=10)

    root.iconbitmap("assets/icons/favicon.ico")
    # Start the GUI main loop
    root.mainloop()


# Start the main thread
if __name__ == "__main__":
    main()
     
            