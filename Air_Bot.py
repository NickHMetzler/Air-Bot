# Naval_Bot.py
# Plays War Thunder Naval to automatically generate Silver Lions (In Game Currency)
# 2023-06-18
# Nicolas Metzler

# Import Statements
from cryptography.fernet import Fernet
import random
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
decryption_key = b'eXqe4xrjdstZTKe3nNNGP8ie8WMqhBZehXev8M1_OEQ='
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
    # Check if the directory exists
    if not os.path.exists(temp_dir):
        # Create the directory
        os.makedirs(temp_dir)
        print("CONSOLE: Creating Temp Folder...")
    else:
        print("CONSOLE: Temp Folder Found")
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

def game_over():
    if pyautogui.locateOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/temp/j_out.png', grayscale=False, confidence=0.95) == None and pyautogui.locateOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.95) == None:
        return False
    else:
        return True
    
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
    url = 'http://localhost:8111/map_obj.json'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except json.decoder.JSONDecodeError as e:
            print(f"CONSOLE: get_location_data() Error decoding JSON: {e}")
    return None

# Returns the current Height and Rate of Climb
def get_attitude():
    url = 'http://localhost:8111/state'
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
    url = 'http://localhost:8111/indicators'
    response = requests.get(url)
    if response.status_code == 200:
        json_data = json.loads(response.text)
        return_data = json_data["mach"]
        return return_data
    
def get_target_info(target):
    json_data = get_location_data()
    if json_data:
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        if player:
            target_x = target[0]
            target_y = target[1]
            x, y, dx, dy = player["x"], player["y"], player["dx"], player["dy"]
            angle = math.atan2(target_y - y, target_x - x)
            facing_angle = math.atan2(dy, dx)
            turn_angle = angle - facing_angle
            angle_degrees = math.degrees(turn_angle)
            distance = math.sqrt((x - target_x)**2 + (y - target_y)**2)
            return angle_degrees, distance
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
        
# Add bases if they are not in bases_arr
# If the base is in bases_arr but not in the new bases, set to False



def initialize_bases():
    global bases_arr
    json_data = get_location_data()
    if json_data:
        for obj in json_data:
            if obj["type"] == "bombing_point":
                bases_arr.append([(obj["x"], obj["y"]), True])
        print(f"Bases Array is: {bases_arr}")
        

def count_bases():
    global bases_arr
    new_bases = []
    json_data = get_location_data()
    if json_data:
        for obj in json_data:
            if obj["type"] == "bombing_point":
                new_bases.append((obj["x"], obj["y"]))
        for base in bases_arr:
            if base[0] not in new_bases and base[1] == True:
                print(f"Base at {base[0]} has been bombed")
                # Base has been bombed
                base[1] = False
        append_list = []
        for new_base in new_bases:
            if bases_arr == []:
                # New base added
                append_list.append(new_base)
            else:
                exists = False
                for base in bases_arr:
                    if new_base in base and base[1] == True:
                        exists = True
                        break
                if exists == False:
                    # New base added
                    append_list.append(new_base)
                        
        for location in append_list:
            bases_arr.append([location, True])
        print(f"Bases Array is: {bases_arr}")
        i = 0
        bases = 0
        for base in bases_arr:
            if base[1] == True and i >= 4:
                bases += 1
            i += 1
        if bases >= 2 or bases <= 0:
            print(f"CONSOLE: There are {bases} new bases present")
        else:
            print(f"CONSOLE: There is {bases} new base present")
        return bases
    return 0
        
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
        try:
            return points[min_index]
        except:
            return None


def get_holding_location(location, city=False):
    json_data = get_location_data()
    points = []
    if json_data:
        for obj in json_data:
            if obj["type"] == "bombing_point":
                points.append(obj["x"])

        points_sorted = sorted(set(points))
    if location == 'left':
        chosen_point = points_sorted[0]
        add_x = -0.15
        if city:
            add_x = -0.25
    elif location == 'right':
        chosen_point = points_sorted[len(points_sorted) - 1]
        add_x = 0.15
        if city:
            add_x = 0.25
    
    for obj in json_data:
        if obj["type"] == "bombing_point" and obj["x"] == chosen_point:
            return obj["x"] + add_x, obj["y"]
                



