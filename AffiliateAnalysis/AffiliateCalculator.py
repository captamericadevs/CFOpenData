#!/usr/local/bin/python3.5

# Author: Will Parker <mr.william.a.parker@gmail.com>
"""
A script to count the number of athletes from each affiliate who registered for the Crossfit Open for the given year
"""
import csv
import logging

division = ['Men', 'Women']
year = ['2017', '2018']

def countParticipants(filename):
    """
    function to open the csv file and iterate one row at a time (to save on memory consumption)
    """
    with open(filename, "r", encoding='utf-8', errors='ignore') as csvfile: #utf8 encoding to handle names
        datareader = csv.reader(csvfile)
        yield next(datareader)

        for row in datareader:
            yield row

def getParticipants(filename):
    for row in countParticipants(filename):
        yield row

def saveCounts(filename, athleteDict):
    """
    function to write out the results and store in a csv for further manipulation
    """
    with open(filename, 'w', encoding='utf-8', errors='ignore') as f: 
        w = csv.writer(f)
        for key,val in athleteDict.items():
            w.writerow([key, *val])

def main(idx):
    """
    main entry point into program
    """

    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
    
    div = division[idx]
    filename = "Data\\" + div + "_Rx_" + year[1] + ".csv" #filename cancatonator

    athleteCount = {} #dict to track affiliates key:value = affiliate_id:[athletes, top performer, percentile]
    affiliate_count = 0
    real_count = 14845 #total number of registered CrossFit affiliates (absolute limit)

    for row in getParticipants(filename):
        if not row[8] in athleteCount:
            athleteCount[row[8]] = [1,row[2],row[11]] #affiliate_id:[athletes, top performer, percentile]
            print(row[8])
            logging.info("START " + row[8] + " - Athlete: " + athleteCount[row[8]][1])
            affiliate_count += 1
            if affiliate_count >= real_count:
                print("Counted too many affiliates " + affiliate_count)
                break
        else:
            athleteCount[row[8]][0] += 1 #increment athletes
            if athleteCount[row[8]][2] < row[11]: #swap the top athlete spot if there if a higher one on list
                athleteCount[row[8]][2] = row[11]
                athleteCount[row[8]][1] = row[2]
                logging.info("UPDATED " + row[8] + " - Athlete: " + athleteCount[row[8]][1])
            logging.info("Added to " + row[8])

    if affiliate_count <= real_count:
        saveCounts(div+"_Counts.csv", athleteCount)	
    else:
        print("Affiliates Counted = " + len(athleteCount) + ", vice actual " + real_count)

if __name__ == '__main__':
    for index in range(len(division)):
        main(index)