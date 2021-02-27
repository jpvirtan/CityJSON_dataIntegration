#Conversion utility for producing a CityJSON -file from CSV data 
#By Juho-Pekka Virtanen, Aalto University, 2020
#Tested on Windows platform, Python 3.7.6, no external libraries should be required.
#Please see the README.md for further information
#Please see the LICENCE.txt for licence information

import csv
import json

print("Welcome")
print ("Please ensure that you use comma as separator.")

#Define path
print("Please input path to file for conversion (.csv)")
path = input()

#Define object title substring
print("Please provide name suffix for CityJSON objects")
subname = input()

#Lets open the file, see what we have...
try:
	rowlist = []
	with open(path, newline='') as csvfile:
		CSVreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in CSVreader:
			rowlist.append(row)
except:
	print("Reading file failed. Aborting")
	exit()

print("Succesfully read treelist from: " +path)
print("Found a total of " +str(len(rowlist))+ " rows.")
print("Here's a small sample:")
print(rowlist[0])
print(rowlist[1])
print(rowlist[2])

#Query user for column order
print("Please indicate coordinate positions from columns:")
m = 0
while m < len(rowlist[0]):
	print(str(m) + ": " + rowlist[0][m])
	m = m + 1
print("Indicate X:")
xpos = input()
print("Indicate Y:")
ypos = input()
print("Indicate Z:")
zpos = input()
print("Indicate position of object ID:")
idpos = input()
print("Indicate position of sub-object index:")
subidpos = input()

try:
	xpos = int(xpos)
	ypos = int(ypos)
	zpos = int(zpos)
	idpos = int(idpos)
	subidpos = int(subidpos)

	if xpos >= len(rowlist[0]) and ypos >= len(rowlist[0]) and zpos >= len(rowlist[0]) and idpos >= len(rowlist[0]) and subidpos >= len(rowlist[0]):
		print("Please input a valid selection.")
		exit()

except:
	print("Please input valid selection...")
	exit()

#Define crop
print("Enable crop?")
print("0 = No, process everything")
print("1 = Yes, exclude objects outside processing boundary")
crop = input()

try:
	crop = int(crop)
except:
	print("Please input valid selection.")
	exit()

if crop == 0:
	print("Processing the whole thing.")
	xmin = 0
	xmax = 0
	ymin = 0
	ymax = 0
if crop == 1:
	print("Please input crop range.")
	print("X min:")
	xmin = float(input())
	print("X max:")
	xmax = float(input())
	print("Y min:")
	ymin = float(input())
	print("Y max:")
	ymax = float(input())
if crop != 0 and crop != 1:
	print("Please input valid selection.")
	exit()

#Create empty dictionary
cityJSONRoot={}

#Set up CityJSON base structure
cityJSONRoot["type"] = "CityJSON"
cityJSONRoot["version"] = "1.0"
cityJSONRoot["CityObjects"] = ""
cityJSONRoot["vertices"] = ""

#Create empty objects that are to hold objects and vertices
cityJSONObjects = {}
cityJSONVertices = []

#Query user for processing style 
print("Please specify what to process")
print("1 = Points (plot as rectangle or with a 3D tree symbol)")
print("2 = Polygons")
getSelection = input()

try:
	getSelection = int(getSelection)
except:
	print("Please input integer number.")
	exit()

if (getSelection != 1) and (getSelection != 2):
	print("Incorrect selection. Aborting.")
	exit()
else:
	if getSelection == 1:
		objectType = "Tree"
	if getSelection == 2:
		objectType = "Area"
			
#This will track the amount of processed objects
writtenTrees = 0

