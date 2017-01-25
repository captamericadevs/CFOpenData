#!/usr/local/bin/python3.5

# Author: Will Parker <mr.william.a.parker@gmail.com>
"""
A file to fix the 2012 participation column in the participant matrix 
file Div_Participation_Matrix.csv. 

Issue: all total open athletes (298K Men)
are listed as having competed in 2012, which should be 25K Men.
"""
import csv
import pandas as pd

def main():
    division = ['Men', 'Women']
    
    score_columns=['Id', 'Name', 'Division', 'OverallScore', 'Rank', 'Wk1_Score', 'Wk1_Rank', 
                            'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank']
    part_columns=['2012 Reg', '2012 Finish', '2013 Reg', '2013 Finish', '2014 Reg', '2014 Finish', 
                            '2015 Reg', '2015 Finish', '2016 Reg', '2016 Finish']
    
    for div in division:
        part_filename = div + "_Participation_Matrix.csv"
        score_filename = "Scores\\12_Scores_" + div + ".csv"

        dataList = pd.read_csv(score_filename, names=score_columns, encoding='ISO-8859-1')
        Id_list = dataList.Id.dropna().astype(int).tolist() #grab the list of finisher ranks
        print("Length of Id_list = " + str(len(Id_list)))
        
        infile = open(part_filename, 'r')
        outfile = open("out"+part_filename, 'w')
        
        writer = csv.writer(outfile, delimiter=',', lineterminator='\n')
        writer.writerow(part_columns)
        
        #read in Participant Matrix line-by-line and check if they competed in 2012
        reader = csv.reader(infile, delimiter=',')
        next(reader, None)
        for line in reader:
            try:
                line[0] = int(line[0])
            except ValueError:
                print("line[0] = " + str(line[0]))
                line[0] = 0
            if line[0] in Id_list:
                line[1] = 1
            writer.writerow(line)
        infile.close()
        outfile.close()
        
        
if __name__ == '__main__':
     main()