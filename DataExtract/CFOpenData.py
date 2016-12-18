from getProfile import *
from extractScores import *
from getAffiliates import *
import logging
import pandas

def main():
    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
            
    #controlling variables
    divisions = [1,2] #Men's and Women's Rx Divisions
    year = 16
    numberperpage = 30

    #Get Affiliates
    #getAffiliates.getAffiliates()
    
    #Get profiles from existing score list
    columns=['Id', 'Name', 'Division', 'OverallRank', 'Rank', 'Wk1_Score', 'Wk1_Rank', 
             'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank']
    data = pandas.read_csv(r'Scores\16_Scores_Men.csv', names=columns, encoding='ISO-8859-1')
    Id_list = data.Id.tolist()
    print("Number of Ids " + str(len(Id_list)))
    getProfile.getProfile(Id_list,1)

    #Get Athlete Scores and Profiles
    #for div in divisions:
    #   CFOpenData = extractScores.extractScores(div,year,numberperpage)
    #   getProfile.getProfile(CFOpenData.Id_list, div)
        
if __name__ == '__main__':
    main()