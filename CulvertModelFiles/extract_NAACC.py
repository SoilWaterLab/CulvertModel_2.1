##  Extract update for NAACC data format
# Created by Jo Archibald, Dec 2018 (jaa78@cornell.edu)

# Input: Field data csv downloaded from the NAACC database
# Make sure data file is saved in folder of same name
    #  e.g. ALB/ALB.csv
# Outputs: Culvert script input

##  This is a re-write of the extract.py file, created by David Gold, Aug 14,2015
# Updates: Keeps survey ID with field data file
# Reads in data based on column names OR numbers


ws_name=raw_input("Enter the name of your data folder:")
raw_data = "../" + ws_name + "/" + ws_name + ".csv"  # Edited for new file setup Jan 2019
INDEXinfo = raw_input("Column placement follows the original instructions?")
    # If no, we expect the names to match exactly, but placement doesn't matter

import numpy, os, re, csv
import pandas as pd

CD = pd.read_csv(raw_data,sep = ',', header=0)


## If using index numbers
if INDEXinfo == "Y" or INDEXinfo == "y" or INDEXinfo == "yes":
	FieldData = CD.iloc[:,(0,35,20,19,26,49,22,44,47,43,27,61,39,55,58,54,11,8,24)].copy()
else:  # Else read in using the column names
	FieldData = CD[['Survey_Id','Naacc_Culvert_Id','GIS_Latitude','GIS_Longitude','Road','Material','Inlet_Type','Inlet_Structure_Type','Inlet_Width','Inlet_Height','Road_Fill_Height','Slope_Percent','Crossing_Structure_Length','Outlet_Structure_Type','Outlet_Width','Outlet_Height','Crossing_Type','Crossing_Comment','Number_Of_Culverts']].copy()


# OLD headers! 
# FieldData.columns= ('Survey_ID', 'NAACC_ID', 'Lat', 'Long', 'Road_Name', 'Culv_material', 'Inlet_type','Inlet_Shape', 'Inlet_A', 'Inlet_B', 'HW', 'Slope' ,'Length', 'Outlet_shape', 'Outlet_A','Outlet_A','Crossing_Type', 'Comments', 'Flags')  
FieldData.columns= ('Survey_ID', 'NAACC_ID', 'Lat', 'Long', 'Rd_Name','Culv_Mat','In_Type','In_Shape','In_A','In_B','HW','Slope','Length','Out_Shape','Out_A','Out_B','Crossing_Type','Comments','Flags')  
# Inlet_Structure_Type --> In_Shape
# Inlet_Type --> In_Type
# 'Number_Of_Culverts' --> Flags - previously set to 0 if # culverts = 1
FieldData.loc[:,'Modeling_notes'] = numpy.nan  

NotExtracted = pd.DataFrame(columns = ['Survey_ID', 'NAACC_ID', 'Lat', 'Long', 'Rd_Name','Culv_Mat','In_Type','In_Shape','In_A','In_B','HW','Slope','Length','Out_Shape','Out_A','Out_B','Crossing_Type','Comments','Flags','Modeling_notes'])

len(FieldData) # 136

#Remove rows that are Bridge or other crossing type
NotExtracted = NotExtracted.append(FieldData.loc[(FieldData['Crossing_Type']=='Bridge') & (FieldData['In_Shape']!="Box/Bridge with Abutments") & (FieldData['In_Shape']!="Open Bottom Arch Bridge/Culvert")])
FieldData = FieldData.loc[-((FieldData['Crossing_Type']=='Bridge') & (FieldData['In_Shape']!="Box/Bridge with Abutments") & (FieldData['In_Shape']!="Open Bottom Arch Bridge/Culvert"))]


NotExtracted = NotExtracted.append(FieldData.loc[(FieldData['Crossing_Type']=='Bridge') & (FieldData['In_A']>=20)])
FieldData = FieldData.loc[-((FieldData['Crossing_Type']=='Bridge') & (FieldData['In_A']>=20))]

NotExtracted['Modeling_notes'] = "Wrong bridge type or bridge wider than 20 ft"

# Convert inlet type to language accepted by capacity_prep script
FieldData.loc[FieldData['In_Type'] == "Headwall and Wingwalls",'In_Type'] =  "Wingwall and Headwall"
FieldData.loc[FieldData['In_Type'] == "Wingwalls",'In_Type'] =  "Wingwall"
FieldData.loc[FieldData['In_Type'] == "None",'In_Type'] =  "Projecting"

# Convert culvert shape to language accepted by capacity_prep script
FieldData.loc[FieldData['In_Shape'] == 'Round Culvert', 'In_Shape'] =  'Round'
FieldData.loc[FieldData['In_Shape'] == 'Pipe Arch/Elliptical Culvert', 'In_Shape'] =  'Elliptical'
FieldData.loc[FieldData['In_Shape'] == 'Box Culvert', 'In_Shape'] =  'Box'
FieldData.loc[FieldData['In_Shape'] == 'Box/Bridge with Abutments', 'In_Shape'] =  'Box'
FieldData.loc[FieldData['In_Shape'] == 'Open Bottom Arch Bridge/Culvert', 'In_Shape'] =  'Arch'


# >>> CD.columns[44]  = 'Inlet_Structure_Type'


#  Remove rows that contain unrealistic geometry, put in NotExtracted
NotExtracted = NotExtracted.append(FieldData.loc[-((FieldData['In_A']>=0) & (FieldData['In_B']>=0) & (FieldData['HW']>=0) & (FieldData['Length']>=0))])
NotExtracted.loc[pd.isnull(NotExtracted['Modeling_notes']), 'Modeling_notes'] = 'Negative or missing culvert geometry'

FieldData = FieldData.loc[(FieldData['In_A']>=0) & (FieldData['In_B']>=0) & (FieldData['HW']>=0) & (FieldData['Length']>=0)]  # 132

# Assign the Barrier ID, after all the unmodelable rows are removed
# UPDATED Jan 2018 - in case watershed name is longer than 3 characters, the ID still needs only 3
FieldData = FieldData.assign(BarrierID = [str(i+1) + ws_name[:3].upper() for i in range(len(FieldData))])


# Re-assign the number of culverts for each crossing location based on how many culverts were kept
for SI in FieldData.loc[FieldData['Flags']>1]['Survey_ID'].unique():
	NC = FieldData.loc[FieldData['Survey_ID'] == SI]['Survey_ID'].count() # Number of culverts we will model at site
	ONC = FieldData.loc[FieldData['Survey_ID'] == SI]['Flags'].max() # Number culverts noted at site
	print NC
	print ONC
	if NC <> ONC:
		FieldData.loc[FieldData['Survey_ID'] == SI, 'Modeling_notes'] = "Not all culverts modeled at crossing. Started with " + str(ONC)
	FieldData.loc[FieldData['Survey_ID'] == SI, 'Flags'] = NC




# Put the output files in the data folder you created
output_file=ws_name+"/"+ws_name+"_field_data.csv"
not_extracted_file=ws_name+"/"+ws_name+"_not_extracted.csv"
    
FieldData.NAACC_ID = FieldData.NAACC_ID.astype(int)   ##   Converts FieldData to int type after invalid rows removed
FieldData.to_csv("../" + output_file, index=False)
NotExtracted.to_csv("../" + not_extracted_file, index=False)

## Notify user that the extraction is complete
print '\nExtraction complete! Extracted values can be found here:'
print os.getcwd()[:-18] + '/' + output_file + '\n'    
print 'Crossings excluded from analysis can be found here:'
print os.getcwd()[:-18] + '/' + not_extracted_file

