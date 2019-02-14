import threading
import cmdColors as cc
import json
import settings as st



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
		print("    save {FILENAME} -> saves work as a .cm file with given filename. Overwrites if filename is taken")
		print("    open {FILENAME} -> opens a .cm file. Does not save current work.")
		print("Other:")

		print("    exit -> exits the program. does not save")
		while st.programIsRunning:
			


			x = input();
			if(x=="tg"):
				toggleGrid()
				print(cc.OKBLUE + "gridlines toggled" + cc.ENDC)

			elif(x[:2]=="bw"):
				try:
					if int(x[3:]) >= 20:
						setBoxWidth(int(x[3:]))
						print(cc.OKBLUE + "box width changed" + cc.ENDC)
					else:
						print(cc.WARNING + "Sorry, box length must be at least 20" + cc.ENDC)

				except ValueError:
					print(cc.FAIL + "Sorry, the integer you entered was not valid. Enter 'bw' followed by a space and then an integer" + cc.ENDC)
			elif(x[:2] =="fc"):
				if x[3:].upper() in st.colorMap:
					setFontColor(st.colorMap[x[3:].upper()])
					print(cc.OKBLUE + "font color changed" + cc.ENDC)
				else:
					print(cc.WARNING + "Sorry, we don't have that color." + cc.ENDC)
			elif(x[:2] =="bc"):
				if x[3:].upper() in st.colorMap:
					setBackgroundColor(st.colorMap[x[3:].upper()])
					print(cc.OKBLUE + "background color changed" + cc.ENDC)
				else:
					print(cc.WARNING + "Sorry, we don't have that color." + cc.ENDC)
			elif(x[:2] =="gc"):
				if x[3:].upper() in st.colorMap:
					setGridColor(st.colorMap[x[3:].upper()])
					print(cc.OKBLUE + "grid color changed" + cc.ENDC)
					if(not st.show_grid):
						print("gridlines must be toggled on to see the grid")
				else:
					print(cc.WARNING + "Sorry, we don't have that color." + cc.ENDC)

			elif(x[:4] == "save"):
				try:
					file = open(x[5:] + ".cm","w")
					st.lock.acquire()
					file.write(json.dumps(st.symbolcontainer))
					st.lock.release()
					file.close()
					print(cc.OKBLUE + "file saved as '" + x[5:] + "'" + cc.ENDC)
				except:
					print(cc.FAIL +"There was an error saving your file." + cc.ENDC)
			elif(x[:4]=="open"):
				if x[-3:] == ".cm":
					x = x[:-3]
				try:
					file = open(x[5:] + ".cm","r")
					st.lock.acquire()
					st.symbolcontainer = json.loads(file.readline())
					st.lock.release()
					print(cc.OKBLUE + "file opened successfully" + cc.ENDC)
				except FileNotFoundError:
					print(cc.FAIL +"File could not be found."+ cc.ENDC)
				except:
					print(cc.FAIL +"There was an error opening your file."+ cc.ENDC)

			elif(x=="exit"):
				st.programIsRunning = False
			else:
				print(cc.FAIL + "Sorry, your command wasn't recognized." + cc.ENDC)



