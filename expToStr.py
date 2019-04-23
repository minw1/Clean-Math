import expression as xp
import settings as st

precedents = {
		"+":0,
		"-":0,
		"*":1,
		"/":1,
		"^":2
	}

def pre(op):
	if op in precedents:
		return precedents[op]
	return 3 #Parens and numbers
def wrap(str,foReallyThough):
	if foReallyThough:
		return "(" + str + ")"
	else:
		return str

def expToStr(exp):
	if exp.op in precedents:
		firstLower = pre(exp.expList[0].op)<pre(exp.op)#is first op lower precedence than the exp op?
		secondLower = pre(exp.expList[1].op)<pre(exp.op)
		return wrap(expToStr(exp.expList[0]),firstLower) + exp.op + wrap(expToStr(exp.expList),secondLower)
	return exp.strRep