import expression as xp
import settings as st

LATEX_FONT_PATH = st.font_locator("cmu.ttf")
LATEX_iFONT_PATH = st.font_locator("cmu_i.ttf")
LATEX_bFONT_PATH = st.font_locator("cmu_b.ttf")
LATEX_biFONT_PATH = st.font_locator("cmu_bi.ttf")



def makeSmaller(font_size):
    return round(font_size/SQRT2)

class smartSurface:

    simpleOps = {'+','-'} #'*' will appear as a cdot
    spacing = 10

    def __init__(self, exp, frac_depth, exp_depth): #depth is number of layers into generation we are. 
    	self.surface = None
    	font = pygame.freetype.Font(LATEX_FONT_PATH, font_size)
    	iFont = pygame.freetype.Font(LATEX_iFONT_PATH, font_size)

    	if exp.op.strRep == "()":
    	if exp.op.strRep in simpleOps:
    	if exp.op.strRep == "^":
    	if exp.op.strRep == "frac":
    	if exp.op.strRep == "*":


