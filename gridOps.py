import settings as st
def getString(location):

	toReturn = ""
	st.lock.acquire()
	curLoc = location

	while True:
		loc = json.loads(curLoc)
		if curLoc in st.symbolcontainer:
			toReturn += st.symbolcontainer[curLoc]
			loc['x'] += 1
		else:


