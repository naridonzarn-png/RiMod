#
#	FILE:	 Tilted_Axis.py
#	AUTHOR:  Bob Thomas (Sirian)
#	PURPOSE: Global map script - Simulates a world with its rotational axis 
#	         tipped over on to its side. This is also a square map.
#-----------------------------------------------------------------------------
#	Copyright (c) 2005 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
from CvMapGeneratorUtil import FractalWorld
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

def getVersion():
	return "1.20a"

def getDescription():
	return "TXT_KEY_MAP_SCRIPT_TILTED_AXIS_DESCR"

def getNumCustomMapOptions():
	return 1
	
def getCustomMapOptionName(argsList):
	translated_text = unicode(CyTranslator().getText("TXT_KEY_MAP_SCRIPT_LANDMASS_SIZE", ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	return 5
	
def getCustomMapOptionDescAt(argsList):
	iSelection = argsList[1]
	selection_names = ["TXT_KEY_MAP_SCRIPT_MASSIVE_CONTINENTS",
	                   "TXT_KEY_MAP_SCRIPT_NORMAL_CONTINENTS",
	                   "TXT_KEY_MAP_SCRIPT_SMALL_CONTINENTS",
	                   "TXT_KEY_MAP_SCRIPT_ISLANDS",
	                   "TXT_KEY_MAP_SCRIPT_TINY_ISLANDS"]
	translated_text = unicode(CyTranslator().getText(selection_names[iSelection], ()))
	return translated_text
	
def getCustomMapOptionDefault(argsList):
	return -1

def getGridSize(argsList):
	"Override Grid Size function to make the maps square."
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:      (8,8),
		WorldSizeTypes.WORLDSIZE_TINY:      (10,10),
		WorldSizeTypes.WORLDSIZE_SMALL:     (14,14),
		WorldSizeTypes.WORLDSIZE_STANDARD:  (18,18),
		WorldSizeTypes.WORLDSIZE_LARGE:     (22,22),
		WorldSizeTypes.WORLDSIZE_HUGE:      (27,27),
		WorldSizeTypes.WORLDSIZE_GIANT:     (30,30)
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def getWrapX():
	return False
def getWrapY():
	return True
	
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
    
# subclass FractalWorld to enable square exponents for use with Tilted Axis.
class TiltedAxisFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def initFractal(self, continent_grain = 2, rift_grain = 2, has_center_rift = True):
		"For no rifts, use rift_grain = -1"
		iFlags = CyFractal.FracVals.FRAC_WRAP_Y + CyFractal.FracVals.FRAC_POLAR
		worldsizes = {
			WorldSizeTypes.WORLDSIZE_DUEL:      (6,6),
			WorldSizeTypes.WORLDSIZE_TINY:      (6,6),
			WorldSizeTypes.WORLDSIZE_SMALL:     (6,6),
			WorldSizeTypes.WORLDSIZE_STANDARD:  (7,7),
			WorldSizeTypes.WORLDSIZE_LARGE:     (7,7),
			WorldSizeTypes.WORLDSIZE_HUGE:      (7,7),
			WorldSizeTypes.WORLDSIZE_GIANT:     (7,7)
			}
		(fracXExp, fracYExp) = worldsizes[self.map.getWorldSize()]

		if rift_grain >= 0:
			self.riftsFrac = CyFractal()
			self.riftsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, rift_grain, self.mapRand, iFlags, fracXExp, fracYExp)
			if has_center_rift:
				iFlags = iFlags | CyFractal.FracVals.FRAC_CENTER_RIFT
			self.continentsFrac.fracInitRifts(self.iNumPlotsX, self.iNumPlotsY, continent_grain, self.mapRand, iFlags, self.riftsFrac, fracXExp, fracYExp)
		else:
			self.continentsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, continent_grain, self.mapRand, iFlags, fracXExp, fracYExp)

