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
import dotenv
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
import io
import platform
import cpuinfo
import multiprocessing
import pytesseract
import subprocess

# Global Variables
resolution = None
aircraft = None
throttle = None
brake = None
slope_es = None
suicide = False
pitch_multiplier = 1.0
distance_multiplier = 1.0
dotenv_path = ".env"

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
with open('data/heights.txt', 'rb') as file:
    contents = file.read()
    
# Evaluate the contents as Python code
HEIGHTS = eval(contents)

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

# Read from chat_phrases.txt and store in the CHAT_PHRASES list
with open("data/chat_phrases.txt", "r") as file:
    CHAT_PHRASES = file.read().splitlines()

# Read from pyrenees_phrases.txt and store in the PYRENEES_PHRASES list
with open("data/pyrenees_phrases.txt", "r") as file:
    PYRENEES_PHRASES = file.read().splitlines()

# Check if the lists are empty and assign two blank strings if they are
if not CHAT_PHRASES:
    CHAT_PHRASES = ["", ""]

if not PYRENEES_PHRASES:
    PYRENEES_PHRASES = ["", ""]

# Set the path to Tesseract OCR executable (change this if necessary)
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR/tesseract.exe'

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
    if pyautogui.locateCenterOnScreen("assets/temp/j_out.png", grayscale=False, confidence=0.75) == None and pyautogui.locateCenterOnScreen("assets/temp/to_hangar.png", grayscale=False, confidence=0.75) == None and pyautogui.locateCenterOnScreen("assets/temp/return_to_hangar.png", grayscale=False, confidence=0.75) == None and pyautogui.locateCenterOnScreen("assets/temp/trophy.png", grayscale=False, confidence=0.75) == None and pyautogui.locateCenterOnScreen("assets/temp/ok.png", grayscale=False, confidence=0.75) == None:
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

def find_text_on_screen(target_text):
    # Perform OCR on the screenshot to recognize text
    screenshot = pyautogui.screenshot()
    extracted_text = pytesseract.image_to_string(screenshot)

    # Check if the target text is present in the extracted text
    if target_text in extracted_text:
        return True
    else:
        return False

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
            pass
    return None

# Query localhost for location data
def get_map_data():
    url = 'http://localhost:8111/map_info.json'
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

def spawned_in():
    json_data = get_location_data()
    if json_data:
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        if player:
            return True
        return False
    
def spawn_screen():
    json_data = get_location_data()
    if json_data:
        types_to_check = ["aircraft", "ground_model", "defending_point", "bombing_point", "respawn_base_bomber"]
        for obj in json_data:
            if obj["type"] in types_to_check:
                return True
        return False

def in_game():
    json_data = get_location_data()
    if json_data:
        field = next((obj for obj in json_data if obj["type"] == "airfield"), None)
        if field:
            json_data2 = get_map_data()
            if json_data2 and 'valid' in json_data2 and json_data2['valid'] is False:
                return False
            return True
        return False
    return False

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
def find_target_base():
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
         

def calculate_slope(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1)

# Returns the angle, distance, and location toward the enemy airfield
def get_friendly_field_info(map_name):
    field_x = None
    field_y = None
    global slope_es
    json_data = get_location_data()
    if json_data:
        player = next((obj for obj in json_data if obj["icon"] == "Player"), None)
        field = next((obj for obj in json_data if obj["type"] == "airfield" and obj["color"] == "#174DFF"), None)
        if player and field:
            x, y, dx, dy = player["x"], player["y"], player["dx"], player["dy"]
            if "ALT" in map_name:
                slope_xy = calculate_slope(field["sx"], field["sy"], x, y)
                if slope_es is None:
                    slope_es = calculate_slope(field["sx"], field["sy"], field["ex"], field["ey"])
            else:
                slope_xy = calculate_slope(x, y, field["ex"], field["ey"])
                if slope_es is None:
                    slope_es = calculate_slope(field["ex"], field["ey"], field["sx"], field["sy"])
            print(slope_xy)
            print(slope_es)
            if slope_xy > slope_es + 0.5 or slope_xy < slope_es - 0.5:
                if "ALT" in map_name:
                    if slope_xy < slope_es:
                        glide_x, glide_y = field["ex"] - 0.2, field["ey"] - 0.2
                    elif slope_xy > slope_es:
                        glide_x, glide_y = field["ex"] + 0.2, field["ey"] - 0.2
                else:
                    if slope_xy < slope_es:
                        glide_x, glide_y = field["sx"] + 0.2, field["sy"] + 0.2
                    elif slope_xy > slope_es:
                        glide_x, glide_y = field["sx"] - 0.2, field["sy"] + 0.2
                print(f"{glide_x}, {glide_y}")
                angle = math.atan2(glide_y - y, glide_x - x)
                facing_angle = math.atan2(dy, dx)
                turn_angle = angle - facing_angle
                angle_degrees = math.degrees(turn_angle)
            else:
                if "ALT" in map_name:
                    field_x, field_y = field["sx"], field["sy"]
                else:
                    field_x, field_y = field["ex"], field["ey"]
                angle = math.atan2(field_y - y, field_x - x)
                facing_angle = math.atan2(dy, dx)
                turn_angle = angle - facing_angle
                angle_degrees = math.degrees(turn_angle)
            if not field_x or not field_y:
                field_x, field_y = field["sx"], field["sy"]
            distance = math.sqrt((x - field_x)**2 + (y - field_y)**2)
            return angle_degrees, distance
        
def get_enemy_field_info():
    json_data = get_location_data()
    if json_data:
        field = next((obj for obj in json_data if obj["type"] == "airfield" and obj["color"] == "#fa0C00"), None)
        if field:
            field_x = round((field["sx"] + field["ex"]) / 2, 2)
            field_y = round((field["sy"] + field["ey"]) / 2, 2)
            return get_target_info((field_x, field_y))
            

#########################
#   Control Functions   #
#########################

def holding_pattern(height):
    move_mouse_by(-700, 0)
    time.sleep(2)
    attitude = get_attitude()
    (height, attitude[0], attitude[1], False)
    press(KEYBINDS['ccrp_off'])
    press(KEYBINDS['ccrp'])
    base_count = count_bases()
    time.sleep(1)
    if pyautogui.locateOnScreen('assets/temp/centreline.png', grayscale=False, confidence=0.7) != None and base_count >= 1:
        return True
    else:
        return False

