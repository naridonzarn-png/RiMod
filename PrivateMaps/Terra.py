#
#	FILE:	 Terra.py
#	AUTHOR:  Bob Thomas (Sirian)
#	PURPOSE: Global map script - Simulates Terran (Earth-like) worlds
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import MultilayeredFractal
from CvMapGeneratorUtil import TerrainGenerator
from CvMapGeneratorUtil import FeatureGenerator

import MapScriptTools as mst
balancer = mst.bonusBalancer

# The following global constants are not neccessary,
# but they are widely used and make reading the code easier.
# (Yes I know thet local variables are faster, but that's only appreciable
#  within deeply nested loops, and the script runs only once per game anyway.)
# ----------------------------------------------------------------------------
gc = CyGlobalContext()
map = CyMap()


'''
MULTILAYERED FRACTAL NOTES

The MultilayeredFractal class was created for use with this script.

I worked to make it adaptable to other scripts, though, and eventually it
migrated in to the MapUtil file along with the other primary map classes.

- Bob Thomas   July 13, 2005


TERRA NOTES

Terra turns out to be our largest size map. This is the only map script
in the original release of Civ4 where the grids are this large!

This script is also the one that got me started in to map scripting. I had 
this idea early in the development cycle and just kept pestering until Soren 
turned me loose on it, finally. Once I got going, I just kept on going!

- Bob Thomas   September 20, 2005
'''

def getVersion():
	return "1.20a"

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_TERRA_DESCR"

def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def getNumCustomMapOptions():
	return 2

def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_WORLD_WRAP",
		1:  "TXT_KEY_CONCEPT_RESOURCES"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text

def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	2
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			},
		1:	{
			0: "TXT_KEY_WORLD_STANDARD",
			1: "TXT_KEY_MAP_BALANCED"
			}
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	[iOption] = argsList
	option_defaults = {
		0:	1,
		1:  0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	false,
		1:  false
		}
	return option_random[iOption]

def beforeGeneration():
	print "-- beforeGeneration()"

	# Create mapInfo string - this should work for all maps
	mapInfo = ""
	for opt in range( getNumCustomMapOptions() ):
		nam = getCustomMapOptionName( [opt] )
		sel = map.getCustomMapOption( opt )
		txt = getCustomMapOptionDescAt( [opt,sel] )
		mapInfo += "%27s:   %s\n" % ( nam, txt )

	# Create function for mst.evalLatitude - here Ringworld3
	#if mapOptions.Polar == 0:
	#	compGetLat = "int(round([0.95,0.80,0.64,0.60,0.52,0.40,0.24,0.04,0.04,0.24,0.40,0.52,0.60,0.64,0.80,0.95][y]*80))"
	#elif mapOptions.Polar == 1:
	#	compGetLat = "int(round([0.98,0.86,0.75,0.65,0.56,0.48,0.41,0.34,0.27,0.21,0.16,0.12,0.09,0.06,0.03,0.00][y]*80))"
	#elif mapOptions.Polar == 2:
	#	compGetLat = "int(round([0.00,0.03,0.06,0.09,0.12,0.16,0.21,0.27,0.34,0.41,0.48,0.56,0.65,0.75,0.86,0.98][y]*80))"
	#elif mapOptions.Polar == 3:
	#	compGetLat = "int(round([0.70,0.57,0.47,0.37,0.28,0.20,0.13,0.08,0.03,0.00,0.03,0.08,0.13,0.20,0.28,0.37][y]*90))"

	# Initialize MapScriptTools
	mst.getModInfo( getVersion(), None, mapInfo, bNoSigns=False )

	# Initialize MapScriptTools.BonusBalancer
	# - balance boni, place missing boni, move minerals, longer balancing range
	balancer.initialize( True, True, True, True )

	# Initialize MapScriptTools.MapRegions, don't use landmarks for FFH or Planetfall
	#mst.mapRegions.initialize( noSigns = (mst.bFFH or bPfall) )

def getWrapX():
	map = CyMap()
	return (map.getCustomMapOption(0) == 1 or map.getCustomMapOption(0) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(0) == 2)

