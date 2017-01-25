#!/usr/local/bin/python3.5

# Author: Will Parker <mr.william.a.parker@gmail.com>
"""
A script to process data from CrossFit Open Scores by Athlete (Id)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import logging
import bisect

division = ['Men', 'Women']

def main(idx):
    div = division[idx]

    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
    
    score_columns=['Id', 'Name', 'Division', 'OverallScore', 'Rank', 'Wk1_Score', 'Wk1_Rank', 
                            'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank']
    score_columns_15=['Id', 'Name', 'Division', 'OverallRank', 'Rank', 'Wk1A_Score', 'Wk1A_Rank', 'Wk1B_Score', 'Wk1B_Rank',
                            'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank']
    
    #loop through Games Years 2012, 2013, 2014, 2015, and 2016
    #store all the score data in dataList matrix
    #...
    #memory is cheap?
    i = 12
    Id_list = [[],[],[],[],[]] #a list for each year
    compList = []
    indices = []
    while i <= 16:
        score_filename = "Scores\\" + str(i) + "_Scores_" + div + ".csv"
        print("i = " + str(i))
        #all the ids of athletes who registered
        if i != 15:
            dataList = pd.read_csv(score_filename, names=score_columns, encoding='ISO-8859-1')
        else:
            dataList = pd.read_csv(score_filename, names=score_columns_15, encoding='ISO-8859-1')  
        
        Id_list[i-12] = dataList.Id.tolist()
        compId_list = dataList.Rank.dropna().tolist() #grab the list of finisher ranks (drop NaN values)
        for j in range(len(compId_list)-1): #loop through the final ranks (minus 'Rank' column name)
            compId_list[j] =  Id_list[i-12][j] #replace the rank with the Id of the finisher
        compList.append(compId_list) #create a list of lists for Ids who completed that year's Open
        
        Id_list[i-12].sort()
        if i == 12:
            indices = Id_list[i-12] #in year 1, take all the Ids
        else:
            for item in Id_list[i-12]:
                if item not in indices: #check for new entrants each year
                    bisect.insort(indices, item) #insert Id in place

        print("Number of athletes in " + div + "'s division in 20" + str(i) + ": " + str(len(Id_list[i-12])))
        print("Number of athletes who completed all the workouts: " + str(len(compList[i-12])))
        i = i + 1
        
    df = pd.DataFrame(columns=('2012 Reg', '2012 Finish', '2013 Reg', '2013 Finish', '2014 Reg', '2014 Finish', '2015 Reg', '2015 Finish', '2016 Reg', '2016 Finish',))
    print("Number of Athletes 2012-2016: " + str(len(indices)))
    logging.info("Length of 2012: " + str(len(Id_list[0])))

    #loop through each Id and determine the years of their participation/completion
    for athlete in indices:
        bRegister = [0,0,0,0,0]
        bComplete = [0,0,0,0,0]
        logging.info("Id in indices: " + str(athlete))
        year = 0
        while year <= 4:
            if athlete in Id_list[year]:
                bRegister[year] = 1
            else:
                bRegister[year] = 0
            if athlete in compList[year]:
                bComplete[year] = 1
            year = year + 1
        logging.info("Years Registered: " + str(bRegister))
        logging.info("Years Completed: " + str(bComplete))
        df.loc[athlete] = (bRegister[0],bComplete[0],bRegister[1],bComplete[1],bRegister[2],bComplete[2],bRegister[3],bComplete[3],bRegister[4],bComplete[4])

    #save to csv
    df.to_csv(path_or_buf=div+'_Participation_Matrix.csv')

    #display plot
    fig, ax = plt.subplots()
    index = np.arange(i-12)
    bar_width = 0.35
    opacity = 0.8
    
    rects1 = plt.bar(index, [len(Id_list[0]),len(Id_list[1]),len(Id_list[2]),len(Id_list[3]),len(Id_list[4])], bar_width, alpha=opacity, color='b', label='Registered')
    rests2 = plt.bar(index + bar_width, [len(compList[0]), len(compList[1]), len(compList[2]), len(compList[3]), len(compList[4])], bar_width, alpha=opacity, color='g', label='Completed')
    
    plt.xlabel('Year')
    plt.ylabel('Athletes')
    plt.title('Athletes per Year')
    plt.xticks(index + bar_width, ('2012', '2013', '2014', '2015', '2016'))
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
        
        
if __name__ == '__main__':
    for index in range(len(division)):
        main(index)