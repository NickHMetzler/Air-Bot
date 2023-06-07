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
from PIL import ImageTk, Image

# Allow the use of relative paths
os.chdir(os.path.dirname(__file__))
script_folder = os.path.dirname(__file__)
# Change the permissions of all files in the script's folder to allow all users to read and write to them
for file in os.listdir(script_folder):
    file_path = os.path.join(script_folder, file)
    os.chmod(file_path, 0o666)

# PyAutoGui Failsafe off
pyautogui.FAILSAFE = False

# Char/Str to Scancode for Bot Game Inputs
# https://kbdlayout.info/kbdusx/scancodes
KEYS = {
  'a': 0x1E,
  'b': 0x30,
  'c': 0x2E,
  'd': 0x20,
  'e': 0x12,
  'f': 0x21,
  'g': 0x22,
  'h': 0x23,
  'i': 0x17,
  'j': 0x24,
  'k': 0x25,
  'l': 0x26,
  'm': 0x32,
  'n': 0x31,
  'o': 0x18,
  'p': 0x19,
  'q': 0x10,
  'r': 0x13,
  's': 0x1F,
  't': 0x14,
  'u': 0x16,
  'v': 0x2F,
  'w': 0x11,
  'x': 0x2D,
  'y': 0x15,
  'z': 0x2C,
  '1': 0x02,
  '2': 0x03,
  '3': 0x04,
  '4': 0x05,
  '5': 0x06,
  '6': 0x07,
  '7': 0x08,
  '8': 0x09,
  '9': 0x0A,
  '0': 0x0B,
  'enter': 0x1C,
  'esc': 0x01,
  'backspace': 0x0E,
  'tab': 0x0F,
  ' ': 0x39,
  '-': 0x0C,
  '=': 0x0D,
  '[': 0x1A,
  ']': 0x1B,
  '\\': 0x2B,
  '#': 0x0E,
  ';': 0x27,
  '\'': 0x28,
  '`': 0x29,
  ',': 0x33,
  '.': 0x34,
  '/': 0x35,
  'caps': 0x3A,
  'l_shift' : 0x2A,
  'f1': 0x3B,
  'f2': 0x3C,
  'f3': 0x3D,
  'f4': 0x3E,
  'f5': 0x3F,
  'f6': 0x40,
  'f7': 0x41,
  'f8': 0x42,
  'f9': 0x43,
  'f10': 0x44,
  'f11': 0x57,
  'f12': 0x58,
  'up': 0x48,
  'right': 0x4D,
  'left': 0x4B,
  'down': 0x50}

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
#   C struct redefinitions    #
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


#################
#   Functions   #
#################
# Finds the leftmost base
def find_left_base():
    min_x = None
    print('Finding...')
    for _ in range(5):
        pyautogui.press(KEYBINDS['ccrp'])
        time.sleep(0.3)
        position = pyautogui.locateOnScreen('assets/centreline.png', grayscale=False, confidence=0.7)
        
        if position is not None:
            x = position[0]
            if min_x is None or x < min_x:
                min_x = x

    while True:
        pyautogui.press(KEYBINDS['ccrp'])
        time.sleep(0.3)
        position = pyautogui.locateOnScreen('assets/centreline.png', grayscale=False, confidence=0.7)
        
        if position is not None:
            x = position[0]
            if x == min_x:
                break
    print('FOUND IT')

# Returns the current Height and Rate of Climb
def get_attitude():
    url = 'http://localhost:8111/state'
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON string
        json_data = json.loads(response.text)

        # Access the value of "H, m"
        return_data = (json_data["H, m"], json_data["Vy, m/s"])
        print(f'Height is: {return_data[0]}m\nRate of Climb is: {return_data[1]}')
        return return_data

