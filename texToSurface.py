import pygame
import pygame.freetype
import string
import settings as st

def floatcastable(str):
	try:
		float(str)
		return True
	except:
		return False



class smartSurface:
	operators = {'+','-'}
	
	def __init__(self, tex):
		self.tex = tex
		if tex in list(string.ascii_letters) or floatcastable(tex):
			st.lock.acquire()
			self.surface = st.iFONT.render(tex,st.fontColor)
			self.hitboxes = {self:self.surface.get_rect()}
		elif tex[0] =="\\":
			pass
		elif tex[0] == "(":
			pass
		elif tex[0] == ")":
			pass
		else:
			for i in range(0,len(tex)):
				if tex[i] in operators:
					firstSurface = smartSurface(tex[0:i])
					secondSurface = smartSurface(tex[i+1:])
					



	def __hash__(self):
		return hash(self.tex)
