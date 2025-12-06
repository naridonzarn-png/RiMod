#
#	FILE:	 Global_Highlands.py
#	AUTHOR:  Bob Thomas (Sirian)
#	PURPOSE: Global map script - mountainous terrain
#-----------------------------------------------------------------------------
#	Copyright (c) 2005, 2007 Firaxis Games, Inc. All rights reserved.
#-----------------------------------------------------------------------------
#

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil
import random
import sys
from math import sqrt
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
	return "TXT_KEY_MAP_SCRIPT_GLOBAL_HIGHLANDS_DESCR"

def getNumCustomMapOptions():
	return 5
	
def getNumHiddenCustomMapOptions():
	return 2

def getCustomMapOptionName(argsList):
	[iOption] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_MOUNTAIN_PATTERN",
		1:	"TXT_KEY_MAP_SCRIPT_MOUNTAIN_DENSITY",
		2:	"TXT_KEY_MAP_SCRIPT_LANDMASS_SIZE",
		3:  "TXT_KEY_MAP_WORLD_WRAP",
		4:  "TXT_KEY_CONCEPT_RESOURCES"
		}
	translated_text = unicode(CyTranslator().getText(option_names[iOption], ()))
	return translated_text
	
def getNumCustomMapOptionValues(argsList):
	[iOption] = argsList
	option_values = {
		0:	3,
		1:	3,
		2:	4,
		3:  3,
		4:  2
		}
	return option_values[iOption]
	
def getCustomMapOptionDescAt(argsList):
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			0: "TXT_KEY_MAP_SCRIPT_SCATTERED",
			1: "TXT_KEY_MAP_SCRIPT_RIDGELINES",
			2: "TXT_KEY_MAP_SCRIPT_CLUSTERED"
			},
		1:	{
			0: "TXT_KEY_MAP_SCRIPT_DENSE_PEAKS",
			1: "TXT_KEY_MAP_SCRIPT_NORMAL_PEAKS",
			2: "TXT_KEY_MAP_SCRIPT_THIN_PEAKS"
			},
		2:	{
			0: "TXT_KEY_MAP_SCRIPT_MASSIVE_CONTINENTS",
			1: "TXT_KEY_MAP_SCRIPT_NORMAL_CONTINENTS",
			2: "TXT_KEY_MAP_SCRIPT_SNAKY_CONTINENTS",
			3: "TXT_KEY_MAP_SCRIPT_RANDOM"
			},
		3:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			},
		4:	{
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
		1:	1,
		2:	3,
		3:  1,
		4:  0
		}
	return option_defaults[iOption]

def isRandomCustomMapOption(argsList):
	[iOption] = argsList
	option_random = {
		0:	true,
		1:	true,
		2:	false,
		3:	false,
		4:  false
		}
	return option_random[iOption]

def isAdvancedMap():
	"This map should not show up in simple mode"
	return 1
	
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
	return (map.getCustomMapOption(3) == 1 or map.getCustomMapOption(3) == 2)
	
def getWrapY():
	map = CyMap()
	return (map.getCustomMapOption(3) == 2)

def normalizeAddExtras():
	if (CyMap().getCustomMapOption(4) == 1):
		balancer.normalizeAddExtras()
	CyPythonMgr().allowDefaultImpl()	# do the rest of the usual normalizeStartingPlots stuff, don't overrride

def addBonusType(argsList):
	[iBonusType] = argsList
	gc = CyGlobalContext()
	type_string = gc.getBonusInfo(iBonusType).getType()

	if (CyMap().getCustomMapOption(4) == 1):
		if (type_string in balancer.resourcesToBalance) or (type_string in balancer.resourcesToEliminate):
			return None # don't place any of this bonus randomly
		
	CyPythonMgr().allowDefaultImpl() # pretend we didn't implement this method, and let C handle this bonus in the default way

def getGridSize(argsList):
	"Enlarge the grids! Need extra land to cover that 'wasted' by all the peaks!"
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:		(13,8),
		WorldSizeTypes.WORLDSIZE_TINY:		(16,10),
		WorldSizeTypes.WORLDSIZE_SMALL:		(21,13),
		WorldSizeTypes.WORLDSIZE_STANDARD:	(26,16),
		WorldSizeTypes.WORLDSIZE_LARGE:		(32,20),
		WorldSizeTypes.WORLDSIZE_HUGE:		(38,24),
		WorldSizeTypes.WORLDSIZE_GIANT:		(44,28)
	}

	if (argsList[0] == -1): # (-1,) is passed to function on loads
		return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]

def minStartingDistanceModifier():
	return -25

