# Culvert Evaluation Model
# January 2019 
# These scripts are based on the culvert evaluation model developed by Rebecca Marjerison in 2013, and Dave Gold in 2015
#
# This script will:
# 1. Determine the runoff peak discharge of given culvert's watershed using the SCS graphical curve number method.
# 2. Calculate the cross sectional area of each culvert and assign c and Y coefficients based on culvert characteristics
# 3. Determine the maximum capacity of a culvert using inlet control
# 4. Determine the maximum return period storm that the culvert can safely pass before overtopping for both current and
#    future rainfall conditions.
#
# Inputs:
# 1. All_Culverts.csv: A CSV file containing data on culvert watershed characteristics including 
#    Culvert IDs, WS_area in sq km, Tc in hrs and CN

# 2. NRCC export CSV file of precipitation data (in) for the 1, 2, 5, 10, 25, 50, 100, 200 and 500 yr 24-hr storm events
#    The precip for the 1-yr, 24 hr storm event should be in cell K-11
#
# 3. Field data collection input: A CSV file containing culvert data gathered in the field using either then NAACC
#    data collection format or Tompkins county Fulcrum app
#
# Outputs:
# 1. Culvert geometry file: A CSV file containing culvert dimensions and assigned c and Y coefficients
#
# 2. Capacity output: A CSV file containing the maximum capacity of each culvert under inlet control
#
# 3. Current Runoff output: A CSV file containing the peak discharge for each culvert's watershed for
#    the analyzed return period storms under current rainfall conditions
#
# 4. Future Runoff output: A CSV file containing the peak discharge for each culvert's watershed for
#    the analyzed return period storms under 2050 projected rainfall conditions
#
# 5. Return periods output: A CSV file containing the maximum return period that each culvert can
#    safely pass under current rainfall conditions and 2050 projections.
#
# 6. Final Model ouptut: A CSV file that summarizes the above model outputs in one table
print('Cornell Culvert Evaluation Model')
print('--------------------------------\n')

# Importing required packages and modules
import capacity, Precip_Append
import capacity_prep
import os
import final_output
# import runoff
import runoffP  # Produces StreamStats estimates (cms) based on watershed area, and runs using NOAA Atlas 14 Precip
# import sorter
import sorterPrecip
# import csv,  pandas as pd

FileNm = raw_input("Please enter your data file prefix, which should also be your data folder name: \n")
data_path = "../" + FileNm + "/"
PrecipType = raw_input("Did you use NOAA Atlas 14 to get different precip values for each culvert watershed? (y/n) \n")

watershed_data_input_filename = data_path + 'All_Culverts.csv'
watershed_precip_input_filename = data_path + FileNm + '_precip.csv'
field_data_input_filename = data_path + FileNm + '_field_data.csv'
not_extracted_filename = data_path + FileNm + '_not_extracted.csv'

# Create folder and filenames for all of the output files.
OutputDirectory = data_path + FileNm + "_Model_Output/"
if not os.path.exists(OutputDirectory):
    os.makedirs(OutputDirectory)
output_prefix = OutputDirectory + FileNm + "_"
current_runoff_filename = output_prefix + "current_runoff.csv"
future_runoff_filename = output_prefix + "future_runoff.csv"
sorted_filename = output_prefix + "sorted_ws.csv"
culvert_geometry_filename = output_prefix + "culv_geom.csv"
capacity_filename = output_prefix + "capacity_output.csv"
return_period_filename = output_prefix + 'return_periods.csv'
final_output_filename = output_prefix + 'model_output.csv'
skipped_filename = output_prefix + 'skipped_culverts.csv'

# Notifies user about runnign calculations
print "\nRunning calculations for culverts in " + FileNm

# 1. WATERSHED PEAK DISCHARGE

# Sort watersheds so they match original numbering (GIS changes numbering)
print " * Sorting watersheds by BarrierID and saving it to " + sorted_filename + "."
if PrecipType == 'n':
    ACA = data_path + 'All_Culverts_All.csv'    # Appended Watershed file
    Reg = raw_input("What NY Region? (provide number 1-6; 2=Hudson River Estuary watershed, See Lumia et al 2006, pg 7) \n")
    Precip_Append.calculate(watershed_data_input_filename, watershed_precip_input_filename, ACA,  Reg=2)
    watershed_data_input_filename = ACA

sorterPrecip.sort(watershed_data_input_filename, FileNm[:3], sorted_filename)

# Culvert Peak Discharge function calculates the peak discharge for each culvert for current and future precip
print " * Calculating current runoff and saving it to " + current_runoff_filename + "."
runoffP.calculate(sorted_filename,  1.0, current_runoff_filename, skipped_filename)
runoffP.calculate(sorted_filename,  1.15, future_runoff_filename)  # 1.15 times the current for future.
print " * Calculating future runoff and saving it to " + future_runoff_filename + "."


# 2. CULVERT GEOMETRY
print " * Calculating culvert geometry and saving it to " + culvert_geometry_filename + "."
# Culvert Capacity Prep function calculates the cross sectional area and assigns c and Y coeffs to each culvert
capacity_prep.geometry(field_data_input_filename, culvert_geometry_filename)

# 3. CULVERT CAPACITY
print " * Calculating culvert capacity and saving it to " + capacity_filename + "."
# Culvert_Capacities function calculates the capacity of each culvert (m^3/s) based on inlet control
capacity.inlet_control(culvert_geometry_filename, capacity_filename)

# 4. RETURN PERIODS AND FINAL OUTPUT
print " * Calculating return periods and saving them to " + return_period_filename + "."
print " * Calculating final output and saving it to " + final_output_filename + "."
final_output.final_output(capacity_filename, current_runoff_filename, future_runoff_filename, final_output_filename, field_data_input_filename, not_extracted_filename, output_prefix)

print "\nDone! All output files can be found within the folder " + OutputDirectory
