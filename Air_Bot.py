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

# Allow the use of relative paths
os.chdir(os.path.dirname(__file__))
script_folder = os.path.dirname(__file__)
# Change the permissions of all files in the script's folder to allow all users to read and write to them
for file in os.listdir(script_folder):
    file_path = os.path.join(script_folder, file)
    os.chmod(file_path, 0o666)

# PyAutoGui Failsafe off
pyautogui.FAILSAFE = False

game_stats = []

MAPS = {
    'GolanHeights' : 560,
    'Sinai' : 150,
    'Spain' : 1070,
    'Vietnam' : 800,
    'city' : 0
}

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
  'f12': 0x58}

# Get User's KeyBinds from file
with open('keybinds.txt', 'r') as file:
    # Read the contents of the file
    contents = file.read()

# Evaluate the contents as Python code
KEYBINDS = eval(contents)


# Phrases that can be typed in chat
phrase_count = -1
with open('chat_phrases.txt', 'r') as file:
    # create an empty list
    CHATPHRASES = []
    # iterate over the lines in the file
    for line in file:
        # strip leading and trailing whitespace from the line
        line = line.strip()
        if line and not line.startswith('#'):
            # add the line to the list
            CHATPHRASES.append(line)
            phrase_count += 1


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
def get_height():
    url = 'http://localhost:8111/state'  # Replace with your URL
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON string
        json_data = json.loads(response.text)

        # Access the value of "H, m"
        return json_data["H, m"]
    
def get_aoa():
    url = 'http://localhost:8111/state'  # Replace with your URL
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON string
        json_data = json.loads(response.text)

        # Access the value of "H, m"
        return json_data["AoA, deg"]


# End Program
def end_program():
    # Send the signal to terminate the program
    os.kill(os.getpid(), 9)

def move_mouse_randomly():
  # Move the mouse randomly a few times
  for _ in range(random.randint(3, 6)):
    move_mouse_by(x=random.randint(-250, 250), y=random.randint(-10, 15))
    # Wait a little before moving the mouse again
    time.sleep(random.uniform(0.1, 0.5))

def click_mouse():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0) 
    time.sleep(np.random.uniform(0.3,0.5)) 
    win32api.mouse_event(win32con. MOUSEEVENTF_LEFTUP, 0, 0)

# Chat a random phrase
def random_chat():
    # Pick a Random message
    message = random.choice(CHATPHRASES)
    print(f'CONSOLE: Typing Message : {message}')
    press('enter')
    time.sleep(np.random.uniform(0.3,0.7)) 
    for letter in message:
        if letter.isupper() == True:
            press('caps')
            type(letter.lower())
            press('caps')
        else:
            type(letter)
    press('enter')

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
        time.sleep(np.random.uniform(0.5,0.7))
        click(button[0], button[1])
        button = pyautogui.locateCenterOnScreen(image_path, grayscale=False, confidence=0.75)
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
            press(KEYBINDS['enter'])
            time.sleep(0.3)
        print("CONSOLE: To Battle!")

        # Wait to Join Battle
        print(f'CONSOLE: Waiting in Qeue...')
        while pyautogui.locateCenterOnScreen('assets/spawn.png', grayscale=False, confidence=0.8) == None:
            pass
        
        # In Battle, click the Spawn In button
        press(KEYBINDS['enter'])
        print("CONSOLE: Spawn Button Clicked") 

        time.sleep(np.random.uniform(0.5,0.7))
        if pyautogui.locateOnScreen('assets/vietnam.png', grayscale=False, confidence=0.95) != None:
            map = 'Vietnam'
        elif pyautogui.locateOnScreen('assets/golan_heights.png', grayscale=False, confidence=0.95) != None:
            map = 'GolanHeights'
        elif pyautogui.locateOnScreen('assets/spain.png', grayscale=False, confidence=0.95) != None:
            map = 'Spain'
        elif pyautogui.locateOnScreen('assets/sinai.png', grayscale=False, confidence=0.95) != None:
            map = 'Sinai'
        elif pyautogui.locateOnScreen('assets/city.png', grayscale=False, confidence=0.95) != None:
            map = 'city'
        height = MAPS[map]

        # Get current time
        battle_time = time.time()

        if map != 'city':
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn In')
            while pyautogui.locateOnScreen('assets/cancel.png', grayscale=False, confidence=0.7) != None:
                pass
            # Pitch values
            pitch_value = 368
            downVal = int(pitch_value/8)

            # Throttle up, then pitch up
            holdFor('w', 4)
            move_mouse_by(0, -pitch_value)
        
            # Start CCRP and choose base
            print('CONSOLE: Activating CCRP')
            press(KEYBINDS['ccrp'])

            while get_elapsed_time(battle_time) < 45.0:
                pass
            print('Done waiting!!!')
            # Retract gear
            press(KEYBINDS['gear'])

            press(KEYBINDS['ccrp'])
            while pyautogui.locateOnScreen('assets/centreline.png', grayscale=False, confidence=0.7) == None:
                pass
            
            # Slowly pitch the plane back to level
            for i in range(5):
                move_mouse_by(0, downVal)
                time.sleep(1)
        else:
            # Wait to Spawn in
            print('CONSOLE: Waiting to Spawn In')
            while pyautogui.locateOnScreen('assets/cancel.png', grayscale=False, confidence=0.7) != None:
                pass
            press('w')
            # Start CCRP and choose base
            print('CONSOLE: Activating CCRP')
            press(KEYBINDS['ccrp'])

        # 60% chance that the bot will Chat this game
        choice = random.randint(0, 10)
        choice = 10
        if choice <= 6 and phrase_count >= 0:
            chat_flag = False
            # Set the Chat to All
            press('enter')
            time.sleep(np.random.uniform(1.2,1.7))
            press('tab')
            time.sleep(np.random.uniform(1.2,1.7))
            press('enter')
        else:
            chat_flag = True

        # Set variables for game loop
        battle_time = time.time()
        time_report = 1
        zoom_time = 0
        zoom_flag = False
        brake_flag = False
        print(map)
        
    
        hold(KEYBINDS['bomb'])

        # Bombing loop
        while pyautogui.locateOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.7) == None:
            
            # Report the time every 20 cycles
            if time_report >= 20:
                time_report = -1
            elif time_report == 0:
                # Print how long the bot ahs been in a match
                current_time = time.time()
                minutes, seconds = divmod(int(current_time - battle_time), 60)
                if seconds <= 9:
                    seconds = '0' + str(seconds)
                print(f'CONSOLE: Playing Game...\nCONSOLE: Elapsed Time : {minutes}:{seconds}')
            time_report += 1
            
            # Type a message in chat
            choice = random.randrange(0, phrase_count)
            if chat_flag == False:
                chat_flag = True
                random_chat()

            # Locate the CCRP line and move the mouse towards it
            location = pyautogui.locateOnScreen('assets/centreline.png', grayscale=False, confidence=0.7)
            if location is not None:
                center_x, center_y= pyautogui.center(location)
                
                # Get the screen's center coordinates
                screen_width, screen_height = pyautogui.size()
                screen_center_x = screen_width // 2
                
                # Calculate the distance between the target center and the screen's center
                distance_x = int((center_x - screen_center_x)/5)
                move_mouse_by(distance_x, 0)
            else:
                release(KEYBINDS['bomb'])
                break

            # Wait 10 cycles before zooming in
            if zoom_time >= 10 and zoom_flag == False:
                press(KEYBINDS['zoom'])
                zoom_flag = True
            zoom_time += 1
            
            # Check the height based on map and adjust AoA
            if get_height() > height + 100 and get_aoa() > 0.0:
                move_mouse_by(0, 15)
            elif get_height() < height + 50:
                move_mouse_by(0, -15)


        #  After Bombing pitch up and bait enemies
        press(KEYBINDS['zoom'])
        press(KEYBINDS['smoke'])
        press(KEYBINDS['airbrake'])
        move_mouse_by(0, -200)
        while pyautogui.locateOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.7) == None and pyautogui.locateOnScreen('assets/to_hangar.png', grayscale=False, confidence=0.7) == None:
            move_mouse_by(10, 0)
            time.sleep(np.random.uniform(1.2,1.7))

        # Vehicle has been destroyed
        if pyautogui.locateCenterOnScreen('assets/return_to_hangar.png', grayscale=False, confidence=0.75) != None:
            print('CONSOLE: Aircraft Downed, Returning to Hangar')
            # Click 'Return To Hangar' Button
            clicked = False
            while clicked == False:
                clicked = click_button('assets/return_to_hangar.png')
            time.sleep(np.random.uniform(20,30))

            # Click 'To Hangar' Button
            clicked = False
            while clicked == False:
                clicked = click_button('assets/to_hangar.png')
        # Match has ended
        else:
            print('CONSOLE: Match Ended, Returning to Hangar')
            # Click 'To Hangar' Button
            clicked = False
            while clicked == False:
                clicked = click_button('assets/to_hangar.png')


