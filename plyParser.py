##adapted from ply example calc.py

import expression as xp
import operation as op
import re
import expToSurface
import pygame

def mkstr_plus(opList):
	opStr = ""
	if len(opList) != 2:
		opStr = "ERROR"
	else:
		opStr = opList[0].getString() + "+" + opList[1].getString()
	return opStr

def mkstr_minus(opList):
	opStr = ""
	if len(opList) != 2:
		opStr = "ERROR"
	else:
		opStr = opList[0].getString() + "-" + opList[1].getString()
	return opStr
	
def mkstr_astrtimes(opList):
	opStr = ""
	if len(opList) != 2:
		opStr = "ERROR"
	else:
		opStr = opList[0].getString() + "*" + opList[1].getString()
	return opStr

def mkstr_slashdiv(opList):
	opStr = ""
	if len(opList) != 2:
		opStr = "ERROR"
	else:
		opStr = opList[0].getString() + "/" + opList[1].getString()
	return opStr
	
def mkstr_caretpow(opList):
	opStr = ""
	if len(opList) != 2:
		opStr = "ERROR"
	else:
		opStr = opList[0].getString() + "^" + opList[1].getString()
	return opStr

def mkstr_error(opList):
	return "ERROR"
	
ADD_OP = op.Operator('+', mkstr_plus)
SUB_OP = op.Operator('-', mkstr_minus)
MUL_OP = op.Operator('*', mkstr_astrtimes)
DIV_OP = op.Operator('/', mkstr_slashdiv)
POW_OP = op.Operator('^', mkstr_caretpow)

ERR_OP = op.Operator("ERROR", mkstr_error)

tokens = (
    'NAME', 'VAR', 'NUMBER',
    '1L1R_OP_L0', '1L1R_OP_L1', '1L1R_OP_R2', 'EQUALS',
    'LPAREN','RPAREN','LBRACK','RBRACK', 'NUM_CURSOR', 'VAR_CURSOR', 'UNF_CURSOR', 'PRN_CURSOR'
    )

# Tokens
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACK  = r'\{'
t_RBRACK  = r'\}'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_UNF_CURSOR  = r'((?<=[^a-zA-Z\d])|(?<=^))\|(?=[^a-zA-Z\d\(]|$)'
t_PRN_CURSOR = r'\|(?=\()|(?<=\))\|'

def t_1L1R_OP_L0(t):
	r'\+|-'
	if t.value == "+":
		t.value = ADD_OP
	elif t.value == '-':
		t.value = SUB_OP
	else:
		t.value = ERR_OP
	return t

def t_1L1R_OP_L1(t):
	r'\*|/'
	if t.value == '*' or t.value == '':
		t.value = MUL_OP
	elif t.value == '/':
		t.value = DIV_OP
	else:
		t.value = ERR_OP
	return t	

def t_1L1R_OP_R2(t):
	r'\^'
	if t.value == '^':
		t.value = POW_OP
	else:
		t.value = ERR_OP
	return t
	
def t_NUM_CURSOR(t):
	r'(\d+\|\d*)|(\d*\|\d+)'
	numString = t.value
	cursor_idx = numString.index('|')
	numString = numString.replace('|', '')
	t.value = xp.NoOpExpression(numString, True, cursor_idx)
	return t
	
def t_VAR_CURSOR(t):
	r'([a-zA-Z]\|)|(\|[a-zA-Z])'
	varString = t.value
	cursor_idx = varString.index('|')
	varString = varString.replace('|', '')
	t.value = xp.NoOpExpression(varString, True, cursor_idx)
	return t
	
def t_VAR(t):
	r'[a-zA-Z]'
	t.value = xp.NoOpExpression(t.value)
	return t
	
def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
        t.value = xp.NoOpExpression(str(t.value))
    except ValueError:
        global error
        error=True
        print("Number value too large %d", t.value)
        t.value = xp.NoOpExpression('0')
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    global error
    error=True
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

# dictionary of names
names = { }

def p_statement_assign(p):
    'statement : NAME EQUALS exp0'
    names[p[1]] = p[3]

def p_statement_exp0(p):
    'statement : exp0'
    p[0] = p[1]

def p_exp0_exp1(p):
	'exp0 : exp1'
	p[0] = p[1]

def p_exp1_exp2(p):
	'exp1 : exp2'
	p[0] = p[1]	

def p_exp2_exp3(p):
	'exp2 : exp3'
	p[0] = p[1]	

def p_exp3_parens(p):
    'exp3 : LPAREN exp0 RPAREN'
    p[0] = p[2]

def p_exp3_clparens(p):
    'exp3 : PRN_CURSOR LPAREN exp0 RPAREN'
    p[3].addCursor(0)
    p[0] = p[3]

def p_exp3_crparens(p):
    'exp3 : LPAREN exp0 RPAREN PRN_CURSOR'
    p[2].addCursor(-1)
    p[0] = p[2]


def p_exp3_number(p):
    'exp3 : NUMBER'
    p[0] = p[1]

def p_exp3_cnumber(p):
    'exp3 : NUM_CURSOR'
    p[0] = p[1]

def p_exp3_cvar(p):
    'exp3 : VAR_CURSOR'
    p[0] = p[1]

def p_exp3_var(p):
    'exp3 : VAR'
    p[0] = p[1]

def p_exp3_empty(p):
    'exp3 : empty'
    p[0] = xp.NoOpExpression(" ")

def p_exp3_cempty(p):
	'exp3 : UNF_CURSOR empty'
	p[0] = xp.NoOpExpression(" ", True, 0)

def p_empty(p):
     'empty :'
     pass

def p_exp0_exp0ops(p):
    'exp0 : exp0 1L1R_OP_L0 exp1'
    expList = [p[1], p[3]]
    p[0] = xp.Expression(p[2], expList)

def p_exp1_exp1ops(p):
    'exp1 : exp1 1L1R_OP_L1 exp2'
    expList = [p[1], p[3]]
    p[0] = xp.Expression(p[2], expList)

def p_exp1_exp2ops(p):
    'exp2 : exp3 1L1R_OP_R2 exp2'
    expList = [p[1], p[3]]
    p[0] = xp.Expression(p[2], expList)

#Not sure what this does
def p_expression_name(t):
    'exp0 : NAME'
    try:
        t[0] = names[t[1]]
    except LookupError:
        global error
        error=True
        print("Undefined name '%s'" % t[1])
        t[0] = 0

def p_error(t):
    global error
    error=True
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()

def process_string(inputStr):
    outputStr = inputStr
    outputStr = re.sub('(?<=\w|\))(?=\|?\()|(?<=\))(?=\|?\w)|(?<=\d|[a-zA-Z])(?=\|?[a-zA-Z])|(?<=[a-zA-Z])(?=\|?\d)', '*', outputStr)
    return outputStr

error=False
def get_exp(inputStr):
    global error
    error=False
    inputStr = process_string(inputStr)
    resultingExpression = parser.parse(inputStr)
    if error:
        raise ValueError("Expression could not parse correctly.")
    else:
        return resultingExpression
        #string = resultingExpression.getString()
        #Surface = expToSurface.smartSurface(string)
        #return Surface.surface
