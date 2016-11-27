import grequests 
import requests
import os, re
from getProfile import *

import numpy
import pandas
import json

basepath = 'http://openg.azurewebsites.net/api/leaderboard?'
file_path = 'Scores'
file_enum = ['Scores_Men.csv', 'Scores_Women.csv', 'Scores_Master_Men_45.csv', 'Scores_Master_Women_45.csv',
             'Scores_Master_Men_50.csv', 'Scores_Master Women_50.csv', 'Scores_Master_Men_55.csv', 'Scores_Master_Women_55.csv',
             'Scores_Master_Men_60.csv', 'Scores_Master_Women_60.csv', 'Scores_Team.csv', 'Scores_Master_Men_40.csv',
             'Scores_Master_Women_40.csv', 'Scores_Teen_Boy_14.csv', 'Scores_Teen_Girl_14.csv', 'Scores_Teen_Boy_16.csv',
             'Scores_Teen_Girl_16.csv']

div_dict = {'1':"I-Men", '2':"I-Women", '3':"M-Men 45-49", '4':"M-Women 45-49", 
            '5':"M-Men 50-54", '6':"M-Women 50-54", '7':"M-Men 55-59", '8':"M-Women 55-59",
            '9':"M-Men 60+", '10':"M-Women 60+", '11':"Team", '12':"M-Men 40-44", '13':"M-Women 40-44",
            '14':"T-Boy 14-15", '15':"T-Girl 14-15", '16':"T-Boy 16-17", '17':"T-Girl 16-17"}

#adjustable variables
year = 16
numperpage = 30

Scores = pandas.DataFrame(columns=('Name', 'Division', 'OverallRank', 'Rank', 'Wk1_Score', 'Wk1_Rank', 
                                       'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank'))
Id_list = []
    
def getScores(response, *args, **kwargs):
    WkScore = numpy.array(range(5))
    WkRank = numpy.array(range(5))
    athletes = response.json()['Athletes'] #get the athletes

    #loop through all the athletes on each page
    for i in range(numperpage):
        Id = athletes[i]['Id']
        Id_list.append(Id)
        Name = athletes[i]['Name']
        print(Name)
        Div = div_dict[str(division)]
        ORank = athletes[i]['OverallRank']
        Rank = athletes[i]['Rank']

        for w in range(5): #loop through the workouts
            try:
                if athletes[i]['Weeks'][w]['Score'] == '--': #if no score
                    WkScore[w] = 0
                    WkRank[w] = 0
                elif len(athletes[i]['Weeks'][w]['Score']) == 5: #if a time
                    WkScore[w] = int(athletes[i]['Weeks'][w]['Score'][:1])*60+int(athletes[i]['Weeks'][w]['Score'][3:])
                    WkRank[w] = athletes[i]['Weeks'][w]['Rank']
                else: #else it is a number
                    WkScore[w] = int(athletes[i]['Weeks'][w]['Score'])
                    WkRank[w] = int(athletes[i]['Weeks'][w]['Rank'])
            except ValueError:
                print("Value: " + Name)
                print(athletes[i]['Weeks'][w]['Score'])
                WkScore[w] = 0
                WkRank[w] = 0

        Scores.loc[Id] = (Name, Div, ORank, Rank, WkScore[0], WkRank[0], WkScore[1], WkRank[1], WkScore[2], WkRank[2],
                          WkScore[3], WkRank[3], WkScore[4], WkRank[4])
            
for div, title in div_dict.items():
    division = div #for each division
    print("Div: " + str(div))
    print("Title: " + str(title))
        
    #request page 1
    response = requests.get(basepath,
                           params={
                               "division": div,
                               "sort": "1",
                               "region": "0",
                               "stage": "15",
                               "year": year,
                               "page": "1",
                               "numberperpage": numperpage,
                               "scaled": "0",
                               "occupation": "0"
                           },
                           headers={
                               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                           }).json()

    num_pages = response['TotalPages'] #get number of pages
    print("Number of Pages = " + str(num_pages))
    async_list = []
    #loop through the pages
    for p in range(1,num_pages):
        #advance the page
        next_page = grequests.get(basepath, params={
                                   "division": div,
                                   "sort": "1",
                                   "region": "0",
                                   "stage": "15",
                                   "year": year,
                                   "page": str(p),
                                   "numberperpage": numperpage,
                                   "scaled": "0",
                                   "occupation": "0"
                                },
                                headers={
                                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                                }, hooks={'response' : getScores})
        print("Downloading Page: " + str(p))
        async_list.append(next_page)

    downloaded_pages = grequests.map(async_list)

    #filename = os.path.join(file_path, file_enum[int(div)-1])
    Scores.to_csv(path_or_buf=file_enum[int(div)-1])
    print(file_enum[int(div)-1] + " written out.")
    getProfile.getProfile(Id_list, div)
    