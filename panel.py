import threading
import cmdColors as cc
import json
import settings as st
import os
import sys
from shutil import copyfile


def isMac():
	return sys.platform == "darwin"

def warn(text):
	if(not isMac()):
		print(text)
	else:
		print(cc.WARNING + text + cc.ENDC)
def fail(text):
	if(not isMac()):
		print(text)
	else:
		print(cc.FAIL + text + cc.ENDC)
def ok(text):
	if(not isMac()):
		print(text)
	else:
		print(cc.OKBLUE + text + cc.ENDC)

def toggleGrid():
	st.lock.acquire()
	st.show_grid = not st.show_grid
	st.lock.release()
def setBoxWidth(width):
	st.lock.acquire()
	st.boxSideLength = width;
	st.lock.release()
def setFontColor(color):
	st.lock.acquire()
	st.fontColor = color
	st.lock.release()
def setBackgroundColor(color):
	st.lock.acquire()
	st.backgroundColor = color
	st.lock.release()
def setGridColor(color):
	st.lock.acquire()
	st.boxStrokeColor = color
	st.lock.release()
def toggleCalm():
	st.lock.acquire()
	st.calmingMode = not st.calmingMode
	st.lock.release()
def loadFileSaveLoc():
	st.lock.acquire()
	try:
		file = open(st.userdata_locator("home.txt"),"r")
		st.fileSaveLoc = file.readline()
		file.close()
	except:
		warn("no file storage path has been set. To save files, specify a path with the home command")
	st.lock.release()







class PanelThread (threading.Thread):
	def __init__(self,name):
		threading.Thread.__init__(self)
		self.name = name
	def run(self):
		loadFileSaveLoc()


		print("Command List:")
		print("Aesthetics:")
		print("    tg -> toggles gridlines")
		print("    bw {integer} -> changes box width to given integer")
		print("    fc {COLOR} -> changes font color to a given color")
		print("    bc {COLOR} -> changes background color to a given color")
		print("    gc {COLOR} -> changes grid color to a given color")

		print("Files:")
		print("    home {PATH} -> sets the home directory path")
		print("    whatis home -> print the home directory path")
		print("    list -> lists all .cm files in the home directory")
		print("    save {FILENAME} -> saves work as a .cm file with given filename in the home directory. Overwrites if filename is taken")
		print("    open {FILENAME} -> opens a .cm file. Does not save current work.")
		print("Other:")

		print("    exit -> exits the program. does not save")
		print("    calm -> toggles calming mode.")


		print("    do not type the curly braces in the command line. for example a valid command is 'fc red'")

		while st.programIsRunning:

			x = input();
			if(x=="tg"):
				toggleGrid()
				ok("gridlines toggled")

			elif(x[:2]=="bw"):
				try:
					if int(x[3:]) >= 20:
						setBoxWidth(int(x[3:]))
						ok("box width changed")
					else:
						warn("Sorry, box length must be at least 20")
				except ValueError:
					fail("Sorry, the integer you entered was not valid. Enter 'bw' followed by a space and then an integer")
			elif(x[:2] =="fc"):
				if x[3:].upper() in st.colorMap:
					setFontColor(st.colorMap[x[3:].upper()])
					ok("font color changed")
				else:
					warn("Sorry, we don't have that color.")
			elif(x[:2] =="bc"):
				if x[3:].upper() in st.colorMap:
					setBackgroundColor(st.colorMap[x[3:].upper()])
					ok("background color changed")
				else:
					warn("Sorry, we don't have that color.")
			elif(x[:2] =="gc"):
				if x[3:].upper() in st.colorMap:
					setGridColor(st.colorMap[x[3:].upper()])
					ok("grid color changed")
					if(not st.show_grid):
						print("gridlines must be toggled on to see the grid")
				else:
					warn("Sorry, we don't have that color.")

			elif(x[:4] == "save"):
				st.lock.acquire()
				if st.fileSaveLoc == None:
					warn("you must specify a home directory to save your cm files to.")
				else:
					if x[-3:] == ".cm":
						x = x[:-3]
					try:
						file = open(os.path.join(st.fileSaveLoc,(x[5:] + ".cm")),"w")
						file.write(json.dumps(st.symbolcontainer))
						file.close()
						ok("file saved as '" + x[5:] + "'")
					except:
						fail("There was an error saving your file. Check that your home directory path is valid")
				st.lock.release()


			elif(x[:4]=="open"):
				st.lock.acquire()
				if st.fileSaveLoc == None:
					warn("you must specify a home directory to open your cm files from.")
				else:
					if x[-3:] == ".cm":
						x = x[:-3]
					try:
						file = open(os.path.join(st.fileSaveLoc,(x[5:] + ".cm")),"r")

						st.symbolcontainer = json.loads(file.readline())
					
						ok("file opened successfully")
					except FileNotFoundError:
						fail("File could not be found. Check that your home directory path is valid")
					except:
						fail("There was an error opening your file. Check that your home directory path is valid")

				st.lock.release()

			elif(x[:4]=="home"):
				st.lock.acquire()
				try:
					file = open(st.userdata_locator("home.txt"),"w")
					file.write(x[5:])
					file.close()
					loadFileSaveLoc()
					ok("home directory saved successfully")
				except:
					fail("There was an error setting your home directory.")
				st.lock.release()


			elif(x=="list"):
				st.lock.acquire()

				if st.fileSaveLoc == None:
					warn("you must specify a home directory to open your cm files from.")
				else:
					try:
						print("Saved CM files:")
						files = os.listdir(st.fileSaveLoc)
						for file in files:
							if file[-3:] == ".cm":
								print ("    " + file)
					except:
						fail("An error occured, check that your home directory path is valid")
				st.lock.release()
			elif(x=="whatis home"):
				st.lock.acquire()
				if st.fileSaveLoc == None:
					warn("you have not yet set a home directory")
				else:
					ok("your home directory is located at " + st.fileSaveLoc)
				st.lock.release()

			elif(x=="exit"):
				st.programIsRunning = False
			elif(x=="calm"):
				toggleCalm()
				print("toggled calming mode")
			else:
				fail("Sorry, your command wasn't recognized.")
