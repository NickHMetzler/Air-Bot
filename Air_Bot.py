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
import mysql.connector
from dotenv import load_dotenv
import os

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


from cryptography.fernet import Fernet
from PIL import Image
import io

def decrypt_bin_file(bin_file):
    # Read the binary file
    with open(bin_file, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt the binary data
    global decryption_key
    cipher = Fernet(decryption_key)
    decrypted_data = cipher.decrypt(encrypted_data)

    return decrypted_data

def convert_to_png(data):
    # Create a PIL Image object from the decrypted data
    image = Image.open(io.BytesIO(data))

    # Convert the image to PNG format
    png_data = io.BytesIO()
    image.save(png_data, format='PNG')
    png_data.seek(0)

    return png_data.read()

def process_bin_folder(bin_folder):
    temp_dir = r"assets\temp"

    try:
        # Iterate over the binary files in the folder
        for filename in os.listdir(bin_folder):
            if filename.endswith('.bin'):
                bin_file = os.path.join(bin_folder, filename)

                # Decrypt the binary file and convert it to PNG
                # Replace this code with your actual decryption and conversion logic
                decrypted_data = decrypt_bin_file(bin_file)
                png_data = convert_to_png(decrypted_data)

                # Create a temporary PNG file with the same name as the bin file
                temp_filename = os.path.join(temp_dir, os.path.splitext(filename)[0] + '.png')

                # Write the PNG data to the temporary file
                with open(temp_filename, 'wb') as f:
                    f.write(png_data)
    finally:
        return
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

def get_location_data():
    url = os.getenv('map_url')  
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return None

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


# Returns the angle toward the enemy airfield
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
        return_data = (json_data["H, m"], json_data["Vy, m/s"])
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

def pitch_control(target_height, curr_height, attitude):
    height_diff = curr_height - target_height
    if height_diff > 100 and attitude > 20.0:
        move_mouse_by(0, 60)
    elif height_diff < 0 and attitude < -20.0:
        move_mouse_by(0, -60)
    elif height_diff > 100 and attitude > 10.0:
        move_mouse_by(0, 30)
    elif height_diff < 0 and attitude < -10.0:
        move_mouse_by(0, -30)
    elif height_diff > 100 and attitude > 5.0:
        move_mouse_by(0, 20)
    elif height_diff < 0 and attitude < -5.0:
        move_mouse_by(0, -20)
    elif height_diff > 25 and attitude > 0.0:
        move_mouse_by(0, 7)
    elif height_diff < 0 and 0.1 < attitude < target_height:
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
    while True:
        # Click 'To Battle' Button in Main Menu
        while pyautogui.locateOnScreen('assets/temp/in_queue.png', grayscale=False, confidence=0.75) == None:
            # Do not click if the vehicle needs to be repaired
            if pyautogui.locateOnScreen('assets/temp/trophy.png', grayscale=False, confidence=0.95) != None:
                press(KEYBINDS['enter'])
            if pyautogui.locateOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.85) != None:
                press(KEYBINDS['enter'])
            
            press(KEYBINDS['enter'])
            time.sleep(0.5)
        print("\n\nCONSOLE: To Battle!")

        # Wait to Join Battle
        print('CONSOLE: Waiting in Qeue...')
        wait_for('assets/temp/spawn.png', grayscale=False, confidence=0.8)
        
        # Check which map match is taking place on
        move_mouse_to(100, 100)
        # Temp Variable
        screenshot_val = False
        city = False
        ec = False
        if pyautogui.locateOnScreen('assets/temp/vietnam.png', grayscale=False, confidence=0.97) != None:
            map = 'Vietnam'
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/temp/vietnamALT.png', grayscale=False, confidence=0.96) != None:
            map = 'VietnamALT'
        elif pyautogui.locateOnScreen('assets/temp/vietnamEC.png', grayscale=False, confidence=0.97) != None:
            map = 'VietnamEC'
            ec = True
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/temp/spain.png', grayscale=False, confidence=0.99) != None:
            map = 'Spain'
        elif pyautogui.locateOnScreen('assets/temp/spainALT.png', grayscale=False, confidence=0.99) != None:
            map = 'SpainALT'
        elif pyautogui.locateOnScreen('assets/temp/spainEC.png', grayscale=False, confidence=0.96) != None:
            map = 'SpainEC'
            ec = True
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/temp/golan_heights.png', grayscale=False, confidence=0.99) != None:
            map = 'GolanHeights'
        elif pyautogui.locateOnScreen('assets/temp/golan_heightsALT.png', grayscale=False, confidence=0.99) != None:
            map = 'GolanHeightsALT'
        elif pyautogui.locateOnScreen('assets/temp/sinai.png', grayscale=False, confidence=0.98) != None:
            map = 'Sinai'
        elif pyautogui.locateOnScreen('assets/temp/sinaiALT.png', grayscale=False, confidence=0.98) != None:
            map = 'SinaiALT'
        elif pyautogui.locateOnScreen('assets/temp/city.png', grayscale=False, confidence=0.97) != None:
            map = 'City'
            city = True
        elif pyautogui.locateOnScreen('assets/temp/cityALT.png', grayscale=False, confidence=0.97) != None:
            map = 'CityALT'
            city = True
        elif pyautogui.locateOnScreen('assets/temp/rocky_canyonALT.png', grayscale=False, confidence=0.97) != None:
            map = 'RockyCanyonALT'
            ec = True
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/temp/afghanistan.png', grayscale=False, confidence=0.97) != None:
            ec = True
            map = 'RockyCanyonALT'
        else:
            ec = True
            map = 'RockyCanyonALT'
            screenshot_val = True
        # Temp condition
        if screenshot_val: 
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
        if not city:
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn on Airfield')
            screenshot_screen()
            wait_on('assets/temp/cancel_spawn.png', True, 0.65)
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
            wait_on('assets/temp/cancel_spawn.png', 0.7)
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
                

            if brake_flag and not mach_flag:
                mach = get_mach()
                if mach < 1.0:
                    print('CONSOLE: Retracting Airbrake')
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
                    pyautogui.scroll(-2)
                    press(KEYBINDS['airbrake'])
                    time.sleep(1)
                    press(KEYBINDS['airbrake'])
                    brake_flag = True

            if pitch_flag and not brake_flag:
                pitch_control(height, attitude[0], attitude[1])
            
        # After Bombing pitch up, throttle down, and bait enemies
        time.sleep(1)
        cruising_height = height + 1000
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


    def check_key(key):
        # Get the user's IP address
        ip_address = get_ip_address()

        if ip_address:
            # Connect to the MySQL database
            try:
                connection = mysql.connector.connect(
                    host=os.getenv("DB_HOST"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    database=os.getenv("DB_DATABASE"),
                    auth_plugin=os.getenv("DB_AUTH_PLUGIN")
                )

                # Create a cursor object to interact with the database
                cursor = connection.cursor()

                # Prepare the SQL query to check for a matching entry
                query = "SELECT * FROM users WHERE users_key = %s"
                values = (key,)

                cursor.execute(query, values)

                result = cursor.fetchone()

                # Check if a matching entry was found
                if result:
                    # Get the user's IP address
                    user_ip = result[1]  # Assuming `users_ip` is the second column in the table (index 1)

                    # Compare the IP address with the provided one
                    if user_ip == ip_address:
                        cursor.close()
                        connection.close()
                        return True
                    else:
                        # Update the IP address in the database
                        update_query = "UPDATE users SET users_ip = %s WHERE users_key = %s"
                        update_values = (ip_address, key)
                        cursor.execute(update_query, update_values)
                        connection.commit()
                        cursor.close()
                        connection.close()
                        return True
                else:
                    cursor.close()
                    connection.close()
                    return False



            except mysql.connector.Error as error:
                print("Error connecting to MySQL:", error)

        else:
            print("Unable to retrieve the IP address.")
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
        if checkbox_var.get() and check_key(key):
            # Prompt the user to Alt + Tab to War Thunder
            messagebox.showinfo("Alert", "Please Alt + Tab to War Thunder")

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
                    print(f'Bot was running for: {formatted_time}')

                    delete_temp_files()
                    end_program()
        elif not checkbox_var.get():
            # Checkbox is not checked, show an error message
            messagebox.showinfo("Error", "Please agree to use responsibly.")
        else:
            messagebox.showinfo("Error", "Incorrect Key")

    root.protocol("WM_DELETE_WINDOW", on_window_close)
    root.geometry("800x600")
    root.title("War Thunder Air Bot 0.9")

    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    logo = ctk.CTkImage(Image.open("assets/icons/icon.png"), size=[164, 139])
    logo_label = ctk.CTkLabel(frame, text="", image=logo)
    logo_label.pack(pady=12, padx=10)

    label = ctk.CTkLabel(master=frame, text="Nicks War Thunder Air Bot 0.9", font=("Roboto", 24))
    label.pack(pady=12, padx=10)

    # Create the setup instructions label
    instructions_label = ctk.CTkLabel(master=frame,
                                      text="Setup Instructions:\n1. Check the KeyBinds file and ensure that your keybinds are set up correctly\n2. Go to Hangar and have the Kfir Canard (Israel) selected\n3. Select 'Air Realistic Battles'\n\nTo end the program, press and hold 'q' at any time",
                                      font=("Roboto", 15))
    instructions_label.pack(pady=12, padx=10)

    key_entry = ctk.CTkEntry(master=frame, placeholder_text="Activation Key", show="*")
    key_entry.pack(pady=12, padx=10)
    # Bind the function to the text change event of the entry widget
    key_entry.bind("<KeyRelease>", update_key_var)

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
     
            