# Returns the angle, distance, and location toward the enemy base
def get_base_info(base):
    json_data = get_location_data()
    base_loc = base
    new_base = None
    if json_data:
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        if player:
            x, y, dx, dy = player["x"], player["y"], player["dx"], player["dy"]
        else:
            x = y = dx = dy = 0  # Set default values
        for obj in json_data:
            if obj["type"] == "bombing_point" and obj["x"] == base_loc[0]:
                point_x, point_y = obj["x"], obj["y"]
                new_base = (point_x, point_y)
        if new_base == None:
            return False
        else:
            angle = math.atan2(base_loc[1] - y, base_loc[0] - x)
            facing_angle = math.atan2(dy, dx)
            turn_angle = angle - facing_angle
            angle_degrees = math.degrees(turn_angle)
            distance = math.sqrt((x - base_loc[0])**2 + (y - base_loc[1])**2)
            return angle_degrees, distance, new_base
         
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
            

#########################
#   Control Functions   #
#########################

# Change the pitch of the plane based on height and RoC
def pitch_control(target_height, curr_height, attitude):
    height_diff = curr_height - target_height

    # Calculate the scaling factor based on the resolution
    global resolution
    scaling_factor = 1.0
    if resolution == "1440":
        scaling_factor = 1.333
    elif resolution == "2160":
        scaling_factor = 2.0

    
    if height_diff > 0:
        if attitude > 20.0:
            move_mouse_by(0, int(90 * scaling_factor))
        elif attitude > 10.0:
            move_mouse_by(0, int(60 * scaling_factor))
        elif attitude > 5.0:
            move_mouse_by(0, int(30 * scaling_factor))
    elif height_diff > 200:
        if attitude > -5.0:
            move_mouse_by(0, int(60 * scaling_factor))
        elif attitude > -10.0:
            move_mouse_by(0, int(30 * scaling_factor))
        elif attitude > -20.0:
            move_mouse_by(0, int(10 * scaling_factor))
    elif height_diff < 0:
        if attitude < -35.0:
            move_mouse_by(0, int(-640 * scaling_factor))
        elif attitude < -30.0:
            move_mouse_by(0, int(-360 * scaling_factor))
        elif attitude < -25.0:
            move_mouse_by(0, int(-180 * scaling_factor))
        elif attitude < -20.0:
            move_mouse_by(0, int(-90 * scaling_factor))
        elif attitude < -10.0:
            move_mouse_by(0, int(-60 * scaling_factor))
        elif attitude < -5.0:
            move_mouse_by(0, int(-30 * scaling_factor))
        elif attitude < 0.5:
            move_mouse_by(0, int(-10 * scaling_factor))



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

def holding_pattern(height):
    move_mouse_by(-700, 0)
    time.sleep(2)
    attitude = get_attitude()
    pitch_control(height, attitude[0], attitude[1])
    press(KEYBINDS['ccrp_off'])
    press(KEYBINDS['ccrp'])
    base_count = count_bases()
    time.sleep(1)
    if pyautogui.locateOnScreen('assets/temp/centreline.png', grayscale=False, confidence=0.6) == None and base_count >= 2:
        return True
    else:
        return False

    

