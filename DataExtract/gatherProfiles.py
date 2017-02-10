#!/usr/local/bin/python3.5

# Author: Will Parker <mr.william.a.parker@gmail.com>
"""
A script that calls getProfile class to download total profiles
"""
from getProfile import *
import logging
import pandas
    
def main():
    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
    division = ['Women']
    
    part_columns=['Id', '2012 Reg', '2012 Finish', '2013 Reg', '2013 Finish', '2014 Reg', '2014 Finish', 
                            '2015 Reg', '2015 Finish', '2016 Reg', '2016 Finish']
    prof_columns=['Id', 'Name', 'Affiliate', 'Region', 'Age', 'Height', 'Weight', 'Back Squat', 'Clean & Jerk', 'Snatch', 'Deadlift',
                                 'Fight Gone Bad', 'Max Pull-ups', 'Fran', 'Grace', 'Helen', 'Filthy 50', 'Sprint 400m', 'Run 5K']  
                            
    i = 0
    while i < len(division):
        part_filename=division[i]+'_Participation_Matrix.csv'
        prof_filename = 'Profiles\\Profile_'+division[i]+'.csv'
    
        #all the ids of athletes who registered
        dataList = pandas.read_csv(part_filename, names=part_columns, encoding='ISO-8859-1')
        Id_list = dataList.Id.tolist()
        print("Total number of Ids " + str(len(Id_list)))
    
        #all of the ids of athlete profiles already downloaded
        profileList = pandas.read_csv(prof_filename, names=prof_columns, encoding='ISO-8859-1')
        remove_list = profileList.Id.tolist() #get the names from the profile list
        for item in remove_list: #if a name is in the profile list and in the scores list then it has already downloaded
            if item in Id_list:
                del Id_list[Id_list.index(item)] #so remove the id from the list of profiles to download
    
        print("Number of Ids to download " + str(len(Id_list)))
        getProfile.getProfile(Id_list,i,True)
        i = i + 1
        
if __name__ == '__main__':
    main()