import expression as xp
import operation as op
import expToSurface
import pygame

ADD_OP = op.Operator(0,0,0,'+')
SUB_OP = op.Operator(0,0,0,'-')
MUL_OP = op.Operator(0,0,0,'*')
DIV_OP = op.Operator(0,0,0,'frac')
POW_OP = op.Operator(0,0,0,'^')
PAR_OP = op.Operator(0,0,0,'()')
BRK_OP = op.Operator(0,0,0,'{}')

tokens = (
    'NAME','NUMBER',
    'PLUS','MINUS','TIMES','DIVIDE','POWER','EQUALS',
    'LPAREN','RPAREN','LBRACK','RBRACK'
    )

# Tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_POWER   = r'\^'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACK  = r'\{'
t_RBRACK  = r'\}'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
        t.value = xp.NoOpExpression(str(t.value))
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = xp.NoOpExpression('0')
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','POWER'),
    ('right','UMINUS'),
    )

# dictionary of names
names = { }

def p_statement_assign(t):
    'statement : NAME EQUALS expression'
    names[t[1]] = t[3]

resultingExpression = None

def p_statement_expr(t):
    'statement : expression'
    global resultingExpression
    resultingExpression = t

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression POWER expression'''
    if t[2] == '+'  : t[0] = xp.Expression(ADD_OP, [t[1],t[3]])
    elif t[2] == '-': t[0] = xp.Expression(SUB_OP, [t[1],t[3]])
    elif t[2] == '*': t[0] = xp.Expression(MUL_OP, [t[1],t[3]])
    elif t[2] == '/': t[0] = xp.Expression(DIV_OP, [t[1],t[3]])
    elif t[2] == '^': t[0] = xp.Expression(POW_OP, [t[1],t[3]])

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = expression('u-',[t[2]])

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = xp.Expression(PAR_OP,[t[2]])

def p_expression_brack(t):
    'expression : LBRACK expression RBRACK'
    t[0] = xp.Expression(BRK_OP,[t[2]])

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    try:
        t[0] = names[t[1]]
    except LookupError:
        print("Undefined name '%s'" % t[1])
        t[0] = 0

def p_error(t):
    print("Syntax error at '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()
counter=0
def get_exp():
    inputStr = input('parse > ')
    parser.parse(inputStr)
    string = resultingExpression[1]
    Surface = expToSurface.smartSurface(string)
    pygame.image.save(Surface.surface,'TestImages/test'+str(counter)+'.png')

while True:
    get_exp()
    counter+=1
