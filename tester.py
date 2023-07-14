# Import Statements
from cryptography.fernet import Fernet
from pyautogui import *
import pyautogui
import os

# Allow the use of relative paths
os.chdir(os.path.dirname(__file__))
script_folder = os.path.dirname(__file__)

# Change the permissions of all files in the script's folder to allow all users to read and write to them
for file in os.listdir(script_folder):
    file_path = os.path.join(script_folder, file)
    os.chmod(file_path, 0o666)

# Iterate over the files in the temp_folder
temp_folder = os.listdir('assets/temp')
for file in temp_folder:
    if pyautogui.locateOnScreen(os.path.join('assets/temp', file), grayscale=False, confidence=0.75) is None:
        print(f"File read: {file}")
    else:
        print(f"File read: {file}")

