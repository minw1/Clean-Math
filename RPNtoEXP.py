import expression as exp

binOperators = {'*','/','^','+','-'}

def RPNtoEXP(rpn):
	if not rpn[len(rpn)-1] in binOperators:
		return len(rpn)-1,exp.Expression("none",[rpn[len(rpn)-1]])

	if rpn[len(rpn)-1] in binOperators: 
		pos,first = RPNtoEXP(rpn[:len(rpn)-1])
		pos2,second = RPNtoEXP(rpn[:pos])
		return pos2,exp.Expression(rpn[len(rpn)-1],[second,first])
