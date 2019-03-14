import expression as xp
import settings as st

LATEX_FONT_PATH = st.font_locator("cmu.ttf")
LATEX_iFONT_PATH = st.font_locator("cmu_i.ttf")
LATEX_bFONT_PATH = st.font_locator("cmu_b.ttf")
LATEX_biFONT_PATH = st.font_locator("cmu_bi.ttf")



def makeSmaller(font_size, n):
    return round(font_size/SQRT2**n)

DEFAULT_FONT_SIZE = 48

class smartSurface:

    simpleOps = {'+','-'} #'*' will appear as a cdot
    spacing = 10

    def __init__(self, exp, frac_depth, script_depth): #depth is number of layers into generation we are. 
    	self.surface = None
    	self.hitboxes = [] #(rect, self.exp)
    	self.font_size = makeSmaller(DEFAULT_FONT_SIZE, script_depth+max(frac_depth-1,0))
    	self.font = pygame.freetype.Font(LATEX_FONT_PATH, font_size)
    	self.iFont = pygame.freetype.Font(LATEX_iFONT_PATH, font_size)

    	if exp.op.strRep == "()":
    	elif exp.op.strRep in simpleOps:
            firstSurface = smartSurface(exp.expList[0])
            secondSurface = smartSurface(exp.expList[1])
            secondWidth, secondHeight = secondSurface.get_size()
            operatorSurface, operatorRect = font.render(tex[i],st.fontColor)
            operatorWidth, operatorHeight = operatorSurface.get_size()
            finalWidth = firstWidth+operatorWidth+secondWidth+2*self.spacing
            finalHeight = max(firstHeight,secondHeight,operatorHeight)
            self.surface = pygame.Surface((finalWidth, finalHeight))
            self.surface.blit(firstSurface.surface, (0,(finalHeight-firstHeight)//2))
            self.surface.blit(secondSurface.surface, (finalWidth-secondWidth,(finalHeight-secondHeight)//2))
            self.surface.blit(operatorSurface, (firstWidth+self.spacing,(finalHeight-operatorHeight)//2))
            self.hitboxes = firstSurface.translateHitboxes([0,(finalHeight-firstHeight)//2]) + secondSurface.translateHitboxes([finalWidth-secondWidth,(finalHeight-secondHeight)//2])
    	elif exp.op.strRep == "^":
    	elif exp.op.strRep == "frac":
    	elif exp.op.strRep == "*":

    def translateHitboxes(self,coordinates):
        newHitboxes = []
        for hb in self.hitboxes:
            rect, expression = hb
            newHitboxes.append((rect.move(coordinates[0],coordinates[1]), expression))
        return newHitboxes



