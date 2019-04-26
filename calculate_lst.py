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
from landsatxplore.earthexplorer import EarthExplorer
import os


site_id = str(129)


api = api("skylinegis","pepsiav123pepsiav123")

dataset = "LANDSAT_8_C1"

latitude, longitude =  33.8722886, -112.29446 


start_date = "2019-01-01"
end_date = "2019-04-04"
months='04'

max_cloud_cover=None

path = os.chdir("/mnt/c/Users/avaro/Desktop/LST/" + site_id + "/")
user = "skylinesgis"
pass = "pepsiav123pepsiav123"

scenes = api.search( dataset, latitude=latitude, longitude=longitude, bbox=None,  start_date=start_date, end_date=end_date, max_cloud_cover=max_cloud_cover, months=months, max_results=2)

print('{} scenes found.'.format(len(scenes)))
    
dl = Download(download_dir=path + "output\\")],usgs_user=user,usgs_pass=pass)
for scene in scenes:
	    
    print(scene['downloadUrl'])

    #dl.fetch(url=scene['downloadUrl'],path=path)
    dl.usgs_eros(scene=scene,path=path)
# ee = EarthExplorer(username, password)ee.logout()


# ee.download(scene_id='LT51960471995178MPS00', output_dir='./data')

api.logout()


#Define Path to AOI
path_aoi = path + "aoi.shp"

#Define path to landcover
path_lc = path + "lc.tif"



# Set mapset parameter
mapset = Mapset()
#print mapset

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
# g.remove type=raster,vector pattern=* -f
