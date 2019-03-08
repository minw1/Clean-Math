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
	spacing = 10
	
	def __init__(self, tex, pos):
		st.lock.acquire()
		self.tex = tex
		self.hitboxes=[]
		if tex in list(string.ascii_letters) or floatcastable(tex):
			self.surface,rect = st.iFONT.render(tex,st.fontColor)
			print(self.surface)
			self.hitboxes.append((self.surface.get_rect(),pos))
		elif tex[0] =="\\":
			pass
		elif tex[0] == "(":
			pass
		elif tex[0] == ")":
			pass
		else:
			for i in range(0,len(tex)):
				if tex[i] in self.operators:
					firstSurface = smartSurface(tex[0:i],[0,i])
					firstWidth, firstHeight = firstSurface.get_size()
					secondSurface = smartSurface(tex[i+1:],[i+1,len(tex)])
					secondWidth, secondHeight = secondSurface.get_size()
					operatorSurface, operatorRect = st.FONT.render(tex[i],st.fontColor)
					operatorWidth, operatorHeight = operatorSurface.get_size()
					finalWidth = firstWidth+operatorWidth+secondWidth+2*self.spacing
					finalHeight = max(firstHeight,secondHeight,operatorHeight)
					self.surface = pygame.Surface((finalWidth, finalHeight))
					self.surface.blit(firstSurface.surface, (0,(finalHeight-firstHeight)//2))
					self.surface.blit(secondSurface.surface, (finalWidth-secondWidth,(finalHeight-secondHeight)//2))
					self.surface.blit(operatorSurface, (firstWidth+self.spacing,(finalHeight-operatorHeight)//2))

					for (hitbox,value) in firstSurface.hitboxes:
						self.hitboxes.append((hitbox.move(0,(finalHeight-firstHeight)//2),value))
					for (hitbox,value) in secondSurface.hitboxes:
						self.hitboxes.append((hitbox.move(finalWidth-secondWidth,(finalHeight-secondHeight)//2),value))

					self.hitboxes.append((operatorSurface.get_rect().move(firstWidth+self.spacing,(finalHeight-operatorHeight)//2),value))



					break
		st.lock.release()

					

	def get_size(self):
		return self.surface.get_size()

	def __hash__(self):
		return hash(self.tex)

pygame.init()
screen = pygame.display.set_mode([800,600], pygame.RESIZABLE)

expression = smartSurface("3+2-2",[0,5])
screen.blit(expression.surface,(0,0))
pygame.display.update()