# subclass FractalWorld to borrow default process for land/sea formation only.
class GHFractalWorld(CvMapGeneratorUtil.FractalWorld):
	def generatePlotTypes(self, water_percent=78, shift_plot_types=True, grain_amount=3):
		# Check for changes to User Input variances.
		self.checkForOverrideDefaultUserInputVariances()
		
		self.hillsFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)
		self.peaksFrac.fracInit(self.iNumPlotsX, self.iNumPlotsY, grain_amount+1, self.mapRand, self.iFlags, self.fracXExp, self.fracYExp)

		water_percent += self.seaLevelChange
		water_percent = min(water_percent, self.seaLevelMax)
		water_percent = max(water_percent, self.seaLevelMin)

		iWaterThreshold = self.continentsFrac.getHeightFromPercent(water_percent)
		iHillsBottom1 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupOneBase - self.hillGroupOneRange), 0))
		iHillsTop1 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupOneBase + self.hillGroupOneRange), 100))
		iHillsBottom2 = self.hillsFrac.getHeightFromPercent(max((self.hillGroupTwoBase - self.hillGroupTwoRange), 0))
		iHillsTop2 = self.hillsFrac.getHeightFromPercent(min((self.hillGroupTwoBase + self.hillGroupTwoRange), 100))
		iPeakThreshold = self.peaksFrac.getHeightFromPercent(self.peakPercent)

		for x in range(self.iNumPlotsX):
			for y in range(self.iNumPlotsY):
				i = y*self.iNumPlotsX + x
				val = self.continentsFrac.getHeight(x,y)
				if val <= iWaterThreshold:
					self.plotTypes[i] = PlotTypes.PLOT_OCEAN
				else:
					self.plotTypes[i] = PlotTypes.PLOT_LAND

		if shift_plot_types:
			self.shiftPlotTypes()

		return self.plotTypes

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Global Highlands) ...")
	NiTextOut("Setting Plot Types (Python Global Highlands) ...")
	gc = CyGlobalContext()
	map = CyMap()
	dice = gc.getGame().getMapRand()
	iFlags = 0  # Disallow FRAC_POLAR flag, to prevent "zero row" problems.
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	plotTypes = [PlotTypes.PLOT_OCEAN] * (iW*iH)
	terrainFrac = CyFractal()
	
	# Get custom map user inputs.
	userInputGrain = map.getCustomMapOption(0)
	userInputPeaks = map.getCustomMapOption(1)
	userInputLandmass = map.getCustomMapOption(2)

	fractal_world = GHFractalWorld()
	
	if userInputLandmass == 3: #Random landmass sizes
		grainRoll = 1 + dice.get(7, "Fractal Grain - Global Highlands PYTHON")
		if grainRoll > 4: grainRoll -= 4
		if grainRoll == 4:
			fractal_world.initFractal(polar = True)
			plotTypes = fractal_world.generatePlotTypes(water_percent=75)
		else:
			fractal_world.initFractal(continent_grain = grainRoll, rift_grain = -1, has_center_rift = False, polar = True)
			plotTypes = fractal_world.generatePlotTypes()
	else:
		grainRoll = 1 + userInputLandmass
		fractal_world.initFractal(continent_grain = grainRoll, rift_grain = -1, has_center_rift = False, polar = True)
		plotTypes = fractal_world.generatePlotTypes()

	# Varying grains for hills/peaks per map size and Mountain Ranges setting.
	# [clustered_grain, ridgelines_grain, scattered_grain]
	worldsizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:      [3,4,5],
		WorldSizeTypes.WORLDSIZE_TINY:      [3,4,5],
		WorldSizeTypes.WORLDSIZE_SMALL:     [4,5,6],
		WorldSizeTypes.WORLDSIZE_STANDARD:  [4,5,6],
		WorldSizeTypes.WORLDSIZE_LARGE:     [4,5,6],
		WorldSizeTypes.WORLDSIZE_HUGE:      [4,5,6],
		WorldSizeTypes.WORLDSIZE_GIANT:     [4,5,6]
		}
	grain_list = worldsizes[map.getWorldSize()]
	grain_list.reverse()
	grain = grain_list[userInputGrain]
	
	# Peak density
	peak_list = [65, 70, 77]
	hill_list = [35, 40, 45]
	peaks = peak_list[userInputPeaks]
	hills = hill_list[userInputPeaks]
	
	terrainFrac.fracInit(iW, iH, grain, dice, 0, -1, -1)

	iHillsThreshold = terrainFrac.getHeightFromPercent(hills)
	iPeaksThreshold = terrainFrac.getHeightFromPercent(peaks)

	# Now the main loop, which will assign the plot types.
	for x in range(iW):
		for y in range(iH):
			i = y*iW + x
			val = terrainFrac.getHeight(x,y)
			if plotTypes[i] == PlotTypes.PLOT_OCEAN:
				continue # Water plots already set.
			if val >= iPeaksThreshold:
				plotTypes[i] = PlotTypes.PLOT_PEAK
			elif val >= iHillsThreshold and val < iPeaksThreshold:
				plotTypes[i] = PlotTypes.PLOT_HILLS
			else:
				pass

	return plotTypes

def generateTerrainTypes():
	NiTextOut("Generating Terrain (Python Global Highlands) ...")
	terraingen = TerrainGenerator()
	terrainTypes = terraingen.generateTerrain()
	return terrainTypes

def addFeatures():
	# Remove all peaks along the coasts, before adding Features, Bonuses, Goodies, etc.
	map = CyMap()
	iW = map.getGridWidth()
	iH = map.getGridHeight()
	for plotIndex in range(iW * iH):
		pPlot = map.plotByIndex(plotIndex)
		if pPlot.isPeak() and pPlot.isCoastalLand():
			# If a peak is along the coast, change to hills and recalc.
			pPlot.setPlotType(PlotTypes.PLOT_HILLS, true, true)
	
	# Now add Features.
	NiTextOut("Adding Features (Python Global Highlands) ...")
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