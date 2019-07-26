# CulvertModel_2.1
Updated Cornell Culvert Model with a fix for peak flow estimation.

Model originally created by Becky Marjerison and David Gold
Edited by Noah Warnke, Lisa Watkins, Tanvi Naidu, Allison Truhlar

Most recent edits and additions in 2019 by Jo Archibald (jaa78@cornell.edu) 

This model requires ArcGIS 10.3+ (developed on Arc 10.6), and python 2.7 on Windows. 
Instructions for using the model are in CulvertModelFiles/00_Full_Culvert_Instructions_V2.1
Data Access links here: CulvertModelFiles/00_Cornell_Model_Data

Model Updates
1. Developed an empirical relationship between 24-hour CN-derived streamflow, and peak streamflow based on small USGS gauges (<20 square miles) to be used in determining peak flow through culverts.  This addressed the concern that model users were noting unreasonably high flow through their stream crossings, and very low return periods passed.

2. Developed compatibility with NOAA precipitation datasets:  Now allows for NOAA precipitation GIS layers to be used as input, to generate average precipitation for each culvert watershed rather than using one precipitation input for each batch of culverts (usually run at a county level – so previously we assumed precipitation did not vary significantly over the county).  

3. Added the NY-state USGS Area-based Streamstats estimates to the Culvert Model output, to provide a point of comparison to Cornell Model flow estimates for each culvert watershed. Methodology from: Lumia, Richard, Freehafer, D.A., and Smith, M.J., 2006, Magnitude and frequency of floods in New York: U.S. Geological Survey Scientific Investigations Report 2006–5112, 152 p. 

Spatial Data Access for NY State:
https://cornell.box.com/s/ygzkpxtu6doat8hheatjcvmx5nqdkfkq

Video Guides for running the model here: 

1 GetCulvertModel FileStructure: https://youtu.be/K6fkDvqDtVg 

2 Extract Data https://youtu.be/KykXNTjVwT8 

3 Create Shapefiles https://youtu.be/5V5uilhqiSw

4 Set up ArcMap https://youtu.be/ygcNNLZ6a94

5 RunArcModel https://youtu.be/0lIo0O-h7vc

5A NOAA Precip: https://youtu.be/SDokWb8lEws

6 CulvertEval ModelResults: https://youtu.be/JfomAwiDIs4