# Research another modification
def researched_mod():
    if pyautogui.locateOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.7) != None:
        print('CONSOLE: researched_mod(): Found OK')
        while pyautogui.locateOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.7) != None:
            move_mouse_to_image('assets/temp/ok.png')
            click_mouse()
            print("CONSOLE: researched_mod(): Trying to click OK")
            time.sleep(0.5)
    else:
        print('CONSOLE: researched_mod(): Did not find OK')
    
    time.sleep(4)

    # If these are false, it is a new Aircraft
    if pyautogui.locateOnScreen('assets/temp/finish.png', grayscale=False, confidence=0.85) != None:
        print('CONSOLE: researched_mod(): Found Finish')
        while pyautogui.locateOnScreen('assets/temp/finish.png', grayscale=False, confidence=0.7) != None:
            move_mouse_to_image('assets/temp/finish.png')
            click_mouse()
            print("CONSOLE: researched_mod(): Trying to click Finish")
            time.sleep(0.5)
    elif pyautogui.locateOnScreen('assets/temp/spend.png', grayscale=False, confidence=0.85) != None:
        print('CONSOLE: researched_mod(): Found Spend')
        while pyautogui.locateOnScreen('assets/temp/spend.png', grayscale=False, confidence=0.7) != None:
            move_mouse_to_image('assets/temp/finish.png')
            click_mouse()
            print("CONSOLE: researched_mod(): Trying to click Spend")
            time.sleep(0.5)
    else:
        print('CONSOLE: researched_mod(): Did not find Finish or Spend\nCONSOLE: researched_mod(): Returning False for Modification')
        return False

    time.sleep(4)

    # All modifications in a row are researched
    if pyautogui.locateOnScreen('assets/temp/all_mods.png', grayscale=False, confidence=0.7) != None:
        print('CONSOLE: researched_mod(): Found all_mods')
        while pyautogui.locateOnScreen('assets/temp/all_mods.png', grayscale=False, confidence=0.7) != None:
            move_mouse_to_image('assets/temp/all_mods.png')
            click_mouse()
            print("CONSOLE: researched_mod(): Trying to click all_mods")
            time.sleep(0.5)
    else:
        print('CONSOLE: researched_mod(): Did not find all_mods')

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

# Define a dictionary to map conditions to heights
heights_map = {
    ('rush', 'GolanHeightsALT', 650): (lambda base_info: base_info[1] <= 0.26),
    ('rush', 'GolanHeights', 550): (lambda base_info: base_info[1] <= 0.26),
    ('rush', 'Sinai', 500): (lambda base_info: base_info[2][0] >= 0.35),
    ('rush', 'Vietnam', 1200): (lambda base_info: base_info[2][0] >= 0.513),
    ('rush', 'City', 300): (lambda base_info: base_info[1] <= 0.11),
    ('rush', 'Spain', 550): (lambda base_info: base_info[1] <= 0.16),
    ('rush', 'SinaiALT', 300): (lambda base_info: base_info[2][0] <= 0.39 and base_info[1] <= 0.24),
    ('rush', 'SinaiALT', 300): (lambda base_info: base_info[2][0] >= 0.4 and base_info[1] <= 0.14)
}

# Function to check and set the height value
def set_height(mode, map_name, base_info, height):
    for key, condition in heights_map.items():
        if key[0] == mode and key[1] == map_name:
            if condition(base_info):
                if height != key[2]:
                    print(f"CONSOLE: Changing {map_name} Height from {height} to {key[2]}")
                    height = key[2]
            elif height != HEIGHTS[map_name]:
                height = HEIGHTS[map_name]
                print(f"CONSOLE: Changing {map_name} Height to OG")
            break
    return height


