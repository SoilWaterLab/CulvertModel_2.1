# Runoff calculation model
# David Gold
# August 2015
#
# Edited by Jo Archibald January 2019 to produce a skipped-watershed file
#   edited 5/30/2019 in order for each watershed to have their own precip inputs
# Based off of the runoff model created by Rebecca Marjerson in 2013
#
# Determine the runoff peak flow using the SCS curve number method (see TR-55 document for further details)
# 
# Inputs:   culvert_Q_input.csv: culvertID, watershed area (sq km), average curve number, time of concentration (hr)
#           ws_precip: csv file exported from the Cornell NRCC of 24 hour storms with return periods 1 to 500 years
#           rainfall_adjustment: scalar, with 1 as current rainfall.
#           output_filename: where to save the results of the runoff calculation.
#
# Outputs:  table of runoff (q_peak) in cubic meters per second for each return periods under current precipitation conditions
#           table of runoff (q_peak) in cubic meters per second for each return periods under future precipitation conditions

import numpy, pandas, os, re, csv, sys, loader


def calculate(sorted_filename, rainfall_adjustment, output_filename, skipped_filename = False,
              SSA = True, IntermediateFiles = False, SSF = False):   # Still need to add these parameters into the function
    # Precipitation values (mm, converted to cm) are average for each watershed from NOAA Atlas 14
    # 1yr,2yr,5yr,10yr,25 yr,50 yr,100yr,200 yr,500 yr storm

    # Define signature for sorted watershed data input file.
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

    # Load and validate watershed data.
    watershed_data = loader.load(sorted_filename, watershed_data_signature, 1, -1)
            #Header in row 1, and we want to read all rows (max rows= -1)
    valid_watersheds = watershed_data['valid_rows']

    # Run the calculation for each watershed and each precipitation:
    results = []
    skipped_watersheds = []
    SSA_Qs = []

    # Intermediate results only used if IntermediateFiles == True
    results2 = []
    results3 = []
    results_precip = []

    for watershed in valid_watersheds:

        #Store our watershed values in handy variables for calculations (from watershed dictionary)
        BarrierID = watershed['BarrierID']
        ws_area = watershed['Area_sqkm'] #sq km, calculated with ArcGIS tools 
        tc = watershed['Tc_hr'] #time of concentration in hours, calculated by ArcGIS script
        CN = watershed['CN'] #area-weighted average curve number
        Region = watershed['Region']
        P = numpy.array([watershed['P1'], watershed['P2'], watershed['P5'],
                        watershed['P10'], watershed['P25'], watershed['P50'],
                        watershed['P100'], watershed['P200'], watershed['P500']
                         ])*rainfall_adjustment/10
            # NOAA Atlas 14 precip values are in mm, converted to cm here, also increased by 15% for future precip.

        # Skip over watersheds where curve number or time of concentration 
        # are 0 or watershed area < 0.01, since this indicates invalid data.
        # Note that this results in output files with potentially fewer 
        # watersheds in them than in the input file.
        if CN == 0:
            Modeling_notes = "CN = 0"
            skipped = [BarrierID, ws_area, tc, CN, Modeling_notes]
            skipped_watersheds.append(skipped)
            continue

        if tc == 0:
            Modeling_notes = "Tc_hr = 0"
            skipped = [BarrierID, ws_area, tc, CN, Modeling_notes]
            skipped_watersheds.append(skipped)
            continue

        if  ws_area < 0.01:
            Modeling_notes = "Area_sqkm < 0.01"
            skipped = [BarrierID, ws_area, tc, CN, Modeling_notes]
            skipped_watersheds.append(skipped)
            continue
            
        # calculate storage, S  and Ia in cm
        Storage = 0.1 * ((25400.0 / CN) - 254.0) #cm
        Ia = 0.2 * Storage #inital abstraction, amount of precip that never has a chance to become runoff (cm)
    
        # calculate depth of runoff from each storm
        # if P < Ia NO runoff is produced
        # Note that P is a vector of the 9 values, so everything hereafter is too.
        Pe = (P - Ia) #cm
        Pe = numpy.array([0 if i < 0 else i for i in Pe]) # get rid of negative Pe's
        Q = (Pe ** 2) / (P + (Storage - Ia)) #cm

        
        #calculate q_peak, cubic meters per second
        # q_u is an adjustment based on Tc.
        # The relationship was found by Jo Archibald 2019
        # Note - the relationship for return interval = 1 year is derived from 2-year information
            # the 1-year results were unreliable from USGS data-derived P-3 curves

        # keep rain ratio within limits set by TR55
        #Calculated
        Const0 = numpy.array([2.798, 2.798, 3.225, 3.529, 3.932, 4.244, 4.57, 4.914, 5.403])
        Const1 = numpy.array([0.367, 0.367, 0.481, 0.559, 0.658, 0.733, 0.81, 0.888, 0.996])

        qu = (Const0 - Const1 * tc)/8.64
        # qu would have to be m^3/s per km^2 per cm :
        # / 8.64 creates those units from a unitless value

        q_peak = Q * qu * ws_area #m^3/s
        Q_daily = Q * ws_area *10000/(3600*24)   # updated 6/3/2019 for cms units 
        #qu has weird units which take care of the difference between Q in cm and area in km2

        # Optional Stream Stats calculations here (Jo added in June 2019)
        #  further StreamStats regions should be added as needed
        if (SSA == True):
            if (Region == 1):
                CA0 = numpy.array([31.7,38.5,47.6,73,92.1,119,
                                   140,162,186,219])
                CA1 = numpy.array([0.857, 0.848, 0.839, 0.822, 0.813, 0.802,
                                   0.796, 0.790, 0.785, 0.779])
            elif (Region == 2):
                CA0 = numpy.array([43.4,56.1,74.7,139,197,291,
                                   378,480,598,782])
                CA1 = numpy.array([0.772, 0.758, 0.743, 0.712, 0.695, 0.677,
                                   0.666, 0.656, 0.648, 0.638])
            elif (Region == 3):
                CA0 = numpy.array([57.4,71.8,90.8,144,185,249,
                                   304,367,436,539])
                CA1 = numpy.array([0.861, 0.857, 0.85, 0.848, 0.843, 0.84,
                                   0.840, 0.836, 0.832, 0.827])
            elif (Region == 4):
                CA0 = numpy.array([39.1, 48.7, 61.3, 97.4, 124, 161,191, 221, 253, 298])
                CA1 = numpy.array([0.833,0.823,0.812, 0.788, 0.775, 0.761, 0.751, 0.743, 0.735, 0.727])
            elif (Region == 5):
                CA0 = numpy.array([54.8, 71.5, 95.4, 172, 237, 332, 412, 502, 600, 745])
                CA1 = numpy.array([0.800,0.785,0.770, 0.738, 0.722, 0.706, 0.695, 0.687, 0.679, 0.670])
            elif (Region == 6):
                CA0 = numpy.array([31.1, 37.2, 44.5, 62.7, 74.2, 88.4, 98.5, 108, 117, 129])
                CA1 = numpy.array([0.783,0.782,0.782, 0.788, 0.794, 0.801, 0.807, 0.813, 0.818, 0.826])
                # from page 34 of Lumia et al.
            else:
                CA0 = 0
                CA1 = 0
                # Modeling_notes = "StreamStats not modeled"
            SSA_Q = (CA0 * (ws_area/2.59)**CA1)/35.315  # Flow in cms
            Q_ratios = q_peak[1:9]/SSA_Q[2:10]  # Cornell value/SS value
            SSA_Qs.append([BarrierID, ws_area, numpy.mean(Q_ratios), max(Q_ratios), min(Q_ratios), Region]+SSA_Q.tolist())

        ##  More if statements neede here - other regions, and/or full regression equation


        # Convert our vector back to a list and add the other info to the front.
        result = [BarrierID, ws_area, tc, CN] + q_peak.tolist()

        # Lastly, put our result for this watershed into the list of results.
        results.append(result)

        if (IntermediateFiles == True):
            result2 = [BarrierID, ws_area, Storage, CN] + qu.tolist()  # Check qu
            result3 = [BarrierID, ws_area, Storage, CN] + Q_daily.tolist()
            #result_precip = [BarrierID, ws_area, Ia, CN] + Pe.tolist()  # Added 4/1/2019
            result_precip = [BarrierID, ws_area, Ia, CN] + P.tolist()  # Check Rain ratio
            results2.append(result2)
            results3.append(result3)
            results_precip.append(result_precip)


    # Set up to save results to new file.
    with open(output_filename, 'wb') as output_file:
        csv_writer = csv.writer(output_file)
        # Header
        csv_writer.writerow(['BarrierID', 'Area_sqkm', 'Tc_hr', 'CN', 'Y1','Y2','Y5','Y10','Y25','Y50','Y100','Y200','Y500'])
        # Each row.
        # Later: when flags (aka number_of_culverts) is present, skip ahead that number
        # instead of just 1 in the results list (ie, ignore the second, third, etc. culvert.)
        for result in results:
            csv_writer.writerow(result)
    # output_file closed by with

    if (IntermediateFiles == True):  # Intermediate files useful for testing model performance
        with open(output_filename[:-4] + '_Daily.csv', 'wb') as output_file:
            csv_writer = csv.writer(output_file)
            csv_writer.writerow(['BarrierID', 'Area_sqkm', 'S_cm', 'CN', 'Y1','Y2','Y5','Y10','Y25','Y50','Y100','Y200','Y500'])
            for result3 in results3:  # type: object
                csv_writer.writerow(result3)

        with open(output_filename[:-4] + '_qu.csv', 'wb') as output_file:
            csv_writer = csv.writer(output_file)
            csv_writer.writerow(['BarrierID', 'Area_sqkm', 'Ia_cm', 'CN', 'Y1','Y2','Y5','Y10','Y25','Y50','Y100','Y200','Y500'])
            for result2 in results2:
                csv_writer.writerow(result2)

        with open(output_filename[:-4] + '_Precip.csv', 'wb') as output_file:
            csv_writer = csv.writer(output_file)
            csv_writer.writerow(['BarrierID', 'Area_sqkm', 'Ia_cm', 'CN', 'Y1','Y2','Y5','Y10','Y25','Y50','Y100','Y200','Y500'])
            for result_precip in results_precip:
                csv_writer.writerow(result_precip)
        # Added by Jo April 1 2019 to check intermediate output


    # Also save thrown-out watersheds into another file, if there were any.
    if rainfall_adjustment == 1:  # only run first time
        with open(skipped_filename, 'wb') as output_file:
            csv_writer = csv.writer(output_file)
            assert isinstance(csv_writer, object)
            csv_writer.writerow(['BarrierID', 'Area_sqkm', 'Tc_hr', 'CN', 'Modeling_notes'])
            for skipped in skipped_watersheds:
                csv_writer.writerow(skipped)

        if (SSA == True):
            with open(output_filename[:-19] + '_StreamStatsAreaBasedQ_CMS.csv', 'wb') as output_file:
                csv_writer = csv.writer(output_file)
                csv_writer.writerow(['BarrierID', 'Area_sqkm', 'Av_CM_SS_Ratio', 'Max_Ratio', 'Min_Ratio', 'Region', 'Y1.25', 'Y1.5', 'Y2', 'Y5','Y10','Y25','Y50','Y100','Y200','Y500'])
                for SSA_Q in SSA_Qs:
                    csv_writer.writerow(SSA_Q)
