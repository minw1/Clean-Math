import expression as xp
import copy

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

def replace_child(parent,badkid,betterkid):
	parent.expList.remove(badkid)#put your own kid up for adoption
	parent.expList.append(betterkid)#and get yourself a new one

def all_under_a_zero_prec_op(exp):
	if type(exp) = xp.NoOpExpression:
		return [exp]
	elif precedents[exp.op] > 0:
		return [exp]
	elif precedents[exp.op] == 0:
		return all_under_a_zero_prec_op(exp.expList[0]) + all_under_a_zero_prec_op(exp.expList[1])
	print("not exactly sure how you got here")

def distribute(exp,rToL = True):
	if(exp.op == "*"):
		if rToL:
			to_insert = exp.expList[1]
			to_insert_to = exp.expList[0]
		else:
			to_insert = exp.expList[0]
			to_insert_to = exp.expList[1]

		all_insertion_sites = all_under_a_zero_prec_op(to_insert_to)
		for site in all_insertion_sites:
			multiplied_node = xp.Expression("*",[site,to_insert])
			replace_child(site.parent,site,multiplied_node)
	exp = to_insert_to
	exp.assign_parents()