#Processing track for polygonal areas
if objectType == "Area":

	#Query user for flipping normals
	print("Enable flipping normals?")
	print("0 = No")
	print("1 = Yes")
	flip = input()

	try:
		flip = int(flip)
	except:
		print("Please input valid selection.")
		exit()
	
	#Query user for what object type to write
	polygonObjectTypes = ["Building","BuildingPart","BuildingInstallation","Road","Railway","TransportSquare","WaterBody","LandUse","PlantCover","CityFurniture","GenericCityObject"]
	print("Please select object type to use:")
	m = 0
	while m < len(polygonObjectTypes):
		print(str(m) + ": " + polygonObjectTypes[m])
		m = m + 1

	selectedObjectType = input()
	try:
		selectedObjectType = int(selectedObjectType)
	except:
		print("Please input valid selection")
		exit()
	
	if selectedObjectType > len(polygonObjectTypes):
		print("Incorrect.")
		exit()

	print("Selected: " + polygonObjectTypes[selectedObjectType])

	#Read file
	pointlist = []
	with open(path, newline='') as csvfile:
		CSVreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in CSVreader:
			pointlist.append(row)

	i = 1 #Index holding the row to process, starts with 1 to skip header!

	polyID = 1 #What polygon to process
	polyPoints = []
	polys = []

	while i < len(pointlist): #Run as long as there are rows (e.g. points)

		#Check if new polygon
		if polyID == int(pointlist[i][idpos]):
			polyPoints.append(pointlist[i])
			i = i + 1
		else:
			if len(polyPoints) == 0: #Check for an empty polygon
				print("Found an empty polygon at: " +str(polyID) + " skipping this.")
				print(pointlist[i])
				polyPoints = []
				polyID = polyID + 1
			else: #New polygon begings, re-initialize
				polys.append(polyPoints)
				polyPoints = []
				polyID = polyID + 1
				
	print("Processed polygons " +str(polyID-1))
	print("Kept " +str(len(polys)))
	
	#Processing an individual polygon. All metadata is taken from the first point, as they are assumed to remain constant
	i = 0
	pointIndex = 0 #Index holding the vertice number, used in assembling boundary
	while i < len(polys):
		polyPoints = polys[i]
		subID = ""
		subIDcount = 0

		#Compute midpoint, used for cropping, if crop is enabled
		xMed = 0
		yMed = 0
		n = 0
		while n < len(polyPoints):
			xMed = xMed + float(polyPoints[n][xpos])
			yMed = yMed + float(polyPoints[n][ypos])
			if polyPoints[n][subidpos] != subID:
				subID = polyPoints[n][subidpos]
				subIDcount = subIDcount + 1
			n = n + 1
		xMed = xMed / len(polyPoints)
		yMed = yMed / len(polyPoints)
		print("Polygon " + str(i) + " center at X=" +str(xMed) + " Y=" +str(yMed))
		print("Polygon had " + str(subIDcount) + " sub-polygons.")

		if (xmin < xMed < xmax and ymin < yMed < ymax) or crop == 0:
			cityJSONAttributes = {}
			
			#This just dumps all attributes from original file to CityJSON, note that is super-non-schema-compliant
			m = 0
			while m < len(polyPoints[0]):
				if m != xpos and m != ypos and m != zpos and m != idpos:
					cityJSONAttributes[pointlist[0][m]] = polyPoints[0][m]
				m = m + 1

			#Create dict for geometry attributes
			cityJSONGeometryAttributes = {}
			cityJSONGeometryAttributes["type"] = "MultiSurface"
			cityJSONGeometryAttributes["lod"] = 2 #Note fixed LOD here!

			#Asseble lists for point indexes to form boundary and sub-boundary list
			#Sub boundary is used for objects that consists of multiple polygons
			boundaryList = []
			subBoundaryList = []

			n = 0
			subID = polyPoints[n][subidpos]
			while n < len(polyPoints):

				if polyPoints[n][subidpos] != subID:
					if flip == 1: #Flipping normals now!
						flippedList = []
						m = 0
						while m < len(subBoundaryList):
							flippedList.append(subBoundaryList[len(subBoundaryList)-(m+1)])
							m = m + 1
						subBoundaryList = flippedList #Replace original boundary list with a flipped one
					boundaryList.append([subBoundaryList])
					subBoundaryList = [] #Begin new sub-boundary list
					subBoundaryList.append(pointIndex) #Add points to new sb list
					subID = polyPoints[n][subidpos] #Update index following which sb were are writing to
				elif n == (len(polyPoints)-1): #Last point of polygon reached
					subBoundaryList.append(pointIndex) #Still add to the same sb
					if flip == 1: #Flipping normals now!
						flippedList = []
						m = 0
						while m < len(subBoundaryList):
							flippedList.append(subBoundaryList[len(subBoundaryList)-(m+1)])
							m = m + 1
						subBoundaryList = flippedList #Replace original boundary list with a flipped one
					boundaryList.append([subBoundaryList]) #Close object
				else:
					subBoundaryList.append(pointIndex) #Add to same sb as before, we remain in same object

				try:
					cityJSONVertices.append([float(polyPoints[n][xpos]),float(polyPoints[n][ypos]),float(polyPoints[n][zpos])]) #This is to go to vertice list, note that it is shared for the entire file
					writtenTrees = writtenTrees + 1
				except:
					print("Error encountered on this poly, writing Z = 0")
					print(polyPoints[n])
					cityJSONVertices.append([float(polyPoints[n][xpos]),float(polyPoints[n][ypos]),0.0]) #This is to go to vertice list, note that it is shared for the entire file
					writtenTrees = writtenTrees + 1

				pointIndex = pointIndex + 1
				n = n + 1

			cityJSONGeometryAttributes["boundaries"] = boundaryList
			#Basic structure for objects
			cityJSONObject = {}

			cityJSONObject["type"] = polygonObjectTypes[selectedObjectType]

			cityJSONObject["attributes"] = cityJSONAttributes
			cityJSONObject["geometry"] = [cityJSONGeometryAttributes]
			cityJSONObjects[polygonObjectTypes[selectedObjectType]+"_"+subname+"_"+polyPoints[1][idpos]] = cityJSONObject

		i = i + 1

