import expression as xp
import settings as st

precedents = {
		"+":0,
		"-":0,
		"*":1,
		"/":1,
		'\u00B7':1,
		"^":2
	}

def pre(op):
	if op in precedents:
		return precedents[op]
	return 3 #Parens and numbers
def wrap(stri,foReallyThough):
	if foReallyThough:
		return "(" + stri + ")"
	else:
		return stri


def clearCursor(exp):
	exp.cursor = False
	if type(exp) == xp.Expression:
		for child in exp.expList:
			clearCursor(child)

def expToStr(exp):
	if(type(exp)==xp.NoOpExpression):
		if(exp.strRep == " "):
			if exp.cursor:
				return "|"
			return ""

		sr = exp.strRep
		if exp.cursor:
			return sr[:exp.cursor_idx] + "|" + sr[exp.cursor_idx:]
		else:
			return sr
	if(exp.op == "()"):
		return wrap(expToStr(exp.expList[0]), True)

	if(exp.op == "("):
		return "(" + expToStr(exp.expList[0])

	if(exp.op == ")"):
		return expToStr(exp.expList[0]) + ")"

	elif exp.op in precedents:
		firstLower = pre(exp.expList[0].op)<pre(exp.op)#is first op lower precedence than the exp op?
		secondLower = pre(exp.expList[1].op)<pre(exp.op)

		if exp.op.strRep == "*":
			return wrap(expToStr(exp.expList[0]),firstLower) + wrap(expToStr(exp.expList[1]),secondLower)
		if exp.op.strRep == '\u00B7':
			return wrap(expToStr(exp.expList[0]),firstLower) + '*' + wrap(expToStr(exp.expList[1]),secondLower)
		return wrap(expToStr(exp.expList[0]),firstLower) + exp.op.strRep + wrap(expToStr(exp.expList[1]),secondLower)
