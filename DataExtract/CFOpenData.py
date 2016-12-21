from getProfile import *
from extractScores import *
from getAffiliates import *
import logging
import pandas

def getAffiliateList():
    getAffiliates.getAffiliates()
    
def getProfilesFromFile(score_filename, prof_filename, div):
    score_columns=['Id', 'Name', 'Division', 'OverallRank', 'Rank', 'Wk1_Score', 'Wk1_Rank', 
             'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank']
    #all the ids of athletes who registered
    dataList = pandas.read_csv(score_filename, names=score_columns, encoding='ISO-8859-1')
    Id_list = dataList.Id.tolist()
    name_list = dataList.Name.tolist()
    print("Total number of Ids " + str(len(Id_list)))
    
    #all of the ids of athlete profiles already downloaded
    prof_columns=('Name', 'Affiliate', 'Age', 'Height', 'Weight', 'Sprint 400m', 
                               'Clean & Jerk', 'Snatch', 'Deadlift', 'Back Squat', 'Max Pull-ups')
    profileList = pandas.read_csv(prof_filename, names=prof_columns, encoding='ISO-8859-1')
    remove_list = profileList.Name.tolist() #get the names from the profile list
    for item in remove_list: #if a name is in the profile list and in the scores list then it has already downloaded
        if item in name_list:
            del Id_list[name_list.index(item)] #so remove the id from the list of profiles to download
            logging.info(str(item) + " removed from the Id_list")
    
    print("Number of Ids to download " + str(len(Id_list)))
    
    #rudimentary loop to download profiles from saved list
    start = 0
    inc = 300
    while start+inc <= len(Id_list):
        getProfile.getProfile(Id_list[start:start+inc],div)
        start = start + inc + 1
    overflow = len(Id_list) % inc
    getProfile.getProfile(Id_list[start:start+overflow],div)

def main():
    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
            
    #controlling variables
    divisions = [2,1] #Women's and Men's Rx Divisions
    year = 16
    numberperpage = 30

    #******************#
    #Get Affiliates
    #getAffiliateList()
    
    #******************#
    #Get profiles from existing score list
    getProfilesFromFile(r'Scores\16_Scores_Men.csv', r'Profiles\Profile_Men.csv', divisions[1])
        
    #*******************#
    #Get Athlete Scores and Profiles from Interwebz
    #for div in divisions:
    #   CFOpenData = extractScores.extractScores(div,year,numberperpage)
    #   getProfile.getProfile(CFOpenData.Id_list, div)
        
if __name__ == '__main__':
    main()