# Define the colors we will use in RGB format
import threading
import os 
import sys

def resource_path(relative_path):
    """ Get absolute path to resource folder, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    repath = os.path.join(base_path, "Resources")

    return os.path.join(repath, relative_path)

def font_locator(filename):
	return os.path.join(resource_path("Fonts"),filename)

def audio_locator(filename):
	return os.path.join(resource_path("Audio"),filename)
def userdata_locator(filename):
	return os.path.join(resource_path("UserData"),filename)

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
PURPLE = (138,43,226)
RED =   (255,   0,   0)
GRAY = (128,128,128)
ORANGE = (255,165,0)
HIGHLIGHTED_CELL_COLOR = (192,192,255)
SELECTED_CELL_COLOR = (37,122,253)

colorMap={"RED":RED, "BLUE":BLUE, "BLACK":BLACK, "GREEN":GREEN, "WHITE":WHITE,"PURPLE":PURPLE,"GRAY":GRAY,"GREY":GRAY,"ORANGE":ORANGE}

boxSideLength = 20
boxStrokeWidth = 1
boxStrokeColor = BLUE
backgroundColor = WHITE
fontColor = BLACK
show_grid = True


calmingMode = False
numSounds = 14


fileSaveLoc = None



lock = threading.RLock()
programIsRunning = True


#dictionary for storing what symbols have text in them
#the key is actually the string representation of a dictionary which holds the cell coordinates (in the format of selectedcell)
#(you can't use pure dictionaries as keys)
# i use json's dumps() function to turn dicts to strings, which is nice because i can use json's loads() function to turn the strings right back into dicts
#the value is a string representing the digit in the cell represented by the key.
symbolcontainer = {}