# Change the pitch of the plane based on height and RoC
def pitch_control(target_height, curr_height, attitude, zoom = False, final = False):
    height_diff = curr_height - target_height
    # Calculate the scaling factor based on the resolution
    global resolution
    global pitch_multiplier
    scaling_factor = 1.0
    if resolution == "1440":
        scaling_factor = 1.333
    elif resolution == "2160":
        scaling_factor = 2.0
    if not zoom:
        scaling_factor = scaling_factor/1.3
    
    if height_diff > 0:
        print(f"CONSOLE: pitch_control(): Aircraft is above target height by {height_diff}m")
    else:
        print(f"CONSOLE: pitch_control(): Aircraft is below target height by {-height_diff}m")
    if attitude > 0:
        print(f"CONSOLE: pitch_control(): Aircraft is ascending by {attitude}m/s")
    else:
        print(f"CONSOLE: pitch_control(): Aircraft is descending by {-attitude}m/s")

    
    if height_diff > 450:
        if attitude > 40.0:
            move_mouse_by(0, int(350 * scaling_factor))
        elif attitude > 20.0:
            move_mouse_by(0, int(230 * scaling_factor))
        elif attitude > 15.0:
            move_mouse_by(0, int(200 * scaling_factor))
        elif attitude > 0.0:
            move_mouse_by(0, int(130 * scaling_factor))
        elif attitude > -5.0:
            move_mouse_by(0, int(60 * scaling_factor))
        elif attitude > -10.0:
            move_mouse_by(0, int(30 * scaling_factor))
        elif attitude > -20.0:
            move_mouse_by(0, int(15 * scaling_factor))
    elif height_diff <= 100 and height_diff > 1:
        if attitude > -10.0:
            move_mouse_by(0, int(-30 * scaling_factor))
        elif attitude > -20.0:
            move_mouse_by(0, int(-85 * scaling_factor))
    elif height_diff > 0:
        if attitude > 20.0:
            move_mouse_by(0, int(130 * scaling_factor))
        elif attitude > 10.0:
            move_mouse_by(0, int(60 * scaling_factor))
        elif attitude > 5.0:
            move_mouse_by(0, int(25 * scaling_factor))
        elif attitude > -5.0:
            move_mouse_by(0, int(15 * scaling_factor))
    elif height_diff < 0:
        if attitude < -40.0:
            move_mouse_by(0, int(-250 * scaling_factor))
        elif attitude < -30.0:
            move_mouse_by(0, int(-200 * scaling_factor))
        elif attitude < -25.0:
            move_mouse_by(0, int(-280 * scaling_factor))
        elif attitude < -20.0:
            move_mouse_by(0, int(-130 * scaling_factor))
        elif attitude < -10.0:
            move_mouse_by(0, int(-60 * scaling_factor))
        elif attitude < -5.0:
            move_mouse_by(0, int(-25 * scaling_factor))
        elif attitude < 5.0:
            move_mouse_by(0, int(-15 * scaling_factor))



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

def type_key(key):
    hold(key)
    time.sleep(np.random.uniform(0.02,0.07)) 
    release(key)

# Hold a given key for a specified amount of time
def holdFor(key, seconds):
    hold(key)
    time.sleep(seconds) 
    release(key)

# Made for typing messages
def typer(map_name=""):
    if map_name == "Pyrenees":
        phrase = random.choice(PYRENEES_PHRASES)
    else:
        phrase = random.choice(CHAT_PHRASES)
    for key in phrase:
        if key.isupper():
            type_key('caps')
            type_key(key.lower())
            type_key('caps')
        else:
            type_key(key.lower())

            
        
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

