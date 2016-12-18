from mergeFiles import *
import pandas as pd
import logging

def main():
    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
    
    columns=['Affiliate', 'Age', 'Height', 'Weight', 'Sprint 400m', 
            'Clean & Jerk', 'Snatch', 'Deadlift', 'Back Squat', 'Max Pull-ups']
        
            
    profiles_df = pd.read_csv('Profile_Men.csv', names=columns, encoding='ISO-8859-1')
    print(profiles_df['Affiliate'].value_counts())
    
    #scores_df = pd.read_csv('16_Scores_Men.csv', keep_default_na=False, na_values[""])
    #affiliates_df = pd.read_csv('affiliateList.csv', keep_default_na=False, na_values[""])
    

    #Get Athletes
    #for div in divisions:
    #   CFOpenData = extractScores.extractScores(div,year,numberperpage)
    #   getProfile.getProfile(CFOpenData.Id_list, div)
        
if __name__ == '__main__':
    main()