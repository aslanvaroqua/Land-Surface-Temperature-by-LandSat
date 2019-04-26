#!/usr/bin/env python2

# Install i.landsat8.swlst via the installer

# Import Libraries
import glob
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules import Module
from grass.script import setup as gsetup
from grass.pygrass.gis import Mapset
import grass.script as grass 
from landsat.downloader import Downloader as dl
import landsatxplore
from landsatxplore.api import API as api
from landsatxplore.earthexplorer import EarthExplorer as ee
import os, sys
import subprocess
site_id = sys.argv[0]


dataset = "LANDSAT_8_C1"

latitude, longitude =  sys.argv[1], sys.argv[2]


start_date = sys.argv[3]
end_date = None
months=None

max_cloud_cover=None

path = "/mnt/c/Users/avaro/Desktop/LST/" + site_id + "/"
user = "skylinegis"
pw = "pepsiav123pepsiav123"
api = api(user,pw)

# scenes = api.search( dataset, latitude=latitude, longitude=longitude, bbox=None,  start_date=start_date, end_date=end_date, max_cloud_cover=max_cloud_cover, months=months, max_results=2)
scenes = api.search( dataset, latitude=latitude, longitude=longitude,max_cloud_cover=max_cloud_cover, months=months)

print('{} scenes found.'.format(len(scenes)))
api.logout()

#init downloader
downloader = ee(user, pw)

# entity id of latest
print(scenes[0]['entityId'])

# download & persist
downloader.download(scenes[0]['entityId'],path)

#close session
downloader.logout()

#Define Path to AOI
path_aoi = path + "aoi.shp"

#Define path to landcover
path_lc = path + "lc.tif"

# Set mapset parameter for GRASS GIS
mapset = Mapset()
#print mapset

process = Popen(['tar','-xhf', scenes[0]['displayId'] + ".tar.gz"], stdout=PIPE, stderr=PIPE)
stdout,stderr = process.communicate()
print(stdout)
print(stderr)

# Look up B10 and B11 TIF-files in dir + subdirs and write path/filename to "files"
files = glob.glob(path + '/*B[1][0-1].TIF')

# Look up BQA TIF-files in dir + subdirs and write path/filename to "files_temp"
files_bqa = glob.glob(path + '/*BQA.TIF')

# Create list with B10 only (for lst creation)
files_b10 = glob.glob(path + '/*B[1][0].TIF')

# Add "files_temp" to "files"
files.extend(files_bqa)

# Import AOI from file
Module("v.import",
    overwrite = True,
    input= path_aoi, 
    output="aoi")

# Set AOI as Region
Module("g.region",
    overwrite = True, 
    vector="aoi@"+str(mapset)

# Import each file "LC08xxxxxxxxxxxx"
for i in files:
    Module("r.import",
       overwrite = True, 
       memory = 2000,
       input = i,
       output = i[-28:-4],
	extent = "region")

# Import landcover map
Module("r.import",
       overwrite = True, 
       memory = 2000,
       input = path_landcover,
       output = "landcover", extent = "region")

# Apply LST-Skript and export TIFs
for i in files_bqa:
	Module("i.landsat8.swlst", 
		overwrite = True, 
		mtl= i[0:len(i)-7]+"MTL.txt",
		b10=i[-28:-7]+ "B10@" + str(mapset),
		b11=i[-28:-7]+"B11@" + str(mapset),
		qab=i[-28:-4]+ "@" + str(mapset),
		landcover="landcover@"+str(mapset),
		lst=i[-28:-7]+"_LST")
       
   	Module("r.out.gdal",
		flags = "f",
		overwrite = True,
		input= i[-28:-7]+"_LST@" + str(mapset),
		output= path_output + i[-28:-7]+"_LST.TIF",
		format="GTiff",
		type="UInt16",
		nodata=9999)

# Remove everything (does not delete files, only maps)
g.remove type=raster,vector pattern=* -f