# Define a dictionary to map conditions to heights
heights_map = {
    ('rush', 'GolanHeightsALT', 650): (lambda base_info: base_info[1] <= 0.26),
    ('rush', 'GolanHeights', 550): (lambda base_info: base_info[1] <= 0.26),
    ('rush', 'Sinai', 500): (lambda base_info: base_info[2][0] >= 0.35),
    ('rush', 'Vietnam', 1200): (lambda base_info: base_info[2][0] >= 0.513),
    ('rush', 'Spain', 550): (lambda base_info: base_info[1] <= 0.16),
    ('rush', 'City', 850): (lambda base_info: base_info[2][0] <= 0.32),
    ('rush', 'City', 1000): (lambda base_info: base_info[2][0] >= 0.32),
    ('rush', 'VietnamALT', 1200): (lambda base_info: base_info[2][0] <= 0.390249) 
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
                print(f"CONSOLE: Changing back {map_name} Height to from {height} to {HEIGHTS[map_name]}")
                height = HEIGHTS[map_name]
            break
    return height

# Research Protocol
def research_protocol():
    researched = False
    # If these are false, it is a new Aircraft
    if pyautogui.locateOnScreen('assets/temp/finish.png', grayscale=False, confidence=0.85) != None:
        print('CONSOLE: Found Finish for Aircraft Modification')
        while pyautogui.locateOnScreen('assets/temp/finish.png', grayscale=False, confidence=0.7) != None:
            move_mouse_to_image('assets/temp/finish.png')
            click_mouse()
            print("CONSOLE: Trying to click Finish")
            time.sleep(0.5)
        print("CONSOLE: Modification has been Researched")
        researched = True
    elif pyautogui.locateOnScreen('assets/temp/spend.png', grayscale=False, confidence=0.85) != None:
        print('CONSOLE: Found Spend for Aircraft Modification')
        while pyautogui.locateOnScreen('assets/temp/spend.png', grayscale=False, confidence=0.7) != None:
            move_mouse_to_image('assets/temp/spend.png')
            click_mouse()
            print("CONSOLE: Trying to click Spend")
            time.sleep(0.5)
        print("CONSOLE: Modification has been Researched")
        researched = True

    time.sleep(4)

    # All modifications in a row are researched
    if pyautogui.locateOnScreen('assets/temp/all_mods.png', grayscale=False, confidence=0.7) != None:
        print('CONSOLE: Found all_mods for Aircraft Modification')
        while pyautogui.locateOnScreen('assets/temp/all_mods.png', grayscale=False, confidence=0.7) != None:
            move_mouse_to_image('assets/temp/all_mods.png')
            click_mouse()
            print("CONSOLE: Trying to click all_mods")
            time.sleep(0.5)

    # A plane has been reserached
    if pyautogui.locateCenterOnScreen('assets/temp/order.png', grayscale=False, confidence=0.85) != None:
        print("CONSOLE: Plane has been Researched")
        press('esc')
        time.sleep(4)
        press('esc')
        researched = True

    return researched


# Bot Loop
def bot():
    # Import Globals
    global aircraft
    global resolution
    global mode
    global bases_arr
    global bot_mode
    global brake
    global throttle
    global flare
    global suicide
    global pitch_multiplier
    global distance_multiplier

    # Set scaling factor for mouse inputs based on resolution
    scaling_factor = 1.0
    if resolution == "1440":
        scaling_factor = 1.333
    elif resolution == "2160":
        scaling_factor = 2.0
    
    # Pitch values
    pitch_value = int(pitch_multiplier * 200 * scaling_factor)
    downVal = int(pitch_value/8)

    # Preset parameters
    if bot_mode == "preset":
        aircraft_settings = {
            "F-84F": {"brake": "No", "throttle": "Full", "airspawn": True},
            "Su-25k": {"brake": "No", "throttle": "Full", "airspawn": False},
            "Su-17M2": {"brake": "No", "throttle": "Slow", "airspawn": False},
            "Milan": {"brake": "No", "throttle": "Full", "airspawn": False},
            "Mirage-5F": {"brake": "No", "throttle": "Full", "airspawn": False},
            "F-4E": {"brake": "Tap", "throttle": "Slow", "airspawn": False},
            "F-4F": {"brake": "Tap", "throttle": "Slow", "airspawn": False},
            "MiG-23BN": {"brake": "Tap", "throttle": "Slow", "airspawn": False},
        }

        default_settings = {"brake": "Full", "throttle": "Slow", "airspawn": False}
        aircraft_data = aircraft_settings.get(aircraft, default_settings)
        brake = aircraft_data["brake"]
        throttle = aircraft_data["throttle"]
        airspawn = aircraft_data["airspawn"]
    # Custom parameters
    else:
        airspawn = False
        aircraft = None
        mode = "rush"


    # Process the bin folder
    process_bin_folder(f"assets/bin/{resolution}")

    # Bot loop
    while True:
        # Initialize variables for the match
        bases_arr = []
        start_loop = time.time()
        zoom = False

        # Hangar Loop
        while in_game() == False:
            waiting_for = get_elapsed_time(start_loop)
            if waiting_for > 600 or find_text_on_screen("Trophy") == True:
                press('esc')

            if research_protocol():
                time.sleep(2)

            if pyautogui.locateOnScreen('assets/temp/decal.png', grayscale=False, confidence=0.85) != None:
                print('CONSOLE: Decal')
                move_mouse_to_image('assets/temp/decal.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(2)
            
            # if trophy is not None or to_hangar is not None or repaired is not None:
            press(KEYBINDS['enter'])
            
            time.sleep(0.5)
            in_queue = pyautogui.locateOnScreen('assets/temp/in_queue.png', grayscale=False, confidence=0.95)
            if in_queue is not None or find_text_on_screen("Waiting") == True:
                break

        # Waiting to join a battle
        print("\n\nCONSOLE: To Battle!")
        print('CONSOLE: Waiting in Qeue...')
        while in_game() == False:
            pass
        print('CONSOLE: In Spawn Screen')
        
        # Initialize variables
        move_mouse_to(100, 100)
        city = False
        map_name = ''
        inc = 0

        # Check which map_name match is taking place on
        while inc <= 5:
            map_coords=get_map_info()
            try:
                map_name = MAPS[map_coords]
                if map_name == 'City' or map_name == 'CityALT':
                    city = True
                break
            except:
                print(f"CONSOLE: Map not found; map_coords are {map_coords}")
                # Temp variable
                map_name = 'RockyCanyonALT'
            inc += 1
            time.sleep(0.5)
        print(f'CONSOLE: Map is {map_name}') 

        # Take off/spawn procedure
        battle_time = time.time()
        if not city and not airspawn:
            # Press enter to spawn in
            while not spawn_screen():
                pass
            if not spawned_in():
                press(KEYBINDS['enter'])
                print("CONSOLE: Spawn Button Clicked")

            print('CONSOLE: Waiting to Spawn on Airfield')
            while not spawned_in():
                pass
            print('CONSOLE: Spawned in\nCONSOLE: Activating CCRP')
            # Throttle up, then pitch up
            holdFor(KEYBINDS['throttleUp'], 2)
            press(KEYBINDS['secondary'])  
            press(KEYBINDS['ccrp'])            
            move_mouse_by(0, -pitch_value)
            press(KEYBINDS['radar'])
            
            ground = get_attitude()[0]
            holdFor(KEYBINDS['throttleUp'], 2)
            chat_check = random.randint(0, 2)
            if chat_check <= 0:
                press('enter')
                press('tab')
                typer(map_name)
                press('enter')
            else:
                press('t')
                press('1')
                press('4')

            # Retract gear when taken off
            height = ground
            while height <= ground + 5 and not game_over():
                height = get_attitude()[0]
            print('CONSOLE: Retracting Landing Gear')
            press(KEYBINDS['gear'])
            
            if mode == 'rush':
            # Choose base target
                while pyautogui.locateOnScreen('assets/temp/centreline.png', grayscale=False, confidence=0.7) == None and not game_over() and spawned_in() and height < HEIGHTS[map_name]/4:
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
                while not game_over() and spawned_in() and curr_height < height/2:
                    curr_height = get_attitude()[0]
                    time.sleep(0.1)
                    target_info = get_target_info(target_location)
                    if target_info:
                        angle = target_info[0]
                        move_mouse_by(int(angle * 10 * scaling_factor), 0)
                # Pitch down a few times
                for i in range(3):
                        move_mouse_by(0, downVal + 5)
                        time.sleep(1)

        # Air Spawn
        else:
            # Wait to Spawn in
            while not spawn_screen():
                pass
            if not spawned_in():
                press(KEYBINDS['enter'])
                print("CONSOLE: Spawn Button Clicked")
            print('CONSOLE: Waiting to Spawn in Airspawn')
            while not spawned_in():
                pass
        
            if aircraft == 'F-84-F':
                time.sleep(2)

            if mode == "rush":
                # Afterburner
                press(KEYBINDS['throttleUp'])
                press(KEYBINDS['radar'])
                # Start CCRP and choose base
                time.sleep(5)
                print('CONSOLE: Activating CCRP')
                press(KEYBINDS['secondary'])  
                press(KEYBINDS['ccrp'])
                time.sleep(5)
                print('CONSOLE: Choosing Target Base')
                press(KEYBINDS['ccrp'])
            elif mode == "slow":
                move_mouse_by(0, -pitch_value)
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
                while not game_over() and spawned_in() and curr_height < height/2:
                    if i >=6:
                        count_bases()
                        i = 0
                    i += 1
                    att = get_attitude()
                    curr_height = att[0]
                    pitch_control(height, curr_height, att[1], zoom)
                    time.sleep(0.1)
                    target_info = get_target_info(target_location)
                    if target_info:
                        angle = target_info[0]
                        move_mouse_by(int(angle * 10 * scaling_factor), 0)
                
        

        # Set variables for game loop
        battle_time = time.time()
        base_loc = None
        brake_flag = False
        base_info = None
        map_distance = distance_multiplier * DISTANCES[map_name]
        pyrenees_flag = False

        # Set heights (Rush Logic)
        if mode == 'rush':
            height = HEIGHTS[map_name]
            if airspawn:
                if map_name == 'GolanHeights':
                    height += 400
                elif map_name == 'Vietnam':
                    height += 200
                else:
                    height += 100

            # Start CCRP and choose base
            print('CONSOLE: Choosing Target Base')
            if map_name == "Spain":
                base_num = 1
            else:
                base_num = random.randint(0, 3)
            base_num = 1
            for i in range(0, base_num):
                press(KEYBINDS['ccrp'])

        # Slow logic
        else:
            # Get holding pattern location
            target_info = None
            while target_info is None and not game_over() and spawned_in():
                target_info = get_target_info(target_location)
            if target_info:
                distance = target_info[1]
                print(f"CONSOLE: Holding Pattern Angle: {target_info[0]}\nCONSOLE: Holding Pattern Distance: {distance}\nCONSOLE: Heading towards Holding Pattern Point...")
            else:
                distance = 1
                
            i = 0
            # Fly towards holding pattern location
            while distance > 0.05 and not game_over() and spawned_in():
                target_info = get_target_info(target_location)
                if target_info:
                    distance = target_info[1]
                    angle = target_info[0]
                    move_mouse_by(int(angle * 10 * scaling_factor), 0)
                attitude = get_attitude()
                if i >= 6:
                    count_bases()
                    i = 0
                i += 1
                pitch_control(height, attitude[0], attitude[1], zoom)
            
            # Reduce throttle and start holding pattern procedure
            holdFor(KEYBINDS["throttleDown"], 0.05)
            print("CONSOLE: Holding Pattern Initaited")
            while holding_pattern(height) is False and not game_over() and spawned_in():
                pass
                
        bomb_flag = False
        print("Before Bombing loop")
        # Bombing loop
        while not game_over() and spawned_in() and base_info is not False:
            print("IN BOMBING LOOP")
            # Check for CCRP centreline and aim towards it
            centreline_location = pyautogui.locateOnScreen('assets/temp/centreline.png', grayscale=False, confidence=0.7)
            if centreline_location:
                print("CCRP Line Found")
                center_x, center_y = pyautogui.center(centreline_location)
                
                screen_width, screen_height = pyautogui.size()
                screen_center_x = screen_width // 2
                
                distance_x = int((center_x - screen_center_x)/1.5)
                move_mouse_by(distance_x, 0)
                if abs(center_x - screen_center_x) < 5:
                    if base_loc == None:
                        press(KEYBINDS['zoom'])
                        zoom = True
                        base_loc = find_target_base()
                        print(f"CONSOLE: Chose Target Base with Location: {base_loc}")
                    else:
                        base_loc_new = find_target_base()
                        # Swap bases to new location
                        if base_loc_new != base_loc:
                            print(f"CONSOLE: Chose New Target Base with Location: {base_loc_new}")
                            base_loc = base_loc_new
            
            # Guide by coordinates
            elif base_info and not brake_flag:
                move_mouse_by(int(base_info[0] * 10 * scaling_factor), 0)
            
            # Get the base information
            if base_loc:
                if base_info:
                    old_base_info = base_info
                base_info = get_base_info(base_loc)
                if base_info == False and old_base_info[1] >= 0.07:
                    print(f"CONSOLE: Base has been stolen, retargeting...")
                    # Zoom out
                    # If further than 0.3, retarget
                    # If closer, head to holding pattern and throttle down
                elif base_info:
                    print(f"CONSOLE: Base Distance is: {base_info[1]}")
                    if base_info[0] >= 100:
                        print("CONSOLE: Base has been Destroyed")
                        break
                elif not base_info:
                    print("CONSOLE: Base has been Destroyed")
                    break

            # Set new height
            if base_info and mode == "rush" and not airspawn:
                height = set_height(mode, map_name, base_info, height)

            # Get attitude of the aircraft
            attitude = get_attitude()
                        # Maintain target altitude
            pitch_control(height, attitude[0], attitude[1], zoom)
            if map_name == "Pyrenees" and attitude[0] >= 3000 and not pyrenees_flag:
                move_mouse_by(-800, 0)
                pyrenees_flag = True

            if base_info:
                base_loc = base_info[2]
                # Deploy airbrakes if close enough to the base
                if not bomb_flag and base_info[1] <= 0.3:
                    # Hold down the bombing button
                    hold(KEYBINDS['bomb'])
                    bomb_flag = True
                if not brake_flag and base_info[1] <= map_distance:
                    brake_flag = True
                    if throttle == "Slow":
                        print("Slowing down")
                        pyautogui.scroll(-2)
                    if brake != "No":
                        print('CONSOLE: Deploying Airbrake')
                        press(KEYBINDS['airbrake'])
                        if brake == "Tap":
                            press(KEYBINDS['airbrake'])
                            print('CONSOLE: Retracting Airbrake')
                        else:
                            # Retract airbrakes when under Mach 1
                            mach = 1.1
                            while mach >= 1.0:
                                mach = get_mach()
                            print('CONSOLE: Retracting Airbrake')
                            press(KEYBINDS['airbrake'])
            
        
        # After Bombing Logic
        # throttle down and smoke
        if game_over() == False:
            release(KEYBINDS['bomb'])
            time.sleep(1)
            pyautogui.scroll(-2)
            brake_flag = False
            zoom = False

            
            if suicide:
                print("CONSOLE: Heading towards Enemy Airfield")
            else:
                print("CONSOLE: Heading towards Friendly Airfield")
                time.sleep(1)
                move_mouse_by(int(-800 * scaling_factor), 0)
                time.sleep(1)
                move_mouse_by(int(-800 * scaling_factor), 0)
                time.sleep(1)
                move_mouse_by(int(-800 * scaling_factor), 0)
                press('t')
                press('4')
                press('4')
            
            # Pitch up
            if mode == "slow":
                cruising_height = height
                holdFor(KEYBINDS["throttleDown"], 0.1)
            elif suicide:
                move_mouse_by(0, int(-150 * scaling_factor))
                cruising_height = HEIGHTS[map_name] + 1500
            else:
                move_mouse_by(int(-800 * scaling_factor), int(-150 * scaling_factor))
                cruising_height = HEIGHTS[map_name] + 200

            if throttle == "Slow":
                holdFor(KEYBINDS["throttleDown"], 0.1)
                
            
            final = False

        # Fly towards enemy Airfield
        while not game_over() and spawned_in():
            attitude = get_attitude()
            if suicide:
                field_data = get_enemy_field_info()
            else:
                field_data = get_friendly_field_info(map_name)

            if not brake_flag:
                pitch_control(cruising_height, attitude[0], attitude[1], zoom, final)
            # Aim towards Airfield
            
            if field_data is not None:
                distance_to_airfield = field_data[1]
                if distance_to_airfield >= 0.04:
                    move_mouse_by(int(field_data[0] * 10 * scaling_factor), 0)
                print(f"Airfield is {distance_to_airfield} distance away")
                
                # Airbrake and pitch down when close to the airfield
                if not suicide and distance_to_airfield <= 0.12:
                    if distance_to_airfield <= 0.08:
                        hold(KEYBINDS['throttleDown'])
                        cruising_height = ground + 20
                    elif distance_to_airfield <= 0.03:
                        release(KEYBINDS['throttleDown'])
                    else:
                        cruising_height = ground + 200
                    
                    if distance_to_airfield <= 0.05 and not brake_flag:
                        press(KEYBINDS['airbrake'])
                        brake_flag = True
                        press('t')
                        press('4')
                        press('3')
                elif suicide and not brake_flag and distance_to_airfield <= 0.04:
                    press(KEYBINDS['airbrake'])
                    move_mouse_by(0, int(attitude[0]/4))
                    hold(KEYBINDS['throttleDown'])
                    brake_flag = True
                if not suicide and attitude[0] < cruising_height + 200:
                    final = True

            # J out if 10 minutes have passed
            elapsed_time = get_elapsed_time(battle_time)
            if elapsed_time >= 600:
                holdFor('j', 4)

        release(KEYBINDS['throttleDown'])
        # After death logic
        # Vehicle has been destroyed, J out
        if pyautogui.locateOnScreen('assets/temp/j_out.png', grayscale=False, confidence=0.85) != None:
            holdFor('j', 4)
            print("CONSOLE: Aircraft Downed: J'ing out")
            time.sleep(1)
        
        while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.75) == None and pyautogui.locateCenterOnScreen('assets/temp/return_to_hangar.png', grayscale=False, confidence=0.85) == None and pyautogui.locateCenterOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.85) == None:
            print('CONSOLE: Waiting on To Hangar/Return To Hangar/OK')
            if pyautogui.locateOnScreen('assets/temp/trophy.png', grayscale=False, confidence=0.85) != None:
                print('CONSOLE: Battle Trophy')
                press(KEYBINDS['enter'])
            time.sleep(2)

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
            if pyautogui.locateOnScreen('assets/temp/decal.png', grayscale=False, confidence=0.85) != None:
                print('CONSOLE: Decal')
                move_mouse_to_image('assets/temp/decal.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(2)
            time.sleep(1)

        if pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.95) != None:
            while pyautogui.locateCenterOnScreen('assets/temp/to_hangar.png', grayscale=False, confidence=0.85) != None:
                print('CONSOLE: Clicking To Hangar')
                move_mouse_to_image('assets/temp/to_hangar.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)
        elif pyautogui.locateCenterOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.95) != None:
            while pyautogui.locateCenterOnScreen('assets/temp/ok.png', grayscale=False, confidence=0.85) != None:
                print('CONSOLE: Clicking OK')
                move_mouse_to_image('assets/temp/ok.png')
                click_mouse()
                move_mouse_to(100, 100)
                time.sleep(3)
                
        research_protocol()
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
        global dotenv_path
        key_str = key_entry_home.get()
        key_var.set(key_str)
        dotenv.set_key(dotenv_path, "activation_key", key_str)
    
    def key_exists(key):
        key_var.set(key)


    def check_key(key):
        # Get the user's IP address
        pc_info = get_pc_info()

        if pc_info:
            url = os.getenv('server_ip')

            pc_name, pc_cpu_name = pc_info
            # JSON payload for the request
            payload = {
                'users_key': key,
                'users_pc_name': pc_name,
                'users_pc_cpu' : pc_cpu_name
            }

            response = requests.post(url, json=payload)

            if response.text == "True":
                return True
            return False

        else:
            messagebox.showinfo("Error", "check_key(): Unable to get PC information")
            print("CONSOLE: Unable to retrieve PC information")
            return False

    def get_pc_info():
        pc_name = platform.node()
        pc_cpuinfo = cpuinfo.get_cpu_info()
        pc_cpu_name = pc_cpuinfo["brand_raw"]
        return pc_name, pc_cpu_name

    # Function to start the bot
    def start_bot():
        key = key_var.get()
        global resolution
        global aircraft
        global mode
        global bot_mode
        global brake
        global throttle
        global suicide
        global dotenv_path
        valid_key = check_key(key)
        if bot_mode == "preset" and agreement_checkbox_var.get() and valid_key and resolution is not None and aircraft is not None:
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

            if suicide_checkbox_var.get():
                suicide = True
                dotenv.set_key(dotenv_path, "suicide", "1")
            else:
                suicide = False
                dotenv.set_key(dotenv_path, "suicide", "0")

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

        elif bot_mode == "custom" and agreement_checkbox_var.get() and valid_key and resolution is not None and throttle is not None and brake is not None:
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
        
        elif not valid_key:
            messagebox.showinfo("Error", "Incorrect Key")
        elif resolution is None:
            messagebox.showinfo("Error", "Please Choose a Resolution")
        elif bot_mode == "preset" and aircraft is None:
            messagebox.showinfo("Error", "Please Choose an Aircraft")
        elif bot_mode == "custom" and throttle is None:
            messagebox.showinfo("Error", "Please Choose Throttle Behavior")
        elif bot_mode == "custom" and brake is None:
            messagebox.showinfo("Error", "Please Choose Airbrake Behavior")
        elif not agreement_checkbox_var.get():
            messagebox.showinfo("Error", "Please agree to use responsibly.")
        else:
            messagebox.showinfo("Error", "Something went wrong")
    
    def choose_resolution(choice):
        resolutions = {
            '1920x1080': "1080",
            '2560x1080': "1080uw",
            '2560x1440': "1440",
            '3840x2160': "2160"
        }
        global resolution
        global dotenv_path
        resolution_box_settings.set(choice)
        resolution = resolutions[choice]
        dotenv.set_key(dotenv_path, "resolution", choice)
        

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

    def choose_brakes(choice):
        print("Brakes Chosen: ", choice)
        brakes = {
            'No Airbrake': 'No',
            'Tap Airbrake': 'Tap',
            'Hold Airbrake': 'Hold',
        }
        global brake
        brake = brakes[choice]
    
    def choose_throttle(choice):
        print("Throttle Chosen: ", choice)
        throttles = {
            'Full Throttle': 'Full',
            'Kill Afterburner': 'Slow',
        }
        global throttle
        throttle = throttles[choice]
        
    
    # Create the main window
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    agreement_checkbox_var = tk.BooleanVar()
    mode_checkbox_var = tk.BooleanVar()
    key_var = tk.StringVar()
    flares_checkbox_var = tk.BooleanVar()
    suicide_checkbox_var = tk.BooleanVar()

    root.protocol("WM_DELETE_WINDOW", on_window_close)
    root.geometry("800x750")
    root.title("War Thunder Air Bot 1.0")

    # Create the sidebar
    sidebar = ctk.CTkFrame(master=root)
    sidebar.pack(side="left", fill="y")

    # Load the image for the button
    image_path_home = "assets/icons/home.png"
    sidebar_image_home = ctk.CTkImage(Image.open(image_path_home), size=[30, 30])

    image_path_custom = "assets/icons/wrench.png"
    sidebar_image_custom = ctk.CTkImage(Image.open(image_path_custom), size=[30, 30])

    # Load the image for the button
    image_path_settings = "assets/icons/gear.png"
    sidebar_image_settings = ctk.CTkImage(Image.open(image_path_settings), size=[35, 35])

    # Initialize different screens
    frame = ctk.CTkFrame(master=root)
    frame2 = ctk.CTkFrame(master=root)
    frame3 = ctk.CTkFrame(master=root)
    frame4 = ctk.CTkFrame(master=root)

    # Change Screen Functions
    def change_to_home():
        global bot_mode
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        frame2.pack_forget()
        frame3.pack_forget()
        frame4.pack_forget()
        bot_mode = "preset"

    def change_to_custom():
        global bot_mode
        frame2.pack(pady=20, padx=20, fill="both", expand=True)
        frame.pack_forget()
        frame3.pack_forget()
        frame4.pack_forget()
        bot_mode = "custom"

    def change_to_settings():
        frame3.pack(pady=20, padx=20, fill="both", expand=True)
        frame.pack_forget()
        frame2.pack_forget()
        frame4.pack_forget()

    def change_to_heights():
        frame4.pack(pady=20, padx=20, fill="both", expand=True)
        frame.pack_forget()
        frame2.pack_forget()
        frame3.pack_forget()
    
    # SideBar Buttons
    sidebar_button_home = ctk.CTkButton(master=sidebar, text="", image=sidebar_image_home, command=change_to_home, width=65, height=60)
    sidebar_button_home.pack(pady=10, padx=10)

    sidebar_button_custom = ctk.CTkButton(master=sidebar, text="", image=sidebar_image_custom, command=change_to_custom, width=65, height=60)
    sidebar_button_custom.pack(pady=10, padx=10)

    sidebar_button_settings = ctk.CTkButton(master=sidebar, text="", image=sidebar_image_settings, command=change_to_settings, width=65, height=60)
    sidebar_button_settings.pack(pady=10, padx=10)

    # Menu Logos
    main_logo = ctk.CTkImage(Image.open("assets/icons/main_menu_icon.png"), size=[164, 139])
    logo_label_home = ctk.CTkLabel(frame, text="", image=main_logo)
    logo_label_home.pack(pady=12, padx=10)

    custom_logo = ctk.CTkImage(Image.open("assets/icons/custom_menu_icon.png"), size=[164, 139])
    logo_label_custom = ctk.CTkLabel(frame2, text="", image=custom_logo)
    logo_label_custom.pack(pady=12, padx=10)

    settings_logo = ctk.CTkImage(Image.open("assets/icons/settings_menu_icon.png"), size=[164, 139])
    logo_label_settings = ctk.CTkLabel(frame3, text="", image=settings_logo)
    logo_label_settings.pack(pady=12, padx=10)

    # Menu Titles
    label_home = ctk.CTkLabel(master=frame, text="Nicks War Thunder Air Bot 1.0\nMain Menu", font=("Roboto", 24))
    label_home.pack(pady=12, padx=10)

    label_custom = ctk.CTkLabel(master=frame2, text="Nicks War Thunder Air Bot 1.0\nCustom Menu", font=("Roboto", 24))
    label_custom.pack(pady=12, padx=10)

    label_settings = ctk.CTkLabel(master=frame3, text="Nicks War Thunder Air Bot 1.0\nSettings Menu", font=("Roboto", 24))
    label_settings.pack(pady=12, padx=10)

    label_heights = ctk.CTkLabel(master=frame4, text="Nicks War Thunder Air Bot 1.0\nMinimum Height Settings Menu", font=("Roboto", 24))
    label_heights.pack(pady=12, padx=10)

    # Setup and Instructions
    instructions_label_home = ctk.CTkLabel(master=frame,
                                      text="Preset Setup Instructions:\n1. Go to Hangar and have the appropriate aircraft selected\n2. Select 'Air Realistic Battles'\n3. Ensure you are using Red and Blue default colors\n\nTo end the program, press and hold 'q' at any time",
                                      font=("Roboto", 15))
    instructions_label_home.pack(pady=12, padx=10)

    instructions_label_custom = ctk.CTkLabel(master=frame2,
                                      text="Custom Setup Instructions:\n1. In the Main Menu, input your Activation Key\n2. Select the behavior options relevant to your Aircraft\n3. Go to Hangar and have the appropriate aircraft selected\n4. Select 'Air Realistic Battles'\n5. Ensure you are using Red and Blue default colors\n\nTo end the program, press and hold 'q' at any time",
                                      font=("Roboto", 15))
    instructions_label_custom.pack(pady=12, padx=10)

    instructions_label_settings = ctk.CTkLabel(master=frame3,
                                      text="Here you can adjust your settings.\nThey are automatically saved.",
                                      font=("Roboto", 15))
    instructions_label_settings.pack(pady=12, padx=10)

    instructions_label_heights = ctk.CTkLabel(master=frame4,
                                      text="Here you can adjust the minimum height for a map.\nClick save once you have made your changes.",
                                      font=("Roboto", 15))
    instructions_label_heights.pack(pady=12, padx=10)


    key_entry_home = ctk.CTkEntry(master=frame, placeholder_text="Activation Key", show="*")
    key_entry_home.pack(pady=12, padx=10)

    # Get key from .env
    activation_key = os.getenv("activation_key")

    if activation_key:
        key_entry_home.insert(0, activation_key)
        key_exists(activation_key)

    # Bind the function to the text change event of the entry widget
    key_entry_home.bind("<KeyRelease>", update_key_var)


    # Resolution Setting
    resolution_var = os.getenv("resolution")

    if not resolution_var:
        resolution_var = ctk.StringVar(value="Select Resolution")

    # Create a label to display the pitch_multiplier value
    resolution_label_settings = ctk.CTkLabel(master=frame3, text=f"Select Resolution", font=("Roboto", 12))
    resolution_label_settings.pack(pady=0, padx=10)

    resolution_box_settings = ctk.CTkComboBox(master=frame3,
                                        values=["1920x1080", "2560x1080", "2560x1440"],
                                        command=choose_resolution,
                                        variable=resolution_var)
    resolution_box_settings.pack(padx=10, pady=10)

    if 'resolution' in os.environ:
        choose_resolution(resolution_var)

    
    # Aircraft drop down
    aircraft_var_home = ctk.StringVar(value="Select Aircraft")  # set initial value

    aircraft_box_home = ctk.CTkComboBox(master=frame,
                                        values=["Kfir Canard (IS)", "F-4F (GR)", "MiG-23BN (GR)", "Milan (FR)", "Mirage 5F (FR)", "F-84F (FR)", "Su-25k (RU)", "F-4E (US)"],
                                        command=choose_aircraft,
                                        variable=aircraft_var_home)
    aircraft_box_home.pack(padx=20, pady=10)

    # Throttle
    throttle_var_custom = ctk.StringVar(value="Throttle Behavior")  # set initial value

    throttle_box_custom = ctk.CTkComboBox(master=frame2,
                                        values=["Full Throttle", "Kill Afterburner"],
                                        command=choose_throttle,
                                        variable=throttle_var_custom)
    throttle_box_custom.pack(padx=20, pady=10)

    # Airbrake
    airbrake_var_custom = ctk.StringVar(value="Airbrake Behavior")  # set initial value

    airbrake_box_custom = ctk.CTkComboBox(master=frame2,
                                        values=["No Airbrake", "Tap Airbrake", "Hold Airbrake"],
                                        command=choose_brakes,
                                        variable=airbrake_var_custom)
    airbrake_box_custom.pack(padx=20, pady=10)

    # Flares Checkbox
    flares_checkbox_custom = ctk.CTkCheckBox(master=frame2, text="Aircraft has Flares", variable=flares_checkbox_var)
    flares_checkbox_custom.pack(pady=12, padx=10)


    # Suicide setting
    suicide_checkbox_settings = ctk.CTkCheckBox(master=frame3, text="Aircraft heads to enemy Airfield?\n              (More detectable)", variable=suicide_checkbox_var)
    suicide_checkbox_settings.pack(pady=12, padx=10)

    suicide_var = os.getenv("suicide")

    if suicide_var == "1":
        suicide_checkbox_settings.select()
    

    mode_checkbox_home = ctk.CTkCheckBox(master=frame, text="Use slow method", variable=mode_checkbox_var)
    mode_checkbox_home.pack(pady=12, padx=10)

    # Pitch Adjustment    
    pitch_multiplier = os.getenv("pitch_multiplier")

    if not pitch_multiplier:
        pitch_multiplier = 1.0
    else:
        pitch_multiplier = float(pitch_multiplier)

    def slider_event(number):
        global pitch_multiplier
        global dotenv_path
        pitch_multiplier = number
        # Update the label text with the current pitch_multiplier value
        pitch_multiplier_label_settings.configure(text=f"Pitch Up Multiplier: {pitch_multiplier}")
        dotenv.set_key(dotenv_path, "pitch_multiplier", str(pitch_multiplier))

    # Create a label to display the pitch_multiplier value
    pitch_multiplier_label_settings = ctk.CTkLabel(master=frame3, text=f"Pitch Up Multiplier: {pitch_multiplier}", font=("Roboto", 12))
    pitch_multiplier_label_settings.pack(pady=5, padx=10)

    # Create and pack the pitch slider
    pitch_slider_settings = ctk.CTkSlider(master=frame3, from_=1, to=6, number_of_steps=20, command=slider_event)
    pitch_slider_settings.pack(pady=1, padx=10)

    if not pitch_multiplier:
        pitch_multiplier = 1.0
    else:
        pitch_multiplier = float(pitch_multiplier)
        pitch_multiplier_label_settings.configure(text=f"Pitch Up Multiplier: {pitch_multiplier}")

    pitch_slider_settings.set(pitch_multiplier)

    # Distance Adjustment    
    distance_multiplier = os.getenv("distance_multiplier")

    if not distance_multiplier:
        distance_multiplier = 1.0
    else:
        distance_multiplier = float(distance_multiplier)

    def distance_slider_event(number):
        global distance_multiplier
        global dotenv_path
        distance_multiplier = math.trunc(number * 10) / 10
        # Update the label text with the current distance_multiplier value
        distance_multiplier_label_settings.configure(text=f"Distance Multiplier: {distance_multiplier}")
        dotenv.set_key(dotenv_path, "distance_multiplier", str(distance_multiplier))

    # Create a label to display the distance_multiplier value
    distance_multiplier_label_settings = ctk.CTkLabel(master=frame3, text=f"Distance Multiplier: {distance_multiplier}", font=("Roboto", 12))
    distance_multiplier_label_settings.pack(pady=5, padx=10)

    # Create and pack the distance slider
    distance_slider_settings = ctk.CTkSlider(master=frame3, from_=0.1, to=3, number_of_steps=29, command=distance_slider_event)
    distance_slider_settings.pack(pady=1, padx=10)

    if not distance_multiplier:
        distance_multiplier = 1.0
    else:
        distance_multiplier = float(pitch_multiplier)
        distance_multiplier_label_settings.configure(text=f"Distance Multiplier: {distance_multiplier}")

    distance_slider_settings.set(distance_multiplier)

    
    def change_chat_phrases():
        file_path = "data/chat_phrases.txt"
        
        try:
            subprocess.Popen(["notepad.exe", file_path])
        except FileNotFoundError:
            print("Notepad not found. Make sure Notepad is installed on your system.")
    
    def change_keybinds():
        file_path = "data/keybinds.txt"
        
        try:
            subprocess.Popen(["notepad.exe", file_path])
        except FileNotFoundError:
            print("Notepad not found. Make sure Notepad is installed on your system.")
        
    def change_heights():
        file_path = "data/heights.txt"
        
        try:
            subprocess.Popen(["notepad.exe", file_path])
        except FileNotFoundError:
            print("Notepad not found. Make sure Notepad is installed on your system.")

    chat_phrases_button_settings = ctk.CTkButton(master=frame3, text="Change Chat Phrases", command=change_chat_phrases)
    chat_phrases_button_settings.pack(pady=12, padx=10)

    keybinds_button_settings = ctk.CTkButton(master=frame3, text="Change Keybinds", command=change_keybinds)
    keybinds_button_settings.pack(pady=12, padx=10)

    heights_button_settings = ctk.CTkButton(master=frame3, text="Change Minimum Height", command=change_heights)
    heights_button_settings.pack(pady=12, padx=10)

    #Height Adjustment Menu

    # Aircraft drop down
    def choose_map():
        pass
    map_var_heights = ctk.StringVar(value="Select Map")  # set initial value

    map_var_heights = ctk.CTkComboBox(master=frame4,
                                        values=[
    'Afghanistan',
    'GolanHeights',
    'GolanHeightsALT',
    'Sinai',
    'SinaiALT',
    'Spain',
    'SpainALT',
    'SpainEC',
    'Vietnam',
    'VietnamALT',
    'VietnamEC',
    'RockyCanyon',
    'RockyCanyonALT',
    'City',
    'CityALT',
    'Pyrenees',
    'PyreneesALT',
    'LadogaLeft',
    'BerlinRight'
],
                                        command=choose_map,
                                        variable=aircraft_var_home)
    map_var_heights.pack(padx=20, pady=10)

    height_val = 200
    def slider_event_2(number):
        global height_val
        global dotenv_path
        height_val = int(number)
        # Update the label text with the current pitch_multiplier value
        height_entry_heights.delete(0, "end")
        height_entry_heights.insert(0, height_val)

    # Create a label to display the pitch_multiplier value
    label_heights = ctk.CTkLabel(master=frame4, text=f"Map Minimum Height", font=("Roboto", 12))
    label_heights.pack(pady=5, padx=10)

    height_entry_heights = ctk.CTkEntry(master=frame4, placeholder_text="Minimum Height", width=75, justify="center")
    height_entry_heights.pack(pady=12, padx=10)
    height_entry_heights.insert(0, height_val)

    # Create and pack the pitch slider
    slider_heights = ctk.CTkSlider(master=frame4, from_=200, to=6000, width=600, number_of_steps=5800, command=slider_event_2)
    slider_heights.pack(pady=1, padx=10)

    slider_heights.set(height_val)
    
    def update_height():
        pass
    # Bind the function to the text change event of the entry widget
    start_button_custom = ctk.CTkButton(master=frame4, text="Save Changes", command=update_height)
    start_button_custom.pack(pady=12, padx=10)

    
    start_button_home = ctk.CTkButton(master=frame, text="Start Bot", command=start_bot)
    start_button_home.pack(pady=12, padx=10)

    start_button_custom = ctk.CTkButton(master=frame2, text="Start Bot", command=start_bot)
    start_button_custom.pack(pady=12, padx=10)

    checkbox_home = ctk.CTkCheckBox(master=frame, text="I agree to use responsibly", variable=agreement_checkbox_var)
    checkbox_home.pack(pady=12, padx=10)

    checkbox_custom = ctk.CTkCheckBox(master=frame2, text="I agree to use responsibly", variable=agreement_checkbox_var)
    checkbox_custom.pack(pady=12, padx=10)

    root.iconbitmap("assets/icons/favicon.ico")
    # Start the GUI main loop
    change_to_home()
    root.mainloop()


# Start the main thread
# Start the main thread
if __name__ == "__main__":
    # When running as a Python script, just call the main function as you're doing currently
    multiprocessing.freeze_support()
    main()
            