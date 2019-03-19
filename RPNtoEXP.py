import expression as exp

operators = {'*','/','^','+','-'}

def RPNtoEXP(rpn):
	if not rpn[len(rpn)-1] in operators:
		return len(rpn)-1,exp.Expression("none",[rpn[len(rpn)-1]])

	if rpn[len(rpn)-1] in operators: 
		pos,first = RPNtoEXP(rpn[:len(rpn)-1])
		pos2,second = RPNtoEXP(rpn[:pos])
		return pos2-1,exp.Expression(rpn[len(rpn)-1],[first,second])
