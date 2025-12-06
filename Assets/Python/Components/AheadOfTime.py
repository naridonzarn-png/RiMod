## Sid Meier's Civilization 4
## Copyright Firaxis Games 2005
from CvPythonExtensions import *
import CvUtil
import PyHelpers	

# globals
gc = CyGlobalContext()

Eras = {
0:	[-10000,	100,200,300,400,500,500],
1:	[-2000,		50,100,200,300,400,400],	## 2000 BC as a start date for that era, and then a list of all the tech cost modifiers
2:	[-1200,		0,100,200,300,400,400],	
3:	[0,			0,50,100,200,300,400],		
4:	[400,		0,0,100,200,300,300],
5:	[1100,		0,0,50,100,200,300],	
6:	[1400,		0,0,0,100,200,200],	
7:	[1600,		0,0,0,50,100,200],	
8:	[1750,		0,0,0,0,100,100],		
9:	[1910,		0,0,0,0,50,100],	
10:	[1945,		0,0,0,0,0,0]
}

EraTexts = ["","TXT_BRON_ERA_AHEAD","TXT_CLAS_ERA_AHEAD","TXT_IMP_ERA_AHEAD","TXT_MED_ERA_AHEAD","TXT_CRUS_ERA_AHEAD","TXT_REN_ERA_AHEAD","TXT_NAT_ERA_AHEAD","TXT_IND_ERA_AHEAD","TXT_WW_ERA_AHEAD","TXT_MOD_ERA_AHEAD"]

class AheadOfTime:
		
	def checkAhead(self):
		iYear = gc.getGame().getGameTurnYear()
		iEra = CyGame().getAheadOfTimeEra()
		iChangeEra = iEra
		for iEraX in Eras:
			if iYear >= Eras[iEraX][0] and iEra < iEraX:
				iChangeEra = iEraX	
		if iChangeEra != iEra:
			CyGame().setAheadOfTimeEra(iChangeEra)
			self.changeTechAhead(iChangeEra)
			print ("Set era to %d"%(CyGame().getAheadOfTimeEra()))
			print ("Triggered on year %d"%(iYear))			

	def setAhead(self):
		iYear = gc.getGame().getGameTurnYear()
		iEra = CyGame().getAheadOfTimeEra()
		iChangeEra = iEra
		for iEraX in Eras:
			if iYear >= Eras[iEraX][0] and iEra < iEraX:
				iChangeEra = iEraX	
		CyGame().setAheadOfTimeEra(iChangeEra)
		self.changeTechAhead(iChangeEra)
		print ("Set era to %d"%(CyGame().getAheadOfTimeEra()))
		print ("Triggered on year %d"%(iYear))

	def changeTechAhead(self, iChangeEra):
		for iTech in xrange(gc.getNumTechInfos()):
			TechInfo = gc.getTechInfo(iTech)
			iTechEra = TechInfo.getEra()
			if iTechEra > 0:
				TechInfo.setAheadOfTime(Eras[iChangeEra][iTechEra])