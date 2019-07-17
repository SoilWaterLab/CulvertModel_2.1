# Culvert Capacity input prep script
# David Gold
# June 3 2015
#
# Updated 8/29/2016
# Noah Warnke
#
# Last updated by Lisa Watkins 9/15/2016
#
# Updated by Tanvi Naidu 6/14/2017
# Fixed local variable errors 6/21/2017 Zoya
# Updated by Sharon Zhang 7/20/2017 
#
# This script will take the raw culvert data from the field and
# calculate the area of each culvert based on the shape.
# It will also assign c and y values to each culvert based
# on culvert shape, material and inlet type (from FHWA engineering pub
# HIF12026, appendix A).
#
# Input:  culvert_field_data.csv with the following columns: BarrierID, Field_ID, Lat, Long,
# Rd_Name, Culv_Mat, In_Type, In_Shape, In_A, In_B, HW, Slope, Length, Out_Shape, Out_A, Out_B
# Comments, Flags
#
# Outputs: culvert_capcity_input: a new csv file that contains all necessary
# parameters to run the culvert capacity script.

import numpy, os, re, csv, loader
#Imports required packages and modules and the function loader which was written
# in 2016 and saved as loader.py
#(loader organizes the data from input file based on headers defined in a signature)

#Function for calculations
def geometry(field_data_input_filename, output_filename):

    # Signature for incoming data.
    # This creates a list of dictionaries that stores the relevant headers of
    # the input file and the type of data in the column under that header
    field_data_signature = [
        {'name': 'BarrierID', 'type': str},
        #eg: The first element of the list 'field_data_signature' is a dictionary for barrier id.
        #'BarrierID' is the header of a column of data we want to extract from the input file,containing
        #data of type strings
        {'name': 'Survey_ID', 'type': int},
        {'name': 'NAACC_ID', 'type': int},
        {'name': 'Lat', 'type': float},
        {'name': 'Long', 'type': float},
        {'name': 'Length', 'type': float},
        {'name': 'Slope', 'type': float},
        {'name': 'Comments', 'type': str},
        {'name': 'In_Shape', 'type': str},
        {'name': 'In_A', 'type': float},
        {'name': 'In_B', 'type': float},
        {'name': 'In_Type', 'type': str},
        {'name': 'Culv_Mat', 'type': str},
        {'name':'HW','type':float},
        {'name': 'Modeling_notes', 'type': str},
        {'name': 'Flags', 'type': int}
    ];

    # Load and validate field data.
    # field_data will now store the relevant data from the culvert geometry input file
    # in the format described in loader.py using the signature defined above.
    # valid_rows will store all value for the key 'valid_rows' in the dictionary field_data
    field_data = loader.load(field_data_input_filename, field_data_signature, 1, -1)
    valid_rows = field_data['valid_rows']

    # Modify data.
    output_data = []
    for barrier in valid_rows:

        # assign unchanged values to variables and convert english units to SI
        BarrierID = barrier['BarrierID']
        #eg: stores values for the key 'BarrierID'
        Survey_ID = barrier['Survey_ID']
        NAACC_ID = barrier['NAACC_ID']
        Lat = barrier['Lat']
        Long = barrier['Long']
        length = barrier['Length'] / 3.2808 # converts culvert length from feet to meters
        Culvert_Sl = barrier['Slope'] / 100 # converts slope from percent to meter/meter
        Fcomments = barrier['Comments']  # Comments taken in the field
        Culvert_shape = barrier['In_Shape'] # assigns culvert shape
        A = barrier['In_A'] / 3.2808 # converts A measurement (width) from feet to meters
        comments = barrier['Modeling_notes']  # These are comments generated from Extract and capacity py files

        # if culvert is not round, need B (height), so convert from feet to meters
        if Culvert_shape != "Round":
            B = barrier['In_B'] / 3.2808

        Inlet_type = barrier['In_Type']
        Culvert_material = barrier['Culv_Mat']
        if "Stone" in Culvert_material: # if the word stone exists in the column it is assigned stone
            Culvert_material = "Stone" #Sharon 7/11/17
        Flags = barrier['Flags']
        HW = barrier['HW']
        #Tanvi Naidu (6/16/2017): Changed from 'Out_A' to 'HW'

        # calculate areas and assign D values (culvert depth) based on culvert shape
        if Culvert_shape == "Round":
            xArea_sqm=((A/2)**2)*3.14159 #Area in m^2, thus diameter in m
            D=A # if culvert is round, depth is diameter
        elif Culvert_shape=='Elliptical' or Culvert_shape=='Pipe Arch':
            xArea_sqm=(A/2)*(B/2)*3.14159
            D=B # if culvert is eliptical, depth is B
        elif Culvert_shape=='Box':
            xArea_sqm=(A)*(B)
            D=B # if culvert is a box, depth is B
        elif Culvert_shape=='Arch':
            xArea_sqm=((A/2)*(B/2)*3.14159)/2
            D=B # if culvert is an arch, depth is B

        # Calculate head over invert by adding dist from road to top of culvert to D
        H = HW /  3.2808 + D
        #Tanvi Naidu (6/16/2017): Changed from 'Out_A' to 'HW'

        # assign ks (slope coefficient from FHWA engineering pub HIF12026, appendix A)
        if Inlet_type == 'Mitered to Slope':
            ks=0.7
        else:
            ks=-0.5

        global c #Renders c and y global variables so that they can be accessed outside of their indent levels (i.e. in Ln 199)
        global Y #Renders c and y global variables so that they can be accessed outside of their indent levels (i.e. in Ln 199)

        c=0.04 #Filler value to define c and y before declared global variables (and identify culverts not covered by inlet type and material combinations)  PREVIOUS to 3/18/2019: 0.99 for both...
        Y=0.7 #Filler value to define c and y before declared global variables (and identify culverts not covered by inlet type and material combinations)

        # assign c and y values (coefficients based on shape and material from FHWA engineering pub HIF12026, appendix A)
        # no c and y value provide for inlet_type == "other".  Will take on the filler values
        if Culvert_shape=='Arch':
            if Culvert_material=="Concrete" or Culvert_material=="Stone":
                if Inlet_type=="Headwall" or Inlet_type=="Projecting":
                    c=0.041
                    Y=0.570
                elif Inlet_type=='Mitered to Slope':
                    c=0.040
                    Y=0.48
                elif Inlet_type=='Wingwall':
                     c=0.040
                     Y=0.620
                elif Inlet_type=='Wingwall and Headwall':
                     c=0.040
                     Y=0.620
            elif Culvert_material=="Plastic" or Culvert_material=="Metal":  #inlet_type to Culvert_material for plastic - sharon
                 if Inlet_type=='Mitered to Slope':
                    c=0.0540
                    Y=0.5
                 elif Inlet_type== 'Projecting':
                    c=0.065
                    Y=0.12
                 elif Inlet_type == 'Headwall' or Inlet_type == 'Wingwall and Headwall' or Inlet_type=='Wingwall':
                     c=0.0431
                     Y=0.610
            elif Culvert_material=="Combination":
                     c=0.045   #Changed March 2019 from c=1.0   #filler values -sharon
                     Y=0.5     #Y=1.0    # filler values - sharon
                     comments = "Filler c & Y values. " + comments



        elif Culvert_shape=="Box":
            if Culvert_material=="Concrete" or Culvert_material=="Stone":
                c=0.0378
                Y=0.870
            elif Culvert_material=="Plastic" or Culvert_material=='Metal':
                if Inlet_type=='Headwall':
                    c=0.0379
                    Y=0.690 #put in else statement in case other inlet types exist-Sharon
                elif Inlet_type=='Wingwall':   ## Jo put this in but needs to check...
                     c=0.040
                     Y=0.620
                     comments = "Filler c & Y values. " + comments
                else:
                    c=0.04  # c=1.0
                    Y=0.65 # Y=1.0 #filler numbers -Sharon
                    comments = "Filler c & Y values. " + comments
            elif Culvert_material=='Wood':
                c=0.038
                Y=0.87
            elif Culvert_material== "Combination":
                c=0.038
                Y=0.7   #filler values -Sharon
                comments = "Filler c & Y values. " + comments

        elif Culvert_shape=="Elliptical" or Culvert_shape== 'Pipe Arch':
            if Culvert_material=="Concrete" or Culvert_material=="Stone":
                c=0.048
                Y=0.80
            elif Culvert_material=="Plastic" or Culvert_material=='Metal':
                if Inlet_type== 'Projecting':
                    c=0.060
                    Y=0.75
                else:
                    c=0.048
                    Y=0.80

            elif Culvert_material =="Combination":
                  c=0.05 #c=1.0
                  Y=0.8 #Y=1.0  #filler -Sharon
                  comments = "Filler c & Y values. " + comments

        elif Culvert_shape=="Round":
            if Culvert_material=="Concrete" or Culvert_material=="Stone":
                if Inlet_type== 'Projecting':
                    c=0.032
                    Y=0.69
                else:
                    c=0.029
                    Y=0.74
            elif Culvert_material=="Plastic" or Culvert_material=='Metal':
                if Inlet_type == 'Projecting':
                    c=0.055
                    Y=0.54
                elif Inlet_type =='Mitered to Slope':
                    c=0.046
                    Y=0.75
                else:
                    c=0.038
                    Y=0.69
            elif Culvert_material == "Combination":
                c=0.04 # c=1.0
                Y=0.65 # Y=1.0 #filler-Sharon
                comments = "Filler c & Y values. " + comments


        #all filler values i.e. 1.0 need to be replaced with real values when they can be found. things that cannot be modelled include
        #all combination culvert material types and Box/Plastic or Metal/any other type of Inlet thats not Headwall  - Sharon

        # Add current output row to output_data
        output_data.append([BarrierID, NAACC_ID, Survey_ID, Lat, Long, H, xArea_sqm, length, D, c, Y, ks, Culvert_Sl, Fcomments, Flags, comments])


    # Set up to save results to new file.
    with open(output_filename, 'wb') as output_file:
        csv_writer = csv.writer(output_file)

        # Header
        csv_writer.writerow(['BarrierID', 'NAACC_ID', 'Survey_ID', 'Lat', 'Long', 'HW_m', 'xArea_sqm', 'length_m', 'D_m', 'c', 'Y', 'ks', 'Culvert_Sl', 'Field_Comments', 'Flags', 'Model_Notes'])

        # Each row.
        for row in output_data:
            csv_writer.writerow(row)