# Bot Loop
def bot():
    # Import Globals
    global aircraft
    global resolution
    global mode
    global bases_arr
    # Process the bin folder
    process_bin_folder(f"assets/bin/{resolution}")
    # Bot loop
    while True:
        bases_arr = []
        start_loop = time.time()
        while True:
            in_queue = pyautogui.locateOnScreen('assets/temp/in_queue.png', grayscale=False, confidence=0.95)
            if in_queue is not None:
                break
            else:
                print("CONSOLE: Looking for in_queue")

            invite = pyautogui.locateOnScreen(f'assets/temp/invite.png', grayscale=False, confidence=0.97)
            repaired = pyautogui.locateOnScreen(f'assets/temp/{aircraft}_repaired.png', grayscale=False, confidence=0.97)
            trophy = pyautogui.locateOnScreen('assets/temp/trophy.png', grayscale=False, confidence=0.95)
            to_hangar = pyautogui.locateOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.85)

            waiting_for = get_elapsed_time(start_loop)
            if waiting_for > 600 or invite is not None:
                press('esc')

            # if trophy is not None or to_hangar is not None or repaired is not None:
            if trophy is not None or to_hangar is not None or repaired is not None or mode == 'slow':
                press(KEYBINDS['enter'])

            time.sleep(0.5)


        print("\n\nCONSOLE: To Battle!")

        # Wait to Join Battle
        print('CONSOLE: Waiting in Qeue...')
        wait_for('assets/temp/spawn.png', grayscale=False, confidence=0.7)
        print('CONSOLE: In Spawn Screen')
        
        # Initialize variables
        move_mouse_to(100, 100)
        city = False
        map = ''
        inc = 0
        exception_flag = False

        # Check which map match is taking place on
        while inc <= 5:
            map_coords=get_map_info()
            try:
                map = MAPS[map_coords]
                if map == 'City' or map == 'CityALT':
                    city = True
                break
            except:
                print(f"CONSOLE: Map not found; map_coords are {map_coords}")
                exception_flag = True
                # Temp variable
                map = 'RockyCanyonALT'
            inc += 1
            time.sleep(0.5)
        
        # Temp variable
        # Record screenshot and coordinates for unknown map
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
        scaling_factor = 1.0
        if resolution == "1440":
            scaling_factor = 1.333
        elif resolution == "2160":
            scaling_factor = 2.0
        pitch_value = int(200 * scaling_factor)
        downVal = int(pitch_value/8)

        # Take off/spawn procedure
        battle_time = time.time()
        if not city and aircraft != 'F-84F':
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn on Airfield')
            wait_on('assets/temp/cancel_spawn.png', True, 0.85)
            print('CONSOLE: Spawned in')

            # Throttle up, then pitch up
            holdFor(KEYBINDS['throttleUp'], 4)
            move_mouse_by(0, -pitch_value)
            press(KEYBINDS['radar'])

            # Retract gear when taken off
            ground = get_attitude()[0]
            height = ground
            while height <= ground + 10:
                height = get_attitude()[0]
            print('CONSOLE: Retracting Landing Gear')
            press(KEYBINDS['gear'])
            
            if mode == 'rush':
            # Choose base target
                print('CONSOLE: Activating CCRP')
                press(KEYBINDS['ccrp'])
                while pyautogui.locateOnScreen('assets/temp/centreline.png', grayscale=False, confidence=0.7) == None and not game_over() and height < HEIGHTS[map]/3:
                    height = get_attitude()[0]
                    time.sleep(0.1)
                # Pitch down a few times
                for i in range(3):
                        move_mouse_by(0, downVal + 5)
                        time.sleep(1)
            elif mode == 'slow':
                # Find the side bombing point and set holding location
                if get_map_info()[1] < 0.5:
                    target_location = get_holding_location('left')
                else:
                    target_location = get_holding_location('right')

                att = get_attitude()
                curr_height = att[0]
                height = ground + 5000
                # Climb to 5000m above ground and aim left
                print("CONSOLE: Climbing...")
                initialize_bases()
                while not game_over() and curr_height < height/2:
                    curr_height = get_attitude()[0]
                    time.sleep(0.1)
                    target_info = get_target_info(target_location)
                    if target_info:
                        angle = target_info[0]
                        move_mouse_by(int(angle * 10), 0)
                # Pitch down a few times
                for i in range(3):
                        move_mouse_by(0, downVal + 5)
                        time.sleep(1)

        # Air Spawn
        else:
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn In Airspawn')
            wait_on('assets/temp/cancel_spawn.png', True, 0.85)
            
            if aircraft == 'F-84-F':
                time.sleep(4)

            if mode == "rush":
                # Afterburner
                press(KEYBINDS['throttleUp'])
                press(KEYBINDS['radar'])
                # Start CCRP and choose base
                time.sleep(5)
                print('CONSOLE: Activating CCRP')
                press(KEYBINDS['ccrp'])
                time.sleep(5)
                print('CONSOLE: Choosing Target Base')
                press(KEYBINDS['ccrp'])
            elif mode == "slow":
                move_mouse_by(0, -pitch_value)
                time.sleep(15)
                # Find the side bombing point and set holding location
                if get_map_info()[1] < 0.5:
                    target_location = get_holding_location('right', True)
                else:
                    target_location = get_holding_location('left', True)

                att = get_attitude()
                curr_height = att[0]
                height = 7000
                # Climb to 5000m above ground
                print("CONSOLE: Climbing...")
                initialize_bases()
                i = 0
                while not game_over() and curr_height < height/2:
                    if i >=6:
                        count_bases()
                        i = 0
                    i += 1
                    att = get_attitude()
                    curr_height = att[0]
                    pitch_control(height, curr_height, att[1])
                    time.sleep(0.1)
                    target_info = get_target_info(target_location)
                    if target_info:
                        angle = target_info[0]
                        move_mouse_by(int(angle * 10), 0)
                
        

        # Set variables for game loop
        battle_time = time.time()
        base_loc = None
        brake_flag = False
        base_info = None
        map_distance = DISTANCES[map]

        # Set heights (Rush Logic)
        if mode == 'rush':
            print(f"CONSOLE: In the Rush Logic")
            height = HEIGHTS[map]
            if aircraft == 'F-84F':
                if map == 'GolanHeights':
                    height += 400
                elif map == 'Vietnam':
                    height += 200
                else:
                    height += 100

            # Start CCRP and choose base
            if map == "Spain":
                base_num = 1
            else:
                base_num = random.randint(0, 3)
            for i in range(0, base_num):
                print('CONSOLE: Activating CCRP')
                press(KEYBINDS['ccrp'])

        # Slow logic
        else:
            print(f"CONSOLE: In the Slow Logic")

            # Get holding pattern location
            target_info = None
            while target_info is None and not game_over():
                target_info = get_target_info(target_location)
            if target_info:
                distance = target_info[1]
                print(f"CONSOLE: Holding Pattern Angle: {target_info[0]}\nCONSOLE: Holding Pattern Distance: {distance}\nCONSOLE: Heading towards Holding Pattern Point...")

            i = 0
            # Fly towards holding pattern location
            while distance > 0.05 and not game_over():
                target_info = get_target_info(target_location)
                if target_info:
                    distance = target_info[1]
                    angle = target_info[0]
                    move_mouse_by(int(angle * 10), 0)
                attitude = get_attitude()
                if i >= 6:
                    count_bases()
                    i = 0
                i += 1
                pitch_control(height, attitude[0], attitude[1])
            
            
            # Reduce throttle and start holding pattern procedure
            holdFor(KEYBINDS["throttleDown"], 0.1)
            print("CONSOLE: Holding Pattern Initaited")
            while holding_pattern(height) is False and not game_over():
                pass
                
        # Hold down the bombing button
        hold(KEYBINDS['bomb'])

        # Bombing loop
        while not game_over() and base_info is not False:
            
            # Check for CCRP centreline and aim towards it
            centreline_location = pyautogui.locateOnScreen('assets/temp/centreline.png', grayscale=False, confidence=0.7)
            if centreline_location:
                center_x, center_y = pyautogui.center(centreline_location)
                
                screen_width, screen_height = pyautogui.size()
                screen_center_x = screen_width // 2
                
                distance_x = int((center_x - screen_center_x)/2)
                move_mouse_by(distance_x, 0)
                if abs(center_x - screen_center_x) < 5:
                    if base_loc == None:
                        press(KEYBINDS['zoom'])
                        base_loc = calculate_ec_base()
                        print(f"CONSOLE: Chose Target Base with Location: {base_loc}")
                    else:
                        base_loc_new = calculate_ec_base()
                        # Swap bases to new location
                        if base_loc_new != base_loc:
                            print(f"CONSOLE: Chose New Target Base with Location: {base_loc_new}")
                            base_loc = base_loc_new
            
            # Guide by coordinates
            elif base_info and not brake_flag:
                move_mouse_by(int(base_info[0] * 10), 0)
            
            # Get the base information
            if base_loc != None:
                if base_info:
                    old_base_info = base_info
                base_info = get_base_info(base_loc)
                if base_info == False and old_base_info[1] >= 0.07:
                    print(f"CONSOLE: Base is gone before bombing, retargeting...")
                    # Add holding pattern and targeting logic
                    #base_loc = None
                    #press(KEYBINDS["zoom"])
                elif base_info:
                    print(f"\nCONSOLE: Base Distance is: {base_info[1]}\nCONSOLE: Base Location is: {base_info[2]}")
                elif not base_info:
                    print("CONSOLE: Base has been Destroyed")
                    
                    

            # Set new height
            if base_info and mode == "rush" and aircraft != "F-84F":
                height = set_height(mode, map, base_info, height)
                print("Changing height UwU")

            

            # Get attitude of the aircraft
            attitude = get_attitude()

            if base_info:
                base_loc = base_info[2]
                # Deploy airbrakes if close enough to the base
                if not brake_flag and base_info[1] <= map_distance:
                    brake_flag = True
                    if aircraft not in ["F-84F", "Su-25k", "Su-17M2", "Milan", "Mirage-5F"]:
                        print('CONSOLE: Deploying Airbrake')
                        press(KEYBINDS['airbrake'])
                        pyautogui.scroll(-2)
                        if aircraft in ["F-4E", "F-4F", "MiG-23BN"]:
                            press(KEYBINDS['airbrake'])
                            print('CONSOLE: Retracting Airbrake')
                        elif aircraft not in ["F-84F", "Su-25k", "Su-17M2", "Milan", "Mirage-5F"]:
                            # Retract airbrakes when under Mach 1
                            mach = 1.1
                            while mach <= 1.0:
                                print('CONSOLE: Retracting Airbrake')
                                press(KEYBINDS['airbrake'])
                                mach = get_mach()
                    

            # Maintain target altitude
            pitch_control(height, attitude[0], attitude[1])
            
        
        # After Bombing Logic
        # throttle down and smoke
        release(KEYBINDS['bomb'])
        time.sleep(1)
        pyautogui.scroll(-2)
        brake_flag = False
        press(KEYBINDS['smoke'])
        

        # Pitch up
        if aircraft != "Su-25k":
            move_mouse_by(0, -200)
            cruising_height = height + 1500
        else:
            cruising_height = height
        if aircraft in ["Su-25k", "Su-17M2"]:
            holdFor(KEYBINDS["throttleDown"], 0.1)
        time.sleep(1)

        # Fly towards enemy Airfield
        while not game_over():
            attitude = get_attitude()
            field_data = get_field_info()
            # Maintain altitude
            if not brake_flag:
                pitch_control(cruising_height, attitude[0], attitude[1])
            # Aim towards Airfield
            if field_data is not None:
                move_mouse_by(int(field_data[0] * 10), 0)
                # Airbrake and pitch down when close to airfield
                if field_data[1] <= 0.085 and not brake_flag:
                    press(KEYBINDS['airbrake'])
                    if attitude[0] >= 2000:
                        move_mouse_by(0, int(attitude[0]/15))
                    brake_flag = True

            # J out if 10 minutes have passed
            elapsed_time = get_elapsed_time(battle_time)
            if elapsed_time >= 600:
                holdFor('j', 4)


        # After death logic
        # Vehicle has been destroyed, J out
        if pyautogui.locateOnScreen('assets/temp/j_out.png', grayscale=False, confidence=0.85) != None:
            holdFor('j', 4)
            print("CONSOLE: Aircraft Downed: J'ing out")
            time.sleep(1)

        while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) == None and pyautogui.locateCenterOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.85) == None and pyautogui.locateCenterOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.85) == None:
            print('CONSOLE: Waiting on To Hangar/Return To Hangar/OK')

        # Return to Hangar appears
        if pyautogui.locateCenterOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.85) != None:
            print('CONSOLE: Found Return To Hangar after Aircraft Downed')
            while pyautogui.locateCenterOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.85) != None:
                move_mouse_to_image('assets/temp/return_to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)

        # Wait for to Hangar or OK to appear
        while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) == None and pyautogui.locateCenterOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.85) == None:
            print('CONSOLE: Waiting on To Hangar/OK')
            if pyautogui.locateOnScreen('assets/temp/trophy.png', grayscale=False, confidence=0.85) != None:
                print('CONSOLE: Battle Trophy')
                press(KEYBINDS['enter'])
            time.sleep(1)

        if pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.85) != None:
            while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.85) != None:
                print('CONSOLE: Clicking To Hangar')
                move_mouse_to_image('assets/temp/to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)
        elif pyautogui.locateCenterOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.85) != None:
            mod = researched_mod()
            if mod == False:
                print("CONSOLE: Plane has been Researched")
                press('esc')
                time.sleep(4)
                press('esc')
                time.sleep(4)
                press('esc')
            else:
                print("CONSOLE: Modification has been Researched")
            time.sleep(3)


