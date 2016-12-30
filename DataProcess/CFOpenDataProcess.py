from mergeFiles import *
import pandas as pd
import logging

division = ['Men', 'Women']

def main(idx):
	div = division[idx]

    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
    
    prof_columns=['Id', 'Name', 'Affiliate', 'Age', 'Height', 'Weight', 'Sprint 400m', 
            'Clean & Jerk', 'Snatch', 'Deadlift', 'Back Squat', 'Max Pull-ups']
      
    profiles_df = pd.read_csv('Profile_'+div+'.csv', names=prof_columns, encoding='ISO-8859-1')
    affiliate_cnt = profiles_df['Affiliate'].value_counts()
	
	score_columns=['Id', 'Name', 'Division', 'OverallRank', 'Rank', 'Wk1_Score', 'Wk1_Rank', 
                            'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank']
    score_columns_15=['Id', 'Name', 'Division', 'OverallRank', 'Rank', 'Wk1A_Score', 'Wk1A_Rank', 'Wk1B_Score', 'Wk1B_Rank',
                            'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank']
	
	#loop through Games Years 2012, 2013, 2014, 2015, and 2016
	i = 12
	dataList = []
	while i <= 16:
	    score_filename = str(i) + "_Scores_" + div + ".csv"
		#all the ids of athletes who registered
		if i != 15:
			dataList.append(pandas.read_csv(score_filename, names=score_columns, encoding='ISO-8859-1'))
		else:
			dataList.append(pandas.read_csv(score_filename, names=score_columns_15, encoding='ISO-8859-1'))
        Id_list = dataList[i-12].Id.tolist()
        print("Number of athletes in " + div + "'s division in 20" + str(i) + ": " + str(len(Id_list)))
        
        
if __name__ == '__main__':
    main(0)