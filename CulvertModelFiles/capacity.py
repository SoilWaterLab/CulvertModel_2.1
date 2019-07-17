# Culvert capacity model
# Becky Marjerison
# Oct 10 2013
#
# Updated by David Gold
# July 8 2015
#
# Updated by Noah Warnke
# August 31 2016 (no formulas changed).
#
# Some comments added by Tanvi Naidu June 13 2016
#
# Calculate the capacity of a culvert under inlet control
#
# Inputs: filename for the culv_geom csv, filename to write output to.

import numpy, os, re, csv, loader
#Imports required packages and modules and the function 'loader' which was written
# in 2016 and saved as loader.py
#(loader organizes the data from input file based on headers defined in a signature)

def inlet_control(culvert_geometry_filename, output_filename):


    #csv_writer.writerow(['BarrierID', 'NAACC_ID', 'Lat', 'Long', 'HW_m', 'xArea_sqm', 'length_m', 'D_m', 'c', 'Y', 'ks', 'Culvert_Sl', 'Comments', 'Flags'])

    # Signature for incoming geometry file.
    # This creates a list of dictionaries that stores the relevant headers of
    # the input file and the type of data in the column under that header
    geometry_signature = [
        {'name': 'BarrierID', 'type': str},
        #eg: The first element of the list 'geometry_signature' is a dictionary for barrier id.
        #'BarrierID' is the header of a column of data we want to extract from the input file,containing
        #data of type strings
        {'name': 'Survey_ID', 'type': int},
        {'name': 'NAACC_ID', 'type': int},
        {'name': 'Lat', 'type': float},
        {'name': 'Long', 'type': float},
        {'name': 'HW_m', 'type': float}, 
        {'name': 'xArea_sqm', 'type': float}, 
        {'name': 'length_m', 'type': float}, # Length of culvert under road meters
        {'name': 'D_m', 'type': float}, 
        {'name': 'c', 'type': float},
        {'name': 'Y', 'type': float},
        {'name': 'ks', 'type': float},
        {'name': 'Culvert_Sl', 'type': float},
        {'name': 'Field_Comments', 'type': str},
        {'name': 'Model_Notes', 'type': str},
        {'name': 'Flags', 'type': int}
    ]

    # Load and validate geometry data.
    # geometry_data will now store the relevant data from the culvert geometry input file
    # in the format described in loader.py using the signature defined above.
    # valid_rows will store all value for the key 'valid_rows' in the dictionary geometry_data
    geometry_data = loader.load(culvert_geometry_filename, geometry_signature, 1, -1)
    valid_rows = geometry_data["valid_rows"]

    # Go through each culvert and calculate capacity.
    output_data = []
    for culvert in valid_rows:
        # Get values needed in computation of capacity.
        # constants c, Y, Ks tabulated, depend on entrance type, from FHWA engineering pub HIF12026, appendix A
        Culvert_Area = culvert['xArea_sqm'] # Calculated in input data prep script sq. meter
        HW = culvert['HW_m'] # Hydraulic head above the culvert invert, meters
        D = culvert['D_m'] # Diameter or dimension b, (height of culvert) meters
        Y = culvert['Y']
        Ks = culvert['ks'] # -0.5, except where inlet is mitered in which case +0.7
        S = culvert['Culvert_Sl'] # meter/meter
        c = culvert['c']
        
        Ku = 1.811 # adjustment factor for units (SI=1.811)
              
        # Calculate capacity for the culvert and store with the rest of the data for that culvert.
        culvert['Qc'] = (Culvert_Area * numpy.sqrt(D * ((HW / D) - Y - Ks * S) / c)) / Ku 
        # Culvert eqn from FHWA Eqn A.3, pg 191
        #Culvert capacity submerged outlet, inlet control (m^3/s)

    # Now produce output data using this.
    output_data = []

    num_culverts = len(valid_rows)
    cur_culvert_index = 0

    # Use a while loop instead of "culverts in valid_rows" because we need to skip some due to multiple-culverts-in-one-spot.
    while cur_culvert_index < num_culverts:
        culvert = valid_rows[cur_culvert_index]
        num_culverts_here = culvert['Flags'] 
        if num_culverts_here == 0:
            num_culverts_here = 1 # Confusingly, Flags = 0 used to mean 1 culvert, and 2+ to mean 2+ culvert
                                    # Fixed in extract, but keeping for now in case there are relics elsewhere

        # Sum together the capacities of the set of culverts at the given spot, and skip processing the latter ones after the first one (that being the representative culvert?)
        # If there is just a single culvert (Flags = 0), this simply gets the Qc value for that culvert.
        Qf = 0
        for offset in range (0, num_culverts_here):
            Qf += valid_rows[cur_culvert_index + offset]['Qc'] #This only works if the flagged culverts are appropriately grouped together in the culv_geom.csv (i.e. the second and third culvert at a crossing appear in the two rows below the first culvert. Data often, but not always, is pre-packaged this way. Culverts at the same crossing usually share the same SurveyIDs, but have different (and not alwyas adjacent) NAACC_IDs. To fix this, we'll first have to do an array sort by both lat and long, and then fill in flags where culvert collectors left them out. We should also address this data collection issue with Andrew.  
        cur_culvert_index += num_culverts_here

        # Compose the output data list.
        # Qf is culvert capacity under inlet control
        output_data.append([culvert['BarrierID'], culvert['NAACC_ID'], culvert['Survey_ID'], culvert['Lat'], culvert['Long'], Qf, culvert['Flags'], culvert['Model_Notes'], culvert['Field_Comments'], culvert['xArea_sqm']])

    # Finally, save output data.
    with open(output_filename, 'wb') as output_file:
        csv_writer = csv.writer(output_file)

        # Header
        csv_writer.writerow(['BarrierID','NAACC_ID', 'Survey_ID', 'Lat','Long','Q','Flags','Model_Notes','Field_Comments','Culvert_Area'])

        # Each row.
        for result in output_data:
            csv_writer.writerow(result)
