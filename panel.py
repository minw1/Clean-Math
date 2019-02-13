import threading
import cmdColors as cc

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

class PanelThread (threading.Thread):
	def __init__(self,name):
		threading.Thread.__init__(self)
		self.name = name
	def run(self):
		while st.programIsRunning:
			print("Command List:")
			print("    tg -> toggles gridlines")
			print("    bw {integer} -> changes box width to given integer")
			print("    fc {COLOR} -> changes font color to a given color")
			print(cc.WARNING + "By the way, guys, there's this quirk where the actual grid panel will not close until you type one more thing into the command line. I'm working on it" + cc.ENDC)


			x = input();
			if(x=="tg"):
				toggleGrid()

			elif(x[:2]=="bw"):
				try:
					if int(x[3:]) >= 20:
						setBoxWidth(int(x[3:]))
					else:
						print(cc.WARNING + "Sorry, box length must be at least 20" + cc.ENDC)

				except ValueError:
					print(cc.FAIL + "Sorry, the integer you entered was not valid. Enter 'bw' followed by a space and then an integer" + cc.ENDC)
			elif(x[:2] =="fc"):
				if x[3:].upper()=="RED":
					setFontColor(st.RED)
				elif x[3:].upper()=="BLUE":
					setFontColor(st.BLUE)
				elif x[3:].upper()=="GREEN":
					setFontColor(st.GREEN)
				elif x[3:].upper()=="BLACK":
					setFontColor(st.BLACK)
				else:
					print(cc.WARNING + "Sorry, we don't have that color." + cc.ENDC)

			else:
				print(cc.FAIL + "Sorry, your command wasn't recognized." + cc.ENDC)