def generatePlotTypes():
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	fractal_world = TiltedAxisFractalWorld()
	
	# Get user input.
	userInputLandmass = map.getCustomMapOption(0)
	
	if userInputLandmass == 4:
		NiTextOut("Setting Plot Types (Python Tilted Axis, Tiny Islands) ...")
		fractal_world.initFractal(continent_grain = 5, rift_grain = -1, has_center_rift = False)
		return fractal_world.generatePlotTypes(grain_amount = 4)

	elif userInputLandmass == 3:
		NiTextOut("Setting Plot Types (Python Tilted Axis, Islands) ...")
		fractal_world.initFractal(continent_grain = 4, rift_grain = -1, has_center_rift = False)
		return fractal_world.generatePlotTypes(grain_amount = 4)

	elif userInputLandmass == 2:
		NiTextOut("Setting Plot Types (Python Tilted Axis, Small Continents) ...")
		fractal_world.initFractal(continent_grain = 3, rift_grain = 3, has_center_rift = False)
		return fractal_world.generatePlotTypes(grain_amount = 4)
		
	elif userInputLandmass == 0:
		NiTextOut("Setting Plot Types (Python Tilted Axis, Massive Continents) ...")
		fractal_world.initFractal(continent_grain = 1, rift_grain = 2, has_center_rift = False)
		return fractal_world.generatePlotTypes(grain_amount = 4)
	
	else: # standard lands
		NiTextOut("Setting Plot Types (Python Tilted Axis, Normal Continents) ...")
		fractal_world.initFractal(continent_grain = 2, rift_grain = 2, has_center_rift = True)
		return fractal_world.generatePlotTypes(grain_amount = 4)
	
# subclass TerrainGenerator to make the climate "latitudes" run west to east
class TiltedAxisTerrainGenerator(CvMapGeneratorUtil.TerrainGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		# Latitudes run vertically for a world with a tilted axis.
		lat = abs((self.iWidth / 2) - iX)/float(self.iWidth/2) # 0.0 = equator, 1.0 = pole

		# Adjust latitude using self.variation fractal, to mix things up:
		lat += (128 - self.variation.getHeight(iX, iY))/(255.0 * 5.0)

		# Limit to the range [0, 1]:
		if lat < 0:
			lat = 0.0
		if lat > 1:
			lat = 1.0

		return lat

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Tilted Axis) ...")
	terraingen = TiltedAxisTerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

# subclass FeatureGenerator to make the climate "latitudes" run west to east
class TiltedAxisFeatureGenerator(CvMapGeneratorUtil.FeatureGenerator):
	def getLatitudeAtPlot(self, iX, iY):
		"returns a value in the range of 0.0 (tropical) to 1.0 (polar)"
		return abs((self.iGridW/2) - iX)/float(self.iGridW/2) # 0.0 = equator, 1.0 = pole

def addFeatures():
	NiTextOut("Adding Features (Python Tilted Axis) ...")
	featuregen = TiltedAxisFeatureGenerator()
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

# if the map-script disallows lakes, then just comment this out
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
	
def normalizeAddExtras():
	print "-- normalizeAddExtras()"

	# Balance boni, place missing boni and move minerals
	balancer.normalizeAddExtras()

	# Do the default housekeeping
	CyPythonMgr().allowDefaultImpl()

	# Print maps and stats
	mst.mapStats.statPlotCount( "" )
	# Print plotMap
	mst.mapPrint.buildPlotMap( True, "normalizeAddExtras()" )
	# Print areaMap
	mst.mapPrint.buildAreaMap( True, "normalizeAddExtras()" )
	# Print terrainMap
	mst.mapPrint.buildTerrainMap( True, "normalizeAddExtras()" )
	# Print featureMap
	mst.mapPrint.buildFeatureMap( True, "normalizeAddExtras()" )
	# Print bonusMap
	mst.mapPrint.buildBonusMap( True, "normalizeAddExtras()" )
	# Print riverMap
	mst.mapPrint.buildRiverMap( True, "normalizeAddExtras()" )
	# Print mod and map statistics
	mst.mapStats.mapStatistics()