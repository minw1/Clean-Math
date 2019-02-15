import threading
import cmdColors as cc
import json
import settings as st
import os
import sys
from shutil import copyfile

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



class PanelThread (threading.Thread):
	def __init__(self,name):
		threading.Thread.__init__(self)
		self.name = name
	def run(self):
		print("Command List:")
		print("Aesthetics:")
		print("    tg -> toggles gridlines")
		print("    bw {integer} -> changes box width to given integer")
		print("    fc {COLOR} -> changes font color to a given color")
		print("    bc {COLOR} -> changes background color to a given color")
		print("    gc {COLOR} -> changes grid color to a given color")

		print("Files:")
		print("    list -> lists all .cm files in the current directory")
		print("    save {FILENAME} -> saves work as a .cm file with given filename. Overwrites if filename is taken")
		print("    open {FILENAME} -> opens a .cm file. Does not save current work.")
		print("    exp {FILENAME} {NEWFILEPATH} -> takes a cm file from local application folder and sends it out into the big world of your computer")
		print("Other:")

		print("    exit -> exits the program. does not save")
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
				try:
					file = open(st.resource_path(x[5:] + ".cm"),"w")
					st.lock.acquire()
					file.write(json.dumps(st.symbolcontainer))
					st.lock.release()
					file.close()
					ok("file saved as '" + x[5:] + "'")
				except:
					fail("There was an error saving your file.")
			elif(x[:4]=="open"):
				if x[-3:] == ".cm":
					x = x[:-3]
				try:
					file = open(st.resource_path(x[5:] + ".cm"),"r")
					st.lock.acquire()
					st.symbolcontainer = json.loads(file.readline())
					st.lock.release()
					ok("file opened successfully")
				except FileNotFoundError:
					fail("File could not be found.")
				except:
					fail("There was an error opening your file.")
			elif(x[:3]=="exp"):
				tokens = x.split()
				if not tokens[1][-3:] == ".cm":
					tokens[1]+= ".cm"
				if not tokens[2][-3:] == ".cm":
					tokens[2]+= ".cm"
				try:
					copyfile(st.resource_path(tokens[1]),tokens[2])
					ok("file exported successfully")
				except:
					fail("There was an error exporting your file.")


			elif(x=="list"):
				print("Saved CM files:")
				files = os.listdir(st.resource_path(""))
				for file in files:
					if file[-3:] == ".cm":
						print ("    " + file)

			elif(x=="exit"):
				st.programIsRunning = False
			else:
				fail("Sorry, your command wasn't recognized.")
