from pyautogui import *
import pyautogui
import time

i = 0
while True:
    print(pyautogui.locateOnScreen(r'C:\Users\nickf\Documents\Code\War Thunder Air Bot\assets\return_btn_2.png', grayscale=False, confidence=0.65))
    if pyautogui.locateOnScreen(r'C:\Users\nickf\Documents\Code\War Thunder Air Bot\assets\return_btn_2.png', grayscale=False, confidence=0.7) != None:
        print(f'Cancel Spawn Found {i}')
        break
    time.sleep(0.1)
    print('Not Found')