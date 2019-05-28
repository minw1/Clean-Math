import pygame
import pygame.freetype
import settings as st
import math
import numpy as np
import json
import string
import panel as pnl
import os
import random
import gridOps as go
import time
import copy
from settings import selectedcell
import expression as xp
import expToSurface as xts
import plyParser as pprs
import expToStr as xtstr
import re
import processString as proc
import ui


def saveCM(filename, uim, uiq):
	xdata = {'typing_first_expression':uim.typing_first_expression, 'uiEx1': uim.uiEx1.text}
	qdata = []
	for q in uiq.alluiEquations:
		qdict = {'leftside':q.leftside.text, 'rightside':q.rightside.text,'eqmid': q.eqmid}
		qdata += [qdict]

	fdata = {'xdata':xdata,'qdata':qdata}

	try:
		file = open(filename + '.cm',"w")
		file.write(json.dumps(fdata))
		file.close()
		print("file saved")
	except Exception as inst:
		print(inst)

def openCM(filename,uim,uiq):
	try:

		print(id(uim))


		file = open(filename + '.cm',"r")
		fdata = json.loads(file.readline())

		print(fdata)
		#reading and setting xdata
		uim.typing_first_expression = fdata['xdata']['typing_first_expression']
		uim.uiEx1.text = fdata['xdata']['uiEx1']



		#reatding and setting qdata
		newAllUiEquations = []
		uiq.alluiEquations =[]

		for q in fdata['qdata']:
			leftside = ui.uiExpression((0,0))
			rightside = ui.uiExpression((0,0))

			leftside.text = q['leftside']
			rightside.text = q['rightside']
			neq = ui.uiEquation(leftside,rightside,q['eqmid'])
			newallUiEquations += [neq]

		uiq.alluiEquations = newAllUiEquations

	except Exception as inst:
		print(inst)