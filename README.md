# CulvertModel_2.1
Edits by Jo Archibald (jaa78@cornell.edu)
Updated Cornell Culvert Model with a fix for peak flow estimation.

Model Updates
1. Developed an empirical relationship between 24-hour CN-derived streamflow, and peak streamflow based on small USGS gauges (<20 square miles) to be used in determining peak flow through culverts.  This addressed the concern that model users were noting unreasonably high flow through their stream crossings, and very low return periods passed.

2. Developed compatibility with NOAA precipitation datasets:  Now allows for NOAA precipitation GIS layers to be used as input, to generate average precipitation for each culvert watershed rather than using one precipitation input for each batch of culverts (usually run at a county level – so previously we assumed precipitation did not vary significantly over the county).  

3. Added the NY-state USGS Area-based Streamstats estimates to the Culvert Model output, to provide a point of comparison to Cornell Model flow estimates for each culvert watershed. Methodology from: Lumia, Richard, Freehafer, D.A., and Smith, M.J., 2006, Magnitude and frequency of floods in New York: U.S. Geological Survey Scientific Investigations Report 2006–5112, 152 p. 

Spatial Data Access for NY State:
https://cornell.box.com/s/ygzkpxtu6doat8hheatjcvmx5nqdkfkq