#Operation Spain 1052m, 1 check
#Operation Vietnam 670m, 2 check
title_banner = """
  _   _ ___ ____ _  ______   __        ___    ____    _____ _   _ _   _ _   _ ____  _____ ____    ____   ___ _____   _   _ 
 | \ | |_ _/ ___| |/ / ___|  \ \      / / \  |  _ \  |_   _| | | | | | | \ | |  _ \| ____|  _ \  | __ ) / _ \_   _| / | / |
 |  \| || | |   | ' /\___ \   \ \ /\ / / _ \ | |_) |   | | | |_| | | | |  \| | | | |  _| | |_) | |  _ \| | | || |   | | | |
 | |\  || | |___| . \ ___) |   \ V  V / ___ \|  _ <    | | |  _  | |_| | |\  | |_| | |___|  _ <  | |_) | |_| || |   | |_| |
 |_| \_|___\____|_|\_\____/     \_/\_/_/   \_\_| \_\   |_| |_| |_|\___/|_| \_|____/|_____|_| \_\ |____/ \___/ |_|   |_(_)_|
                                                                                                                           
                                                                                                                    
"""
# Main function
def main():
    # Main menu
    print(title_banner)
    print('Welcome to Nicks War Thunder Air Bot 1.1\nThis program is designed to help you generate silver lions AFK in War Thunder.\n\nSetup Instructions : \n1. Check the KeyBinds file and ensure that your keybinds are set up correctly\n2. Go to Hangar and have the Kfir Canard (Israel) selected \n3. Select "Air Realistic Battles"\n\nTo end the program press and hold "q" at any time')

    while True:
        # Prompt the user for input
        user_input = input("\nPlease press Enter to execute program : ")

        # If the user presses enter, execute the program
        if user_input == "":
            time.sleep(2)
            break
        elif user_input == 'q' or user_input == 'Q':
            end_program()
        else:
            print('CONSOLE: Error, "Enter" (Start Bot) or "q" (Quit Program) were not inputted')


    # Allow time for User to Alt-Tab
    print('\nCONSOLE: Starting Program...')
    print('Please Alt + Tab to War Thunder\n')
    for i in range(5):
        print(f'CONSOLE: Starting Bot in {5 - i} Seconds...')
        time.sleep(1)

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
        
            


# Start the main thread
main()