# Organized CSV file validator and loader (for Cornell Culverts Model, or anything else.)
# Noah Warnke
# 2016-08-30
#
# Brief comments added by Tanvi Naidu, 6/13/2017
#
# This script will 
# a) open a given .csv file, validating the file exists,
# b) locate each of the required headers, validating that they exist, 
# c) cast each value to the given header types, validating that this is possible, and
# d) return a list of dictionaries that map the header names to the parsed values.
#
# Note, the "signature" (the second parameter) is essential, 
# since it defines what data is expected.
# 
# For example, given a CSV file with filename test.csv:
# a, b, c
# 1, 2, 3
# 4, 5, 6
#
# loader.load(
#   'test.csv', 
#   [
#      {'name': 'a', 'type': 'int'}, 
#      {'name': 'b', 'type': 'int'},
#      {'name': 'c', 'type': 'int'}
#   ],
#   1,
#   -1
# ) will return:
#
# [
#   {'a': '1', 'b': '2', 'c': '3'},
#   {'a': '4', 'b': '5', 'c': '6'}
# ]
# 
# Importantly, if anything is wrong with the file, a helpful error will be given.

import csv
import sys
import operator
import numpy

# Load and validate a file.
# Parameters:
#   filename: the path and filename of the csv file to open.
#   required_headers: the signature of the headers and their data types in the above format.
#   start_row: which row to look for the headers on. Normally 1.
#   max_rows: How many rows of data to read. Put -1 to read until end of file.
# Returns:
#   A dictionary containing two entries: valid_rows and invalid_rows.
# 
#   valid_rows is a list of dictionaries, where each dictionary is the data from a row,
#   its keys are the header names, and the values are the table values parsed to the proper type.
#
#   invalid_rows is a dictionary containing row_number, 
#   row (the actual row list), and reason_invalid string.
def load(filename, required_headers, start_row, max_rows) :
    try:
        with open(filename, 'r') as csv_file:
            input_table = csv.reader(csv_file)

            # Get down to the start row.
            for i in range (1, start_row):
                next(input_table)
            
            # Read the header row.
            header_row = next(input_table)
            
            # For each header in the signature, find it in the table's header row.
            # If it's missing, keep a list of them so we can give an error later.
            header_index = {} #empty dictionary for header names
            missing_headers = [] #empty list for missing headers
            for header in required_headers:
                try:
                    index = header_row.index(header['name']) 
                    header_index[header['name']] = index
                except ValueError:
                    missing_headers.append(header['name'])

            # If any headers were missing, give an error and exit.
            if len(missing_headers) > 0:
                print "ERROR: file '" \
                    + filename \
                    + "' was missing the following required headers on row " \
                    + str(start_row) \
                    + ": " \
                    + ", ".join(missing_headers) \
                    + ". Bailing out."
                sys.exit(0)

            # Now we can attempt to grab all the values from each row and put them in dictionaries.
            result_list = []
            invalid_rows = []
            row_number = start_row + 1 #initializing row number as the first row below headers
            for row in input_table:
                # Stop if there is a maximum number of rows to load and we've reached it.
                if max_rows != -1 and row_number - start_row > max_rows:
                    break

                result_item = {}
                for header in required_headers:
                    index = header_index[header['name']]
                    
                    if index >= len(row):
                        # Row not long enough to reach at least one header.
                        invalid_rows.append({
                            "row_number": row_number,
                            "row": row,
                            "reason_invalid": "it did not have enough columns to reach header " \
                                + header['name'] \
                                + " in column " \
                                + column_string(index + 1) \
                                + "." \
                        })
                        break
                    value = row[index]
                    try:
                        # Attempt to parse the value to the correct type.
                        result_item[header['name']] = header['type'](value)
                    except ValueError:
                        invalid_rows.append({
                        "row_number": row_number,
                        "row": row,
                        "reason_invalid": "in row " \
                            + str(row_number) \
                            + ", column " \
                            + column_string(index + 1) \
                            + " (" \
                            + header['name'] \
                            + ") of file '" \
                            + filename \
                            + "', the value '" \
                            + value \
                            + "' could not be parsed to " \
                            + str(header['type']) \
                            + "." \
                        })
                        break

                #Successful, so add to result list.
                result_list.append(result_item)
                row_number += 1 #row number is increased by 1
               
            # Return our list of dictionaries.
            return {
                "valid_rows": result_list,
                "invalid_rows": invalid_rows
            };
        csv_file.close()
    except IOError:
        print "ERROR: Could not find file '" \
            + filename \
            + "'. Bailing out."
        sys.exit(0)    

# Define a helper function to get a spreadsheet column name from an index.
# Copied straight from http://stackoverflow.com/questions/23861680/convert-spreadsheet-number-to-column-letter
def column_string(n):
    div=n
    string=""
    temp=0
    while div>0:
        module=(div-1)%26
        string=chr(65+module)+string
        div=int((div-module)/26)
    return string
    
