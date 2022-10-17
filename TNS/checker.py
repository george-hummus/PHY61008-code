import csv
import numpy as np
from tqdm import tqdm
import argparse

### SYSTEM ARGUMENTS ###
parser = argparse.ArgumentParser(description = """
Counts the matches in ID between two TNS CSV databases.
""")

#adding arguments to praser object
parser.add_argument('csv_offical' , type = str, help = 'Path to the offical TNS CSV database.')
parser.add_argument('csv_local' , type = str, help = 'Path to the locally created TNS CSV database.')
args = parser.parse_args()

### Functions ###
def CSVloader(fname,skiprows=0):
    """
    Loads in a CSV file conatining numbers and strings as a NumPy Object array.
    Arguments:
        - fname: path to the CSV file (string).
        - skiprows: number of rows you want to skip from the top (integer).
    Output:
        - csv_array: the CSV file saved as a NumPy object array.
    """
    #load in the csv file
    file=open(fname) #load in database
    csvreader = csv.reader(file) #openfile as csv

    #skips x number of rows from top of CSV
    for i in range(skiprows):
        next(csvreader)

    # list to save the rows to
    csv_list = []

    for row in csvreader:
            csv_list.append(row) #save all rows into a list

    #convert list into numpy array
    csv_array = np.array(csv_list,dtype="object")

    file.close() #closes file to free up RAM

    return csv_array


#load in offical and local CSV files
database = CSVloader(args.csv_offical, skiprows=2)
localdb = CSVloader(args.csv_local, skiprows=2)

#extarct only the IDs
IDs = database.T[0]
localIDs = localdb.T[0]

#empty lists
nomatch = []
mult = []
match = []

for ID in tqdm(IDs):
    index = np.where(localIDs==ID)[0] #looks for index that matches the ID in the local CSV
    if index.size == 0: #if no index produced then there is no match
        nomatch.append(ID)
    if index.size == 1: #if multiple one index then there has been a match
        match.append(ID)
    else: #else multiple indices so multiple matches
        mult.append(ID)

print(f"Number of matches: {len(match)}")
print(f"Number of IDs not matched: {len(nomatch)}")
print(f"    - These no match IDs where: {nomatch}")
print(f"Number of IDs with multiple matches: {len(mult)}")
print(f"    - These multiple match IDs where: {mult}")
