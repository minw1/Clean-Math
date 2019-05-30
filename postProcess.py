import settings as st
import math
import string
import os
import random
import time
import copy
from settings import selectedcell
import expression as xp
import expToSurface as xts
import plyParser as pprs
import expToStr as xtstr
import re
import processString as proc
import saver
import wolframalpha

def move_cursors_from_brackets(exp):
    if type(exp) == NoOpExpression:
        return exp, (False, None)
    newList = []
    for child in exp.expList:
        newChild, (addCursor, index) = move_cursors_from_brackets(child)
        if addCursor:
            exp.cursor = True
            exp.cursor_idx = index
        newList.append(newChild)
        

def post_process(exp):
    return move_cursors_from_brackets(exp)
