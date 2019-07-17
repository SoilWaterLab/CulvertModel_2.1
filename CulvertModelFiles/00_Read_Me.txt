Python Files and ArcToolbox required for Cornell Culvert Model V2.1
July 2019 
Contacts: 
Jo Archibald (jaa78@cornell.edu)
Todd Walter (mtw5@cornell.edu)

Python Files and ArcToolbox all saved here, no need to recopy for each model run.
Python script requires that file structure will be:
Culvert Model Run folder --> CulvertModelFiles
			--> Data folder --> GIS_files --> DEMs, Temp, WS_Poly, All_Culverts_Shapefile, ArcMap file, OPTIONAL Precip folder if using NOAA rasters
					--> NAACC precip csv files (OR use NOAA)
					--> Model output folder
Note - multiple data folders can be housed within the larger Culvert Run folder, with any edits made to the python/GIS files applying for all datasets.
Python script files need to be told the "Data folder" name, and assumes the csv files also include that name.

ArcToolbox Models:
00_clip_files
00_clipP *(Only needed if using NOAA raster Precip files)
01_Culvert_Watershed_Model
02_Add_Precip *
03_Region *
31_NOAA_Precip *
93_Model_WS_delin
94_append WS
95_Tc_calc
96_CN_calc
98_Model_CreateWS
99_Add_Fields

Python Files:
capacity
capacity_prep
Culvert_Eval
extract_NAACC
final_output
loader
Precip_Append
return_periods
runoffP
sorterPrecip