# Returns the distance from the Base
def get_distance(map):
    url = 'http://localhost:8111/map_obj.json'  
    response2 = requests.get(url)

    if response2.status_code == 200:
        # Request successful
        json_data = json.loads(response2.text)
        # Extract x and y values where icon is "Player"
        points = []
        x = None  # Initialize x with a default value
        y = None  # Initialize y with a default value
        for obj in json_data:
            if obj["icon"] == "Player":
                print("Player Coordinates:")
                x = obj["x"]
                y = obj["y"]
            if obj["type"] == "bombing_point":
                points.append(obj["x"])
            
        points_sorted = sorted(set(points))  # Remove duplicates and sort the values
        if map == 'GolanHeights2' or map == 'Spain3' or map == 'Sinai2':
            index = 3
        elif map == 'RockyCanyon' or map == 'Vietnam3':
            index = 0
        elif map == 'City2':
            index = 2
        elif map == 'Spain2' or map == 'Vietnam2':
            index = 4
        else:
            index = 1
        if x is not None and index < len(points_sorted):
            chosen_point = points_sorted[index] 
            point_x = None  # Initialize point_x with a default value
            point_y = None  # Initialize point_y with a default value
            for obj in json_data:
                if obj["type"] == "bombing_point" and obj["x"] == chosen_point:
                    point_x = obj["x"]
                    point_y = obj["y"]
            distance = math.sqrt((x - point_x)**2 + (y - point_y)**2)
        else:
            distance = 0
        print(f'Distance from the base is: {distance}')
        return distance


# Returns the speed in Mach
def get_mach():
    url = 'http://localhost:8111/indicators'  # Replace with your URL
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON string
        json_data = json.loads(response.text)

        # Access the value of "H, m"
        return_data = json_data["mach"]
        print(f'Plane is at Mach {return_data}')
        return return_data
    
# Temp Function
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

# End Program
def end_program():
    # Send the signal to terminate the program
    os.kill(os.getpid(), 9)

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

# Click the provided button
def click_button(image_path):
    button = pyautogui.locateCenterOnScreen(image_path, grayscale=False, confidence=0.75)
    if button != None:
        move_mouse_to(button[0], button[1])
        time.sleep(np.random.uniform(0.9,1.2))
        click(button[0], button[1])
        button = pyautogui.locateCenterOnScreen(image_path, grayscale=False, confidence=0.75)
        return True
    else:
        return False

# Move the Mouse to a given image
def move_mouse_to_image(image_path):
    image = pyautogui.locateCenterOnScreen(image_path, grayscale=False, confidence=0.75)
    if image != None:
        move_mouse_to(image[0], image[1])
        time.sleep(np.random.uniform(0.9,1.2))
        return True
    else:
        return False

# Syntax is lowercase
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