def normalizeAddExtras():
	balancer.normalizeAddExtras()
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()

	if (CyMap().getCustomMapOption(1) == 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def getGridSize(argsList):
	"Enlarge the grids! According to Soren, Earth-type maps are usually huge anyway."
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:      (10,6),
        WorldSizeTypes.WORLDSIZE_TINY:      (15,9),
        WorldSizeTypes.WORLDSIZE_SMALL:     (25,15),
        WorldSizeTypes.WORLDSIZE_STANDARD:  (30,18),
        WorldSizeTypes.WORLDSIZE_LARGE:     (40,24),
        WorldSizeTypes.WORLDSIZE_HUGE:      (44,26),
		WorldSizeTypes.WORLDSIZE_GIANT:		(52,30)
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def minStartingDistanceModifier():
	return -20

def findStartingPlot(argsList):
	[playerID] = argsList

	def isValid(playerID, x, y):
		map = CyMap()
		pPlot = map.plot(x, y)
		
		if (pPlot.getArea() != map.findBiggestArea(False).getID()):
			return False

		return True
	
	return CvMapGeneratorUtil.findStartingPlot(playerID, isValid)

class TerraMultilayeredFractal(CvMapGeneratorUtil.MultilayeredFractal):
	# Subclass. Only the controlling function overridden in this case.
	def generatePlotsByRegion(self):
		# Sirian's MultilayeredFractal class, controlling function.
		# You -MUST- customize this function for each use of the class.
		#
		# The following grain matrix is specific to Terra.py
		sizekey = self.map.getWorldSize()
		sizevalues = {
			WorldSizeTypes.WORLDSIZE_DUEL:      (3,2,1,2),
			WorldSizeTypes.WORLDSIZE_TINY:      (3,2,1,2),
			WorldSizeTypes.WORLDSIZE_SMALL:     (4,2,1,2),
			WorldSizeTypes.WORLDSIZE_STANDARD:  (4,2,1,2),
			WorldSizeTypes.WORLDSIZE_LARGE:     (4,2,1,2),
			WorldSizeTypes.WORLDSIZE_HUGE:      (5,2,1,2),
			WorldSizeTypes.WORLDSIZE_GIANT:     (6,2,1,2)
			}
		(archGrain, contGrain, gaeaGrain, eurasiaGrain) = sizevalues[sizekey]
		
		# Sea Level adjustment (from user input), limited to value of 5%.
		sea = self.gc.getSeaLevelInfo(self.map.getSeaLevel()).getSeaLevelChange()
		sea = min(sea, 5)
		sea = max(sea, -5)

		# The following regions are specific to Terra.py
		newworldWestLon = 0.05
		newworldEastLon = 0.35
		eurasiaWestLon = 0.45
		eurasiaEastLon = 0.95
		eurasiaNorthLat = 0.95
		eurasiaSouthLat = 0.45
		thirdworldDimension = 0.125
		thirdworldNorthLat = 0.35
		thirdworldSouthLat = 0.05
		subcontinentLargeHorz = 0.2
		subcontinentLargeVert = 0.32
		subcontinentLargeNorthLat = 0.6
		subcontinentLargeSouthLat = 0.28
		subcontinentSmallDimension = 0.125
		subcontinentSmallNorthLat = 0.525
		subcontinentSmallSouthLat = 0.4

		# Dice rolls to randomize the quadrants (specific to Terra.py's regions)
		roll1 = self.dice.get(2, "Eurasian Hemisphere N/S - Terra PYTHON")
		if roll1 == 1:
			eurasiaNorthLat -= 0.4; eurasiaSouthLat -= 0.4
			thirdworldNorthLat += 0.6; thirdworldSouthLat += 0.6
			subcontinentLargeNorthLat += 0.12; subcontinentLargeSouthLat += 0.12
			subcontinentSmallNorthLat += 0.075; subcontinentSmallSouthLat += 0.075
		roll2 = self.dice.get(2, "Eurasian Hemisphere E/W - Terra PYTHON")
		if roll2 == 1:
			newworldWestLon += 0.6; newworldEastLon += 0.6
			eurasiaWestLon -= 0.4; eurasiaEastLon -= 0.4

		# Simulate the Old World - a large continent akin to Earth's Eurasia.
		NiTextOut("Generating the Old World (Python Terra) ...")
		# Set dimensions of the Old World region (specific to Terra.py)
		eurasiaWestX = int(self.iW * eurasiaWestLon)
		eurasiaEastX = int(self.iW * eurasiaEastLon)
		eurasiaNorthY = int(self.iH * eurasiaNorthLat)
		eurasiaSouthY = int(self.iH * eurasiaSouthLat)
		eurasiaWidth = eurasiaEastX - eurasiaWestX + 1
		eurasiaHeight = eurasiaNorthY - eurasiaSouthY + 1
		
		eurasiaWater = 55+sea

		self.generatePlotsInRegion(eurasiaWater,
		                           eurasiaWidth, eurasiaHeight,
		                           eurasiaWestX, eurasiaSouthY,
		                           eurasiaGrain, archGrain,
		                           self.iHorzFlags, self.iTerrainFlags,
		                           -1, -1,
		                           True, 11,
		                           2, False,
		                           False
		                           )

		# Eurasia, second layer (to increase pangaea-like cohesion).
		twHeight = eurasiaHeight/2
		twWestX = eurasiaWestX + eurasiaWidth/10
		twEastX = eurasiaEastX - eurasiaWidth/10
		twWidth = twEastX - twWestX + 1
		twNorthY = eurasiaNorthY - eurasiaHeight/4
		twSouthY = eurasiaSouthY + eurasiaHeight/4

		twWater = 60+sea; twGrain = 1; twRift = 2
                
		self.generatePlotsInRegion(twWater,
		                           twWidth, twHeight,
		                           twWestX, twSouthY,
		                           twGrain, archGrain,
		                           self.iHorzFlags, self.iTerrainFlags,
		                           -1, -1,
		                           True, 11,
		                           twRift, False,
		                           False
		                           )

		# Simulate the New World - land masses akin to Earth's American continents.
		# First simulate North America
		NiTextOut("Generating the New World (Python Terra) ...")
		nwWestX = int(self.iW * newworldWestLon)
		nwEastX = int(self.iW * newworldEastLon)
		nwNorthY = int(self.iH * 0.85)
		nwSouthY = int(self.iH * 0.52)
		nwWidth = nwEastX - nwWestX + 1
		nwHeight = nwNorthY - nwSouthY + 1

		nwWater = 61+sea; nwGrain = 1; nwRift = -1
                
		self.generatePlotsInRegion(nwWater,
		                           nwWidth, nwHeight,
		                           nwWestX, nwSouthY,
		                           nwGrain, archGrain,
		                           self.iVertFlags, self.iTerrainFlags,
		                           6, 6,
		                           True, 7,
		                           nwRift, False,
		                           False
		                           )

		# Now simulate South America
		nwsRoll = self.dice.get(2, "New World South E/W - Terra PYTHON")
		nwsVar = 0.0
		if nwsRoll == 1: nwsVar = 0.05
		nwsWestX = nwWestX + int(self.iW * (0.08 - nwsVar)) # Not as wide as the north
		nwsEastX = nwEastX - int(self.iW * (0.03 + nwsVar))
		nwsNorthY = int(self.iH * 0.47)
		nwsSouthY = int(self.iH * 0.25)
		nwsWidth = nwsEastX - nwsWestX + 1
		nwsHeight = nwsNorthY - nwsSouthY + 1

		nwsWater = 55+sea; nwsGrain = 1; nwsRift = -1
                
		self.generatePlotsInRegion(nwsWater,
		                           nwsWidth, nwsHeight,
		                           nwsWestX, nwsSouthY,
		                           nwsGrain, archGrain,
		                           self.iRoundFlags, self.iTerrainFlags,
		                           6, 6,
		                           True, 5,
		                           nwsRift, False,
		                           False
		                           )

		nwpWestX = nwWestX + int(self.iW * (0.1 - nwsVar)) # Not as wide as the north
		nwpEastX = nwEastX - int(self.iW * (0.07 + nwsVar))
		nwpNorthY = int(self.iH * 0.3)
		nwpSouthY = int(self.iH * 0.18)
		nwpWidth = nwpEastX - nwpWestX + 1
		nwpHeight = nwpNorthY - nwpSouthY + 1

		nwpWater = 67+sea; nwpGrain = 1; nwpRift = -1
                
		self.generatePlotsInRegion(nwpWater,
		                           nwpWidth, nwpHeight,
		                           nwpWestX, nwpSouthY,
		                           nwpGrain, archGrain,
		                           self.iVertFlags, self.iTerrainFlags,
		                           6, 5,
		                           True, 3,
		                           nwpRift, False,
		                           False
		                           )

		# Now the Yukon
		twWidth = int(self.iW * 0.15)
		twWestX = nwWestX
		boreal = self.dice.get(2, "New World North E/W - Terra PYTHON")
		if boreal == 1: twWestX += int(self.iW * 0.15)
		twEastX = twWestX + twWidth
		twNorthY = int(self.iH * 0.93)
		twSouthY = int(self.iH * 0.75)
		twHeight = twNorthY - twSouthY + 1

		twWater = 68+sea; twGrain = 2; twRift = -1
                
		self.generatePlotsInRegion(twWater,
		                           twWidth, twHeight,
		                           twWestX, twSouthY,
		                           twGrain, archGrain,
		                           self.iRoundFlags, self.iTerrainFlags,
		                           6, 5,
		                           True, 5,
		                           twRift, False,
		                           False
		                           )

		# Now add a random region of arctic islands
		twWidth = int(thirdworldDimension * self.iW)
		twHeight = int(thirdworldDimension * self.iH)
		if boreal == 0: 
			twEastX = nwEastX
			twWestX = twEastX - twWidth
		else:
			twWestX = nwWestX
			twEastX = twWestX + twWidth
		twNorthY = int(self.iH * 0.975)
		twSouthY = int(self.iH * 0.85)

		twWater = 76+sea; twGrain = archGrain; twRift = -1
                
		self.generatePlotsInRegion(twWater,
		                           twWidth, twHeight,
		                           twWestX, twSouthY,
		                           twGrain, archGrain,
		                           self.iHorzFlags, self.iTerrainFlags,
		                           6, 5,
		                           True, 5,
		                           twRift, False,
		                           False
		                           )

 		# Now simulate Central America
 		nwcVar = 0.0
		if nwsRoll == 1: nwcVar = 0.04
		nwcWidth = int(self.iW * 0.06)
		nwcRoll = self.dice.get(2, "Central America and Carribean Placement - Terra PYTHON")
		nwcWestX = nwWestX + int(self.iW * (0.1 + nwcVar))
		nwcEastX = nwcWestX + nwcWidth
		nwcNorthY = int(self.iH * 0.6)
		nwcSouthY = int(self.iH * 0.42)
		nwcHeight = nwcNorthY - nwcSouthY + 1

		nwcWater = 60+sea; nwcGrain = 1; nwcRift = -1
                
		self.generatePlotsInRegion(nwcWater,
		                           nwcWidth, nwcHeight,
		                           nwcWestX, nwcSouthY,
		                           nwcGrain, archGrain,
		                           self.iVertFlags, self.iTerrainFlags,
		                           6, 5,
		                           True, 5,
		                           nwcRift, False,
		                           False
		                           )

		# Now the Carribean islands
 		carVar = 0.0
		if nwsRoll == 1: carVar = 0.15
		twWidth = int(0.15 * self.iW)
		twEastX = nwEastX - int(carVar * self.iW)
		twWestX = twEastX - twWidth
		twNorthY = int(self.iH * 0.55)
		twSouthY = int(self.iH * 0.47)
		twHeight = twNorthY - twSouthY + 1

		twWater = 75+sea; twGrain = archGrain + 1; twRift = -1
                
		self.generatePlotsInRegion(twWater,
		                           twWidth, twHeight,
		                           twWestX, twSouthY,
		                           twGrain, archGrain,
		                           0, self.iTerrainFlags,
		                           6, 5,
		                           True, 3,
		                           twRift, False,
		                           False
		                           )

		# Add subcontinents to the Old World, one large, one small. (Terra.py)
		# Subcontinents can be akin to pangaea, continents, or archipelago.
		# The large adds an amount of land akin to subSaharan Africa.
		# The small adds an amount of land akin to South Pacific islands.
		NiTextOut("Generating the Third World (Python Terra) ...")
		scLargeWidth = int(subcontinentLargeHorz * self.iW)
		scLargeHeight = int(subcontinentLargeVert * self.iH)
		scRoll = self.dice.get((eurasiaWidth - scLargeWidth), "Large Subcontinent Placement - Terra PYTHON")
		scWestX = eurasiaWestX + scRoll
		scEastX = scWestX + scLargeWidth
		scNorthY = int(self.iH * subcontinentLargeNorthLat)
		scSouthY = int(self.iH * subcontinentLargeSouthLat)

		scShape = self.dice.get(4, "Large Subcontinent Shape - Terra PYTHON")
		if scShape > 1: # Massive subcontinent! (Africa style)
			scWater = 55+sea; scGrain = 1; scRift = 2
		elif scShape == 1: # Standard subcontinent.
			scWater = 66+sea; scGrain = 2; scRift = 2
		else: # scShape == 0, Archipelago subcontinent.
			scWater = 77+sea; scGrain = archGrain; scRift = -1
                
		self.generatePlotsInRegion(scWater,
		                           scLargeWidth, scLargeHeight,
		                           scWestX, scSouthY,
		                           scGrain, archGrain,
		                           self.iRoundFlags, self.iTerrainFlags,
		                           6, 6,
		                           True, 7,
		                           scRift, False,
		                           False
		                           )

		scSmallWidth = int(subcontinentSmallDimension * self.iW)
		scSmallHeight = int(subcontinentSmallDimension * self.iH)
		endless = 1
		while endless == 1: # Prevent excessive overlap of the two subcontinents.
			scsRoll = self.dice.get((eurasiaWidth - scSmallWidth), "Small Subcontinent Placement - Terra PYTHON")
			scsWestX = eurasiaWestX + scsRoll
			if abs((scsWestX + self.iW/12) - scWestX) > self.iW/8: break
		scsEastX = scsWestX + scSmallWidth
		scsNorthY = int(self.iH * subcontinentSmallNorthLat)
		scsSouthY = int(self.iH * subcontinentSmallSouthLat)

		scsShape = self.dice.get(4, "Small Subcontinent Shape - Terra PYTHON")
		if scsShape == 2: # Massive subcontinent!
			scsWater = 55+sea; scsGrain = 1; scsRift = 2
		elif scsShape == 1: # Standard subcontinent. (India style).
			scsWater = 66+sea; scsGrain = 2; scsRift = 2
		else: # scsShape == 0 or 3, Archipelago subcontinent (East Indies style).
			scsWater = 77+sea; scsGrain = archGrain; scsRift = -1
                
		self.generatePlotsInRegion(scsWater,
		                           scSmallWidth, scSmallHeight,
		                           scsWestX, scsSouthY,
		                           scsGrain, archGrain,
		                           self.iHorzFlags, self.iTerrainFlags,
		                           6, 5,
		                           True, 5,
		                           scsRift, False,
		                           False
		                           )

		# Now simulate random lands akin to Australia and Antarctica
		extras = 2 + self.dice.get(3, "Number of Minor Regions - Terra PYTHON")
		for loop in range(extras):
			# Two to four of these regions.
			twWidth = int(thirdworldDimension * self.iW)
			twHeight = int(thirdworldDimension * self.iH)
			twVertRange = int(0.3 * self.iH) - twHeight
			twRoll = self.dice.get((eurasiaWidth - twWidth), "Minor Region Placement - Terra PYTHON")
			twWestX = eurasiaWestX + twRoll
			twEastX = scWestX + scLargeWidth
			twVertRoll = self.dice.get(twVertRange, "Minor Region Placement - Terra PYTHON")
			twNorthY = int(self.iH * thirdworldNorthLat) + twVertRoll
			twSouthY = int(self.iH * thirdworldSouthLat) + twVertRoll

			twShape = self.dice.get(3, "Minor Region Shape - Terra PYTHON")
			if twShape == 2: # Massive subcontinent!
				twWater = 60+sea; twGrain = 1; twRift = 2
			elif twShape == 1: # Standard subcontinent.
				twWater = 65+sea; twGrain = 2; twRift = 2
			else: # twShape == 0, Archipelago subcontinent.
				twWater = 70+sea; twGrain = archGrain; twRift = -1
                
			self.generatePlotsInRegion(twWater,
			                           twWidth, twHeight,
			                           twWestX, twSouthY,
			                           twGrain, archGrain,
			                           self.iHorzFlags, self.iTerrainFlags,
			                           6, 5,
			                           True, 5,
			                           twRift, False,
			                           False
			                           )

		# All regions have been processed. Plot Type generation completed.
		return self.wholeworldPlotTypes

'''
Regional Variables Key:

iWaterPercent,
iRegionWidth, iRegionHeight,
iRegionWestX, iRegionSouthY,
iRegionGrain, iRegionHillsGrain,
iRegionPlotFlags, iRegionTerrainFlags,
iRegionFracXExp, iRegionFracYExp,
bShift, iStrip,
rift_grain, has_center_rift,
invert_heights
'''

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Terra) ...")
	# Call generatePlotsByRegion() function, from TerraMultilayeredFractal subclass.
	global plotgen
	plotgen = TerraMultilayeredFractal()
	return plotgen.generatePlotsByRegion()

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Terra) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	NiTextOut("Adding Features (Python Terra) ...")
	featuregen = FeatureGenerator()
	featuregen.addFeatures()
	return 0