# Main function
def main():
    # CustomTkinter functions
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
        if key == "Gaijiggles":
            return True
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
        global mode
        if agreement_checkbox_var.get() and check_key(key) and resolution is not None and aircraft is not None:
            # Prompt the user to Alt + Tab to War Thunder
            messagebox.showinfo("Alert", "Please Alt + Tab to War Thunder")
            root.destroy()
            # Allow time for user to Alt + Tab
            time.sleep(5)

            # Set bot method
            if mode_checkbox_var.get():
                mode = "slow"
            else:
                mode = "rush"

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
        elif not agreement_checkbox_var.get():
            messagebox.showinfo("Error", "Please agree to use responsibly.")
        else:
            messagebox.showinfo("Error", "Incorrect Key")

    # Create the main window
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    agreement_checkbox_var = tk.BooleanVar()
    mode_checkbox_var = tk.BooleanVar()
    key_var = tk.StringVar()

    root.protocol("WM_DELETE_WINDOW", on_window_close)
    root.geometry("800x750")
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
            '1920x1080': "1080",
            '2560x1080': "1080uw",
            '2560x1440': "1440",
            '3840x2160': "2160"
        }
        global resolution
        resolution = resolutions[choice]


    #4K = "3840x2160"
    resolution_box = ctk.CTkComboBox(master=frame,
                                        values=["1920x1080", "2560x1080", "2560x1440"],
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
            'MiG-23BN (GR)': 'MiG-23BN',
            'Milan (FR)' : 'Milan',
            'Mirage 5F (FR)' : 'Mirage-5F',
            'F-84F (FR)' : 'F-84F',
            'Su-25k (RU)' : 'Su-25k',
            'F-4E (US)' : 'F-4E'
        }
        global aircraft
        aircraft = aircrafts[choice]

    aircraft_box = ctk.CTkComboBox(master=frame,
                                        values=["Kfir Canard (IS)", "F-4F (GR)", "MiG-23BN (GR)", "Milan (FR)", "Mirage 5F (FR)", "F-84F (FR)", "Su-25k (RU)", "F-4E (US)"],
                                        command=choose_aircraft,
                                        variable=aircraft_var)
    aircraft_box.pack(padx=20, pady=10)

    mode_checkbox = ctk.CTkCheckBox(master=frame, text="Use slow method", variable=mode_checkbox_var)
    mode_checkbox.pack(pady=12, padx=10)

    start_button = ctk.CTkButton(master=frame, text="Start Bot", command=start_bot)
    start_button.pack(pady=12, padx=10)

    checkbox = ctk.CTkCheckBox(master=frame, text="I agree to use responsibly", variable=agreement_checkbox_var)
    checkbox.pack(pady=12, padx=10)

    root.iconbitmap("assets/icons/favicon.ico")
    # Start the GUI main loop
    root.mainloop()


# Start the main thread
if __name__ == "__main__":
    main()
     
            