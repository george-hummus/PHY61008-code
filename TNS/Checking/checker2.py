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

#we want to check if the IDs largest database
#ideally though the databases will have the same size
#and then we just check if the IDs from the official one are in the local one
if IDs.size >= localIDs.size:
    ids1, db1 = IDs, database #larger is the official list
    ids2, db2 = localIDs, localdb #smaller is the local list
    database_name = "official"
    #finding where ID from official list is in the local list
else:
    ids1, db1 = localIDs, localdb #larger is the local list
    ids2, db2 = IDs, database #smaller is the official list
    database_name = "local"
    #finding where the ID from the local list is in the official list

#empty lists
nomatch = []
mult = []
match = []
rowdifs = []
checkedIDs = []
duplicates = []

for idx, iD in enumerate(tqdm(ids1)):
    #idx is the index that the id is located at in the list of ids, id is the value of the id
    #check if new id is already been called (i.e., duplicate in ID list we are looping thru)
    if iD in checkedIDs:
        duplicates.append(iD) #add id to list of duplicates if it is
    else:
        index = np.where(ids2==iD)[0] #looks for index that the id is at in the smaller id list
        if index.size == 0: #if no index produced then there is no match
            nomatch.append(iD)
        elif index.size == 1: #if one index then there has been a match
            if (np.prod(db1[idx] == db2[index[0]]) == 1):
                #checks if the row with the ID we were searching for is the same as the row where the ID is located in the other database
                #if all entries in this row comparison for this ID are true then the rows are the same
                #this means the product of this comparison will be 1 (or True)
                match.append(iD)
            else: #else the rows for this ID have different entries
                rowdifs.append(iD)
        else: #else multiple indices so multiple matches
            mult.append(iD)

        checkedIDs.append(iD) #add id to the list of ids that have been checked

print(f"Number of full matches: {len(match)}")
print(f"Number of ID matches with different row entries: {len(rowdifs)}")
print(f"    - These IDs were: {rowdifs}")
print(f"Number of IDs not matched: {len(nomatch)}")
print(f"    - These IDs were: {nomatch}")
print(f"Number of IDs with multiple matches: {len(mult)}")
print(f"    - These IDs were: {mult}")
print(f"Number of duplicate IDs in {database_name}: {len(duplicates)}")
print(f"    - These IDs were: {duplicates}")