def addRivers():
	print "-- addRivers()"
	mst.mapPrint.buildTerrainMap( True, "addRivers()" )

	# Generate marsh terrain
	mst.marshMaker.convertTerrain()

	# Expand coastal waters - you may not want this
	mst.mapPrettifier.expandifyCoast()
	# Some scripts produce more chaotic terrain than others. You can create more connected
	# (bigger) deserts by converting surrounded plains and grass.
	# Prettify the map - create better connected deserts and plains
	mst.mapPrettifier.lumpifyTerrain( mst.etDesert, mst.etPlains, mst.etGrass )
	mst.mapPrettifier.lumpifyTerrain( mst.etPlains, mst.etDesert, mst.etGrass )

	# No standard rivers for 'SandsOfMars'
	CyPythonMgr().allowDefaultImpl()							# don't forget this

	# Put rivers on small islands
	mst.riverMaker.islandRivers()
	
def addLakes():
	print "-- addLakes()"
	mst.mapPrint.buildRiverMap( True, "addRivers()" )

	CyPythonMgr().allowDefaultImpl()

def addBonuses():
	print "-- addBonuses()"
	mst.mapPrint.buildFeatureMap( True, "addBonuses()" )

	# if the script handles boni itself, insert the function here
	CyPythonMgr().allowDefaultImpl()	
	
def assignStartingPlots():
	print "-- assignStartingPlots()"
	mst.mapPrint.buildBonusMap( True, "assignStartingPlots()" )

	CyPythonMgr().allowDefaultImpl()
	
def normalizeStartingPlotLocations():
	print "-- normalizeStartingPlotLocations()"
	mst.mapPrint.buildRiverMap( True, "addRivers()" )		# river-map also shows starting-plots

	# shuffle starting-plots for teams
	#opt = map.getCustomMapOption(3)						# assuming the 4th map-option is for teams
	#if opt == 0:
	#	CyPythonMgr().allowDefaultImpl()					# by default civ places teams near to each other
	#	# mst.teamStart.placeTeamsTogether( True, True )	# use teamStart to place teams near to each other
	#elif opt == 1:
	#	mst.teamStart.placeTeamsTogether( False, True )		# shuffle starting-plots to separate team players
	#elif opt == 2:
	#	mst.teamStart.placeTeamsTogether( True, True )		# randomize starting-plots (may be near or not)
	#else:
	#	mst.teamStart.placeTeamsTogether( False, False )	# leave starting-plots alone

	# comment this out if team option exists
	CyPythonMgr().allowDefaultImpl()
	
