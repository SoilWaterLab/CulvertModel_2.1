import loader
import csv, numpy


def calculate(watershed_data_input_filename, watershed_precip_input_filename, output_filename,  Reg=2):
    precip_data_signature = [
        {'name': '24-hr', 'type': float}
    ];

    watershed_data_signature = [
        {'name': 'BarrierID', 'type': str},
        {'name': 'Area_sqkm', 'type': float},
        {'name': 'Tc_hr', 'type': float},
        {'name': 'CN', 'type': float}
    ];

    watershed_data = loader.load(watershed_data_input_filename, watershed_data_signature, 1, -1)
    #Header in row 1, and we want to read all rows (max rows= -1)
    valid_watersheds = watershed_data['valid_rows']

    # Load precipitation data.
    precip_data = loader.load(watershed_precip_input_filename, precip_data_signature, 10, 9)
     #Header in row 10, and there are 9 rows to read (max rows= 9)
    precip_rows = precip_data['valid_rows']

    # If there is a problem loading the precipitation rows (i.e. less than 9 rows), bail out.
    if len(precip_rows) < 9:
        print "ERROR: failed to load all precipitation data from file '" \
            + watershed_precip_input_filename \
            + "'. Bailing out."
        sys.exit(0)

    # Create list of preciptations, converted to metric and adjusted.
    precips_list = []
    results = []
    for row in precip_rows:
        precips_list.append(row['24-hr'] * 25.4)
        #coverts from inches (nrcc default) to mm.

    # Clever multi-math technique: convert precips list to a vector aka array:
    P = numpy.array(precips_list)

    for watershed in valid_watersheds:
        BarrierID = watershed['BarrierID']
        ws_area = watershed['Area_sqkm'] #sq km, calculated with ArcGIS tools
        tc = watershed['Tc_hr'] #time of concentration in hours, calculated by ArcGIS script
        CN = watershed['CN'] #area-weighted average curve number
            # Reg is NY StreamStats region used to calculated Area-generated SS estimates
        result = [BarrierID, ws_area, tc, CN, Reg] + P.tolist()
        results.append(result)

    with open(output_filename, 'wb') as output_file:
        csv_writer = csv.writer(output_file)

        # Header
        csv_writer.writerow(['BarrierID', 'Area_sqkm', 'Tc_hr', 'CN', 'Region', 'P1','P2','P5','P10','P25','P50','P100','P200','P500'])

        # Each row.
        # Later: when flags (aka number_of_culverts) is present, skip ahead that number
        # instead of just 1 in the results list (ie, ignore the second, third, etc. culvert.)
        for result in results:
            csv_writer.writerow(result)