#This is the processing pipeline for points, such as tree objects
if objectType == "Tree":
	treeList = []
	with open(path, newline='') as csvfile:
		CSVreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in CSVreader:
			treeList.append(row)

	#Query user for lod-representation to use
	print("Please specify model to utilize:")
	print("1 = 2D rectangle")
	print("2 = Simplified 3D tree icon")
	treeModel = input()

	try:
		treeModel = int(treeModel)
	except:
		print("Please input integer number.")
		exit()

	if (treeModel != 1) and (treeModel != 2):
		print("Incorrect selection. Aborting.")
		exit()

	#Default for tree size, later overwritten by what is found from data
	treeScale = 1

	#This is used to interpret Helsinki tree register size markings
	sizeGroups = ["0_-_10_cm","20_-_30_cm","30_-_50_cm","50_-_70_cm","70_cm_-"]
	# This is not smart, but remains here due to issues with original datasets.
	# Should be fixed in the future to be more ubiquitous...

	#Index to track how we progress in tree list
	i = 1

	while i < len(treeList):
		y = float(treeList[i][xpos])
		x = float(treeList[i][ypos])
		z = float(treeList[i][zpos])
	
		if (xmin < x < xmax and ymin < y < ymax) or crop == 0:
			n = 0
			while n < len(sizeGroups):
				if treeList[i][9] == sizeGroups[n]:
					treeScale = n * 3
				n = n + 1
	
			#Dict for object attributes
			cityJSONAttributes = {}

			#This just dumps all attributes from original file to CityJSON, note that is super-non-schema-compliant
			m = 0
			while m < len(treeList[i]):
				if m != xpos and m != ypos and m != zpos and m != idpos:
					cityJSONAttributes[treeList[i][m]] = treeList[i][m]
				m = m + 1

			#Dict for geometry attributes
			cityJSONGeometryAttributes = {}
			cityJSONGeometryAttributes["type"] = "MultiSurface"
			cityJSONGeometryAttributes["lod"] = treeModel

			#Create geometry for rectangular patch
			if treeModel == 1:
				cityJSONGeometryAttributes["boundaries"] = [[[writtenTrees*4,writtenTrees*4+1,writtenTrees*4+2,writtenTrees*4+3]]]

			#Create geometry for a small 3D tree symbol.
			if treeModel == 2:
				cityJSONGeometryAttributes["boundaries"] = [
				[[writtenTrees*13+0,writtenTrees*13+2,writtenTrees*13+5,writtenTrees*13+3]],
				[[writtenTrees*13+2,writtenTrees*13+1,writtenTrees*13+4,writtenTrees*13+5]],
				[[writtenTrees*13+1,writtenTrees*13+0,writtenTrees*13+3,writtenTrees*13+4]],
				[[writtenTrees*13+3,writtenTrees*13+5,writtenTrees*13+8,writtenTrees*13+6]],
				[[writtenTrees*13+5,writtenTrees*13+4,writtenTrees*13+7,writtenTrees*13+8]],
				[[writtenTrees*13+4,writtenTrees*13+3,writtenTrees*13+6,writtenTrees*13+7]],
				[[writtenTrees*13+6,writtenTrees*13+8,writtenTrees*13+11,writtenTrees*13+9]],
				[[writtenTrees*13+8,writtenTrees*13+7,writtenTrees*13+10,writtenTrees*13+11]],
				[[writtenTrees*13+7,writtenTrees*13+6,writtenTrees*13+9,writtenTrees*13+10]],
				[[writtenTrees*13+9,writtenTrees*13+11,writtenTrees*13+12]],
				[[writtenTrees*13+11,writtenTrees*13+10,writtenTrees*13+12]],
				[[writtenTrees*13+10,writtenTrees*13+9,writtenTrees*13+12]],
				]
				#In future, this should be expressed as templates for performance improvements in visualization.
		
			#Assebling the object
			cityJSONObject = {}
			cityJSONObject["type"] = "SolitaryVegetationObject"
			cityJSONObject["attributes"] = cityJSONAttributes
			cityJSONObject["geometry"] = [cityJSONGeometryAttributes]
			cityJSONObjects["Tree_" + subname + "_" + treeList[i][1]] = cityJSONObject
	
			#Add vertices for rectangular patch
			if treeModel == 1:
				cityJSONVertices.append([x+treeScale,y+treeScale,z])
				cityJSONVertices.append([x-treeScale,y+treeScale,z])
				cityJSONVertices.append([x-treeScale,y-treeScale,z])
				cityJSONVertices.append([x+treeScale,y-treeScale,z])
			
			#Add vertices for tree symbol
			if treeModel == 2:
				cityJSONVertices.append([x+0.000000*treeScale,y-0.093815*treeScale,z+0.000000*treeScale])
				cityJSONVertices.append([x-0.081246*treeScale,y+0.046907*treeScale,z+0.000000*treeScale])
				cityJSONVertices.append([x+0.081246*treeScale,y+0.046907*treeScale,z+0.000000*treeScale])
				cityJSONVertices.append([x+0.000000*treeScale,y-0.093815*treeScale,z+0.295725*treeScale])
				cityJSONVertices.append([x-0.081246*treeScale,y+0.046907*treeScale,z+0.295725*treeScale])
				cityJSONVertices.append([x+0.081246*treeScale,y+0.046907*treeScale,z+0.295725*treeScale])
				cityJSONVertices.append([x-0.000000*treeScale,y-0.351669*treeScale,z+0.696748*treeScale])
				cityJSONVertices.append([x-0.304555*treeScale,y+0.175835*treeScale,z+0.696748*treeScale])
				cityJSONVertices.append([x+0.304555*treeScale,y+0.175835*treeScale,z+0.696748*treeScale])
				cityJSONVertices.append([x-0.000000*treeScale,y-0.284935*treeScale,z+0.914895*treeScale])
				cityJSONVertices.append([x-0.246761*treeScale,y+0.142468*treeScale,z+0.914895*treeScale])
				cityJSONVertices.append([x+0.246761*treeScale,y+0.142468*treeScale,z+0.914895*treeScale])
				cityJSONVertices.append([x+0.000000*treeScale,y-0.000000*treeScale,z+1.000180*treeScale])
			writtenTrees = writtenTrees + 1
		i = i + 1

#Assembling the entire file
cityJSONRoot["CityObjects"] = cityJSONObjects
cityJSONRoot["vertices"] = cityJSONVertices

#Path to write to, overwritten if there already
outPath = path + ".json"

#Open write, write, close write
write = open(outPath,"w")
write.write(json.dumps(cityJSONRoot,indent=1))
write.close()

#Print some stats.
print("Processed a total of " + str(i-1) + " objects.")
print("Wrote out a total of " + str(writtenTrees) + " points.")