#!/usr/local/bin/python3.5

# Author: Will Parker <mr.william.a.parker@gmail.com>
"""
A script to process data from CrossFit Open Scores by Athlete (Id)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

division = ['Men', 'Women']

def main(idx):
    logging.basicConfig(filename='async.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
    
    div = division[idx]
    filename = div + "_Participation_Matrix.csv"
    part_columns=['2012 Reg', '2012 Finish', '2013 Reg', '2013 Finish', '2014 Reg', '2014 Finish', '2015 Reg', '2015 Finish', '2016 Reg', '2016 Finish']
    dataMatrix = pd.read_csv(filename, names=part_columns, encoding='ISO-8859-1')
    
    dataList = [0,0,0,0,0,0,0,0,0,0] 

    for i in range(10):
        for item in dataMatrix[part_columns[i]]:
            try:
                dataList[i] = dataList[i] + int(item)
            except:
                print(item)

    #display plot
    fig, ax = plt.subplots()
    index = np.arange(5)
    bar_width = 0.35
    opacity = 0.8
    
    rects1 = plt.bar(index, [int(dataList[0]), int(dataList[2]), int(dataList[4]), int(dataList[6]), int(dataList[8])], bar_width, alpha=opacity, color='b', label='Registered')
    rests2 = plt.bar(index + bar_width, [int(dataList[1]), int(dataList[3]), int(dataList[5]), int(dataList[7]), int(dataList[9])], bar_width, alpha=opacity, color='g', label='Completed')
    
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