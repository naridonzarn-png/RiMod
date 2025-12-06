#
#	FILE:	 Continents.py
#	AUTHOR:  Soren Johnson
#	PURPOSE: Global map script - Civ4's default map script
#-----------------------------------------------------------------------------
#	Copyright (c) 2004, 2005 Firaxis Games, Inc. All rights reserved.
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

# The following two functions are not exactly neccessary either, but they should be
# in all map-scripts. Just comment them out if they are already in the script.
# ---------------------------------------------------------------------------------
def getVersion():
	return "1.20a"
	
def getDescription():
	return "TXT_KEY_MAP_SCRIPT_CONTINENTS_DESCR"

def getNumCustomMapOptions():
	return 0

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
	
def isAdvancedMap():
	"This map should show up in simple mode"
	return 0

def generatePlotTypes():
	NiTextOut("Setting Plot Types (Python Continents) ...")
	fractal_world = FractalWorld()
	fractal_world.initFractal(polar = True)
	return fractal_world.generatePlotTypes(water_percent=75)

def generateTerrainTypes():
	print "-- generateTerrainTypes()"
	mst.mapPrint.buildPlotMap( True, "generateTerrainTypes()" )

	# Planetfall: build more highlands and ridges
	mst.planetFallMap.buildPfallHighlands()

	# Prettify the map - you may not want this
	mst.mapPrettifier.hillifyCoast()
	mst.mapPrettifier.bulkifyIslands()

	# Choose terrainGenerator
	terrainGen = mst.MST_TerrainGenerator()			# this is the default
	# terrainGen = MyTerrainGenerator() 			# better is the terrain generator of the map-script
	# Generate terrain
	terrainTypes = terrainGen.generateTerrain()
	return terrainTypes

def addRivers():
	print "-- addRivers()"
	mst.mapPrint.buildTerrainMap( True, "addRivers()" )

	# Generate marsh terrain
	mst.marshMaker.convertTerrain()

	# Create map-regions
	mst.mapRegions.buildBigBogs()									# build BigBogs
	mst.mapRegions.buildBigDents()									# build BigDents

	# Expand coastal waters - you may not want this
	mst.mapPrettifier.expandifyCoast()
	# Generate DeepOcean-terrain if mod allows for it
	mst.deepOcean.buildDeepOcean()

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

	# No lakes on desertified Mars
	CyPythonMgr().allowDefaultImpl()	

def addFeatures():
	print "-- addFeatures()"
	mst.mapPrint.buildRiverMap( True, "addFeatures()" )

	# Prettify map - connect some small adjacent lakes
	mst.mapPrettifier.connectifyLakes()
	# Sprout rivers from lakes
	# - all lakes, 33% chance for each of a maximum of two rivers, from lakes of minimum size 2
	mst.riverMaker.buildRiversFromLake( None, 33, 2, 2 )

	featureGen = mst.MST_FeatureGenerator()		# 'Mars Now!' needs this generator
	featureGen.addFeatures()

	# Planetfall: handle shelves and trenches
	mst.planetFallMap.buildPfallOcean()
	# Prettify the map - transform coastal volcanos; default: 66% chance
	mst.mapPrettifier.beautifyVolcanos()
	# Build ElementalQuarter; default: 33% chance
	mst.mapRegions.buildElementalQuarter()

def addBonuses():
	print "-- addBonuses()"
	mst.mapPrint.buildFeatureMap( True, "addBonuses()" )
	CyPythonMgr().allowDefaultImpl()

def normalizeAddExtras():
	print "-- normalizeAddExtras()"

	# Balance boni, place missing boni and move minerals
	balancer.normalizeAddExtras()

	# Do the default housekeeping
	CyPythonMgr().allowDefaultImpl()

	# Make sure marshes are on flatlands
	mst.marshMaker.normalizeMarshes()

	# Give extras to special regions
	mst.mapRegions.addRegionExtras()

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
	# Print manaMap if FFH
	if mst.bFFH: mst.mapPrint.buildBonusMap( True, "normalizeAddExtras():Mana", None, mst.mapPrint.manaDict )
	# Print riverMap
	mst.mapPrint.buildRiverMap( True, "normalizeAddExtras()" )
	# Print mod and map statistics
	mst.mapStats.mapStatistics()
	
