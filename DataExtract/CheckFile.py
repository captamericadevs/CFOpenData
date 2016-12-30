import logging
import pandas
from collections import defaultdict

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>1)

def checkFile(filename):
    columns=['Id', 'Name', 'Affiliate', 'Age', 'Height', 'Weight', 'Sprint 400m', 
                               'Clean & Jerk', 'Snatch', 'Deadlift', 'Back Squat', 'Max Pull-ups']
    #all the ids of athletes who registered
    dataList = pandas.read_csv(filename, names=columns, encoding='ISO-8859-1')
    Id_list = dataList.Id.tolist()
    print("Total number of Ids " + str(len(Id_list)))
    dup_list = sorted(list_duplicates(Id_list))
    print("Total number of non-duplicates " + str(len(dup_list)))
    for dup in dup_list:
        print(str(dup_list.index(dup)) + " - " + str(dup))
        
def main():
    #Get profiles from existing score list
    checkFile(r'Profiles\Profile_Women.csv')
        
if __name__ == '__main__':
    main()