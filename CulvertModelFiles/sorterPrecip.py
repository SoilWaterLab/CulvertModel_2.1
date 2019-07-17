# Sorter.py
# David Gold
# November 6, 2015
#
#Edited by Noah
# Some comments added by Tanvi Naidu 6/13/2017
# This script will sort the ws data exported from GIS by ID number
# Edited 5/31/2019 by Jo to allow precipitation inputs for each watershed

import csv, sys, operator, numpy, loader
#Imports required packages and modules (numpy, os, re, csv) and the function loader
# which was written in 2016 and saved as loader.py
#(loader organizes the data from input file based on headers defined in a signature)

def sort(watershed_data_input_filename, county_abbreviation, output_filename):

    # Define signature for input file.
    # This creates a list of dictionaries that stores the relevant headers of
    # the input file and the type of data in the column under that header

    watershed_data_signature = [
        {'name': 'BarrierID', 'type': str},
        {'name': 'Area_sqkm', 'type': float},
        {'name': 'Tc_hr', 'type': float},
        {'name': 'CN', 'type': float},
        {'name': 'P1', 'type': float},
        {'name': 'P2', 'type': float},
        {'name': 'P5', 'type': float},
        {'name': 'P10', 'type': float},
        {'name': 'P25', 'type': float},
        {'name': 'P50', 'type': float},
        {'name': 'P100', 'type': float},
        {'name': 'P200', 'type': float},
        {'name': 'P500', 'type': float},
        {'name': 'Region', 'type': float}
    ];

    # Load data.
    # watershed_data will now store the relevant data from the watershed data input file
    # in the format described in loader.py using the signature defined above.
    # valid_watersheds will store all value for the key 'valid_rows' in the dictionary watershed_data
    
    watershed_data = loader.load(watershed_data_input_filename, watershed_data_signature, 1, -1)
    valid_watersheds = watershed_data['valid_rows']

    # If there were invalid watershed rows, make a note but continue on.
    num_invalid_rows = len(watershed_data['invalid_rows']) 
    if num_invalid_rows > 0:
        print "* Note: there were " \
            + str(num_invalid_rows) \
            + " invalid rows in the watershed data. Continuing with the " \
            + str(len(valid_watersheds)) \
            + " valid rows."

    # Strip 'their' county abbreviation off the BarrierID string and cast to int, e.g., '10cmbws' -> 10
    id_suffix_len = 5  # Removes WS abbr. and ws 
   
    for watershed in valid_watersheds:
        barrier_id = watershed['BarrierID']
        watershed['BarrierID'] = int(barrier_id[:len(barrier_id) - id_suffix_len])
    
    # Sort the valid watersheds by this BarrierID number.
    def get_id(row):
        return row['BarrierID']
    valid_watersheds = sorted(valid_watersheds, key = get_id, reverse = False)

    # Write the sorted data to a new csv file.
    with open(output_filename, 'wb') as output_file:
        output_writer = csv.writer(output_file)

        # Header.
        output_writer.writerow(['BarrierID','Area_sqkm','Tc_hr','CN', 'P1', 'P2','P5', 'P10','P25', 'P50','P100', 'P200', 'P500', 'Region'])
    
        # Row for each watershed.
        for watershed in valid_watersheds:
            output_writer.writerow([
                str(watershed['BarrierID']) + county_abbreviation,
                watershed['Area_sqkm'],
                watershed['Tc_hr'],
                watershed['CN'],
                watershed['P1'],
                watershed['P2'],
                watershed['P5'],
                watershed['P10'],
                watershed['P25'],
                watershed['P50'],
                watershed['P100'],
                watershed['P200'],
                watershed['P500'],
                watershed['Region']
            ])

    # File automatically closed by 'with'.
