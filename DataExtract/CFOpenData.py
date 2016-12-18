from getProfile import *
from extractScores import *
from getAffiliates import *
import logging

def main():
    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)

    div_dict = {'1':"I-Men", '2':"I-Women", '3':"M-Men 45-49", '4':"M-Women 45-49", 
            '5':"M-Men 50-54", '6':"M-Women 50-54", '7':"M-Men 55-59", '8':"M-Women 55-59",
            '9':"M-Men 60+", '10':"M-Women 60+", '11':"Team", '12':"M-Men 40-44", '13':"M-Women 40-44",
            '14':"T-Boy 14-15", '15':"T-Girl 14-15", '16':"T-Boy 16-17", '17':"T-Girl 16-17"}
            
    #controlling variables
    divisions = [1,2] #Men's and Women's Rx Divisions
    year = 16
    numberperpage = 30

    #Get Affiliates
    #getAffiliates.getAffiliates()
    #getProfile.getProfile([18670],1)

    #Get Athletes
    for div in divisions:
       CFOpenData = extractScores.extractScores(div,year,numberperpage)
       getProfile.getProfile(CFOpenData.Id_list, div)
        
if __name__ == '__main__':
    main()