# Function to calculate the elapsed time
def get_elapsed_time(startTime):
    current_time = time.time()
    elapsed_time = current_time - startTime
    return elapsed_time

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
        print(f'CONSOLE: Waiting in Qeue...')
        while pyautogui.locateCenterOnScreen('assets/spawn.png', grayscale=False, confidence=0.8) == None:
            time.sleep(0.1)
        
        # In Battle, click the Spawn In button
        press(KEYBINDS['enter'])
        print("CONSOLE: Spawn Button Clicked") 
        move_mouse_to(100, 100)
        time.sleep(np.random.uniform(0.5,0.7))
        # Temp Variable
        screenshot_val = False

        # Figure out which map
        if pyautogui.locateOnScreen('assets/vietnam3.png', grayscale=False, confidence=0.96) != None:
            map = 'Vietnam3'
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/vietnam2.png', grayscale=False, confidence=0.97) != None:
            map = 'Vietnam2'
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/vietnam1.png', grayscale=False, confidence=0.97) != None:
            map = 'Vietnam1'
        elif pyautogui.locateOnScreen('assets/golan_heights1.png', grayscale=False, confidence=0.97) != None:
            map = 'GolanHeights1'
        elif pyautogui.locateOnScreen('assets/golan_heights2.png', grayscale=False, confidence=0.97) != None:
            map = 'GolanHeights2'
        elif pyautogui.locateOnScreen('assets/spain1.png', grayscale=False, confidence=0.97) != None:
            map = 'Spain1'
        elif pyautogui.locateOnScreen('assets/spain3.png', grayscale=False, confidence=0.97) != None:
            map = 'Spain3'
        elif pyautogui.locateOnScreen('assets/spain2.png', grayscale=False, confidence=0.97) != None:
            map = 'Spain2'
            screenshot_val = True
        elif pyautogui.locateOnScreen('assets/sinai1.png', grayscale=False, confidence=0.97) != None:
            map = 'Sinai1'
        elif pyautogui.locateOnScreen('assets/sinai2.png', grayscale=False, confidence=0.97) != None:
            map = 'Sinai2'
        elif pyautogui.locateOnScreen('assets/city2.png', grayscale=False, confidence=0.97) != None:
            map = 'City2'
        elif pyautogui.locateOnScreen('assets/city1.png', grayscale=False, confidence=0.97) != None:
            map = 'City1'
        elif pyautogui.locateOnScreen('assets/rocky_canyon2.png', grayscale=False, confidence=0.97) != None:
            map = 'RockyCanyon2'
            screenshot_val = True
        else:
            screenshot_val = True
        # Temp condition
        if screenshot_val == True: 
            screenshot_screen()

        print(f'CONSOLE: Map is {map}')

        # Pitch values
        pitch_value = 344
        downVal = int(pitch_value/8)

        # Take off/spawn procedure
        battle_time = time.time()
        if map != 'City1' and map != 'City2':
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn In')
            while pyautogui.locateOnScreen('assets/cancel.png', grayscale=False, confidence=0.7) != None:
                time.sleep(0.1)
            start_time = time.time()
            # Throttle up, then pitch up
            holdFor('w', 4)
            move_mouse_by(0, -pitch_value)
        
            # Start CCRP and choose base
            print('CONSOLE: Activating CCRP')
            press(KEYBINDS['ccrp'])

            while get_elapsed_time(battle_time) < 45.0:
                time.sleep(0.1)
            # Retract gear
            press(KEYBINDS['gear'])
            # Choose base target
            press(KEYBINDS['ccrp'])
            while pyautogui.locateOnScreen('assets/centreline.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/j_out.png', grayscale=False, confidence=0.95) == None:
                time.sleep(0.1)
            # Pitch down a few times
            for i in range(3):
                    move_mouse_by(0, downVal + 5)
                    time.sleep(1)
        # Air Spawn
        else:
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn In')
            while pyautogui.locateOnScreen('assets/cancel.png', grayscale=False, confidence=0.7) != None:
                time.sleep(0.1)
            start_time = time.time()
            # Afterburner
            press('w')
            # Start CCRP and choose base
            time.sleep(5)
            print('CONSOLE: Activating CCRP')
            press(KEYBINDS['ccrp'])
            time.sleep(5)
            press(KEYBINDS['ccrp'])

        # Set variables for game loop
        battle_time = time.time()
        zoom_time = 0
        zoom_flag = False
        brake_flag = False
        if map == 'City1' or map == 'City2':
            pitch_flag = True
        else:
            pitch_flag = False
        mach_flag = False
        map_distance = DISTANCES[map]
        height = HEIGHTS[map]

        if map == 'Spain2' or map == 'Vietnam2':
            print('Finding Left Base')
            find_left_base()
        
        # Hold down the bombing button
        hold(KEYBINDS['bomb'])

        # Bombing loop
        while pyautogui.locateOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/j_out.png', grayscale=False, confidence=0.95) == None:
            # Temp Condition
            if screenshot_val == True and zoom_time == 6 and (map == 'RockyCanyon2' or map == 'Spain3'):
                screenshot_screen()
                hold('m')
                screenshot_screen()
                release('m')
                screenshot_val = False

            # Locate the CCRP line and move the mouse towards it
            location = pyautogui.locateOnScreen('assets/centreline.png', grayscale=False, confidence=0.7)
            if location is not None:
                center_x, center_y= pyautogui.center(location)
                
                # Get the screen's center coordinates
                screen_width, screen_height = pyautogui.size()
                screen_center_x = screen_width // 2
                
                # Calculate the distance between the target center and the screen's center
                distance_x = int((center_x - screen_center_x)/2)
                move_mouse_by(distance_x, 0)
            elif brake_flag == True:
                # Release the bombing button
                release(KEYBINDS['bomb'])
                break

            # Wait 6 cycles before zooming in
            if zoom_time >= 6 and zoom_flag == False:
                press(KEYBINDS['zoom'])
                zoom_flag = True
            zoom_time += 1
            
            # Release flares while subsonic
            if brake_flag == True:
                pyautogui.scroll(-2)
                pyautogui.scroll(2)
                
            # Check if the airbrake can be deactivated
            if brake_flag == True and mach_flag == False:
                mach = get_mach()
                if mach < 1.0:
                    press(KEYBINDS['airbrake'])
                    mach_flag = True

            # Slowly pitch the plane back to level
            attitude = get_attitude()
            if (map != 'City1' and map != 'City2') and pitch_flag == False and attitude[0] > height - 10:
                for i in range(2):
                    move_mouse_by(0, downVal + 5)
                    time.sleep(1)
                pitch_flag = True

            # Hit the airbrake and turn off afterburner when close to the base
            distance = get_distance(map)
            if brake_flag == False and distance <= map_distance:
                press(KEYBINDS['airbrake'])
                pyautogui.scroll(-2) 
                brake_flag = True

            # Maintain level flight
            if pitch_flag == True and brake_flag == False:
                if attitude[0] > height + 100 and attitude[1] > 15.0:
                    move_mouse_by(0, 30)
                elif attitude[0] < height and attitude[1] < -15.0:
                    move_mouse_by(0, -30)
                elif attitude[0] > height + 100 and attitude[1] > 5.0:
                    move_mouse_by(0, 20)
                elif attitude[0] < height and attitude[1] < -5.0:
                    move_mouse_by(0, -20)
                elif attitude[0] > height + 100 and attitude[1] > 0.0:
                    move_mouse_by(0, 7)
                elif attitude[0] < height and attitude[1] < 0.0:
                    move_mouse_by(0, -7)
                elif attitude[0] < height + 100 and attitude[0] > height and attitude[1] > 0.1:
                    move_mouse_by(0, 7)
                elif attitude[0] < height + 100 and attitude[0] > height and attitude[1] < -0.1:
                    move_mouse_by(0, -7)
            
        #  After Bombing pitch up, throttle down, and bait enemies
        time.sleep(1)
        if mach_flag == False:
            press(KEYBINDS['airbrake'])
        press(KEYBINDS['smoke'])
        move_mouse_by(0, -200)
        time.sleep(np.random.uniform(1.2,1.7))
        holdFor('s', 0.3)
        time.sleep(np.random.uniform(1.2,1.7))
        while pyautogui.locateOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/j_out.png', grayscale=False, confidence=0.95) == None:
            move_mouse_by(random.randint(130,170), 0)
            elapsed_time = get_elapsed_time(battle_time)
            # J out if 10 minutes have passed
            if elapsed_time >= 600:
                holdFor('j', 4)

        # Vehicle has been destroyed
        if pyautogui.locateOnScreen('assets/j_out.png', grayscale=False, confidence=0.95) != None:
            holdFor('j', 4)
            print('CONSOLE: Aircraft Downed, Returning to Hangar')
            # Click 'Return To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.75) == None:
                time.sleep(0.1)
            move_mouse_to_image('assets/return_to_hangar.png')
            click_mouse()
            
            # Click 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.75) == None:
                time.sleep(0.1)
            move_mouse_to_image('assets/to_hangar.png')
            click_mouse()
        elif pyautogui.locateCenterOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.75) != None:
            print('CONSOLE: Aircraft Downed, Returning to Hangar')
            # Click 'Return To Hangar' Button
            move_mouse_to_image('assets/return_to_hangar.png')
            click_mouse()

            # Click 'To Hangar' Button
            while pyautogui.locateCenterOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.75) == None:
                time.sleep(0.1)
            move_mouse_to_image('assets/to_hangar.png')
            click_mouse()

        # Match has ended
        else:
            print('CONSOLE: Match Ended, Returning to Hangar')
            # Click 'To Hangar' Button
            move_mouse_to_image('assets/to_hangar.png')
            click_mouse()

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

        # Check if the user presses key 'q' then quit the program
        while True:
            if keyboard.is_pressed('q'):
                # handle the 'q' key press
                print("CONSOLE: Exiting program")
                # Quit the program
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
     
            