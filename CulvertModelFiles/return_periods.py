# Culvert max return periods
# Jo Archibald, January 2019
# Building on file created by David Gold, 2015
	# Edits made by Noah Warnke 2016, Lisa Watkins 9/15/2016
	# Tanvi Naidu 6/14/2017
#
# Given culvert capacity and peak discharge from storm events, determine the
# highest return period storm that a culvert can pass for current and future rainfall conditions.
# Produces summary output file with all model results for culverts

import numpy, os, re, csv, loader

def return_periods(capacity_filename, current_runoff_filename, future_runoff_filename, return_periods_output_filename, final_output_filename):

    # 1st Signature: Runoff signature:
    # This creates a list of dictionaries that stores the relevant headers of
    # the input file and the type of data in the column under that header
    runoff_signature = [
        {'name': 'BarrierID', 'type': str},
        #eg: The first element of the list 'runoff_signature' is a dictionary for barrier id.
        #'BarrierID' is the header of a column of data we want to extract from the input file,containing
        #data of type strings
        {'name': 'Area_sqkm', 'type': float},
        # Later: NEW_Lat, NEW_Long
        {'name': 'Tc_hr', 'type': float},
        {'name': 'CN', 'type': float},
        {'name': 'Y1', 'type': float},
        {'name': 'Y2', 'type': float},
        {'name': 'Y5', 'type': float},
        {'name': 'Y10', 'type': float},
        {'name': 'Y25', 'type': float},
        {'name': 'Y50', 'type': float},
        {'name': 'Y100', 'type': float},
        {'name': 'Y200', 'type': float},
        {'name': 'Y500', 'type': float}
    ]

    # 2nd Signature: Culvert signature:
    culvert_signature = [
        {'name': 'BarrierID', 'type': str},
        {'name': 'NAACC_ID', 'type': int},
        {'name': 'Lat', 'type': float},
        {'name': 'Long', 'type': float},
        {'name': 'Q', 'type': float},
        {'name': 'Flags', 'type': int},
        {'name': 'Comments', 'type': str},
        {'name': 'Culvert_Area', 'type': float},
    ]

    # Load and validate current and future runoffs:
    # current_runoff_data will now store the relevant data from the current runoff input file
    # in the format described in loader.py using the first signature defined above.
    # valid_rows will store all value for the key 'valid_rows' in the dictionary current_runoff_data

    current_runoff_data = loader.load(current_runoff_filename, runoff_signature, 1, -1)
    current_runoff_rows = current_runoff_data['valid_rows']

    future_runoff_data = loader.load(future_runoff_filename, runoff_signature, 1, -1)
    future_runoff_rows = future_runoff_data['valid_rows']

    # Create lookup dictionaries for the runoffs. This speeds matching culverts to watersheds up quite a bit.
    current_runoff_lookup = {}
    for watershed in current_runoff_rows:
        current_runoff_lookup[watershed['BarrierID']] = watershed

    future_runoff_lookup = {}
    for watershed in future_runoff_rows:
        future_runoff_lookup[watershed['BarrierID']] = watershed
    
    # Load culvert capacities:
    culvert_data = loader.load(capacity_filename, culvert_signature, 1, -1)
    culvert_rows = culvert_data['valid_rows']

    # A list of the years.
    years = [0, 1, 2, 5, 10, 25, 50, 100, 200, 500]

    # A helper function to find the first overflow.
    def find_first_overflow(culvert, watershed, years):
        capacity = culvert['Q']
        #stores the max flow in culvert as 'capacity' 
        i = 1
        while i < len(years):
            year = years[i]
            #loops through all the relevant return periods
            if capacity < watershed['Y' + str(year)]:
                return years[i - 1]
            #if capacity is lower than the runoff for a particular return period,
            # return the previous highest return period. 
            i += 1
        return years[i - 1]
    
    # Compute which return period each culvert will be able to withstand.
    for culvert in culvert_rows:
        # Find the corresponding current and future watersheds (they share BarrierID):
        culvert['watershed'] = None
        try:
            current_watershed = current_runoff_lookup[culvert['BarrierID']]
            future_watershed = future_runoff_lookup[culvert['BarrierID']]

            culvert['current_return'] = find_first_overflow(culvert, current_watershed, years)
            #returns the highest withstandable return period for current storm data
            culvert['future_return'] = find_first_overflow(culvert, future_watershed, years)
            #returns the highest withstandable return period for future storm data
            culvert['watershed'] = current_watershed # Also save the watershed info, since we'll want it for our final output.
            if culvert['Flags'] == 0:
                culvert['Flags'] = 1 # Also fix flags so it means number of culverts (previously, flag '0' meant 1 culvert)
        except KeyError:
            print "Did not find watershed for barrierID " + culvert['BarrierID']
            # Did not find a watershed corresponding to this culvert in the runoffs. Skip.
            # TODO export skipped culverts.
            continue



    # Just save the return periods.
    with open(return_periods_output_filename, 'wb') as return_output_file:
        csv_writer = csv.writer(return_output_file)

        # Header
        csv_writer.writerow(['BarrierID','Current Max Return (yr)','Future Max Return (yr)'])

        # Each row.
        for culvert in culvert_rows:
            watershed = culvert['watershed']
            if watershed == None:
                continue # Skip all the culverts we couldn't match with watersheds.
            csv_writer.writerow([culvert['BarrierID'], culvert['current_return'], culvert['future_return']])
        


    # Now save all the final data (easier to do that here since all the relevant files are already open.)
    with open(final_output_filename, 'wb') as final_output_file:
        csv_writer = csv.writer(final_output_file)

        # Header
        csv_writer.writerow(['BarrierID', 'NAACC_ID', 'Original Latitude', 'Original Longitude', 'Current Max Return Period (yr)', 'Future Max Return Period (yr)', 'Capacity (m^3/s)', 'Cross sectional Area (m^2)', 'WS Area (sq km)', 'Tc (hr)', 'CN', 'Number of Culverts', 'Comments'])  
        # Removed ['Point Moved', 'New Latitude', 'New Longitude'] columns

        # Each row.
        for culvert in culvert_rows:
            watershed = culvert['watershed']
            if watershed == None:
                print "Skipping culvert " + culvert['BarrierID']
                continue # Skip all the culverts we couldn't match with watersheds.
            csv_writer.writerow([
                culvert['BarrierID'], \
                culvert['NAACC_ID'], \
                culvert['Lat'], \
                culvert['Long'], \
                # "?", \
                # "?", \
                # "?", \
                culvert['current_return'], \
                culvert['future_return'], \
                culvert['Q'], \
                culvert['Culvert_Area'], \
                watershed['Area_sqkm'], \
                watershed['Tc_hr'], \
                watershed['CN'], \
                culvert['Flags'], \
                culvert['Comments']
            ])

