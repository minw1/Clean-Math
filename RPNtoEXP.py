import expression as exp


precedence = {'+':0,'-':0,"*":1,"/":1,"^":2,
		"none":100#obviously, we should evaluate numbers to be themselves before anything else. This is really just a technicality.
}

def RPNtoEXP(rpn):
	if not rpn[len(rpn)-1] in precedence:
		return len(rpn)-1,exp.Expression("none",[rpn[len(rpn)-1]])

	if rpn[len(rpn)-1] in precedence: 
		pos,first = RPNtoEXP(rpn[:len(rpn)-1])
		pos2,second = RPNtoEXP(rpn[:pos])

		if(precedence[first.op] < precedence[rpn[len(rpn)-1]]):
			first = exp.Expression("()",[first])
		if(precedence[second.op] < precedence[rpn[len(rpn)-1]]):
			second = exp.Expression("()",[second])

		return pos2,exp.Expression(rpn[len(rpn)-1],[second,first])
