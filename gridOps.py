import settings as st
import json
def getString(location):
	toReturn = ""
	st.lock.acquire()
	curLoc = location
	bottom = json.loads(curLoc)['y']

	while True:
		loc = json.loads(curLoc)
		if curLoc in st.symbolcontainer:
			toReturn += st.symbolcontainer[curLoc]
			loc['x'] += 1
			curLoc = json.dumps(loc)
		else:
			loc['y'] -= 1
			if json.dumps(loc) in st.symbolcontainer:
				toReturn += "^{"
				curLoc = json.dumps(loc)
			else:
				#okay, there's nothing above us, is there anything below us?
				loc['y']+=1
				found = False
				ypos = loc['y']

				while loc['y']<= bottom and not found:
					
					if json.dumps(loc) in st.symbolcontainer:
						toReturn += "}" * (loc['y']-ypos)
						curLoc = json.dumps(loc)
						found = True

					loc['y'] += 1

				if not found:
					if toReturn.count("{") > toReturn.count("}"):
						toReturn += "}" * (toReturn.count("{") - toReturn.count("}"))
					st.lock.release()
					return toReturn
	

def printExpression(string,location):
	curLoc = location
	st.lock.acquire()
	for i in range(0, len(string)):
		loc = json.loads(curLoc)
		if string[i] == "^": #okay i'll fix this running off the screen at some point
			loc['y'] -= 1
		elif string[i] == "}":
			loc['y'] += 1
		elif (not string[i]=="{"):
			st.symbolcontainer[curLoc] = string[i]
			loc['x']+=1
		curLoc = json.dumps(loc)
	st.lock.release()

