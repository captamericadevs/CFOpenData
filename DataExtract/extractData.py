__author__ = 'kbalkoski'

import requests
import urllib.request as request
from collections import OrderedDict

import numpy
import pandas
import json
import time

div_dict = {'1':"I-Men", '2':"I-Women", '3':"M-Men 45-49", '4':"M-Women 45-49", 
            '5':"M-Men 50-54", '6':"M-Women 50-54", '7':"M-Men 55-59", '8':"M-Women 55-59",
            '9':"M-Men 60+", '10':"M-Women 60+", '11':"Team", '12':"M-Men 40-44", '13':"M-Women 40-44",
            '14':"T-Boy 14-15", '15':"T-Girl 14-15", '16':"T-Boy 16-17", '17':"T-Girl 16-17"}

#adjustable variables
division = 1
numperpage = 30
params_cf = OrderedDict({
    "division": division,
    "sort": "1",
    "region": "0",
    "stage": "15",
    "year": "16",
    "page": "1",
    "numberperpage": numperpage,
    "scaled": "0",
    "occupation": "0"
})

basepath = 'http://openg.azurewebsites.net/api/leaderboard?'

#request page 1
response = requests.get(basepath,
                           params=params_cf,
                           headers={
                               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                           }).json()

num_pages = response['TotalPages'] #get number of pages

Scores = pandas.DataFrame(columns=('Name', 'Division', 'OverallRank', 'Rank', 'Wk1_Score', 'Wk1_Rank',
                               'Wk1A_score', 'Wk1A_Rank', 'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank',
                               'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank'))

WkScore = numpy.array(range(6))
WkRank = numpy.array(range(6))

Id_list = []

#loop thorugh the pages
for p in range(1,10):#num_pages):
    params_cf["page"] = str(p) #advance the page
    time.sleep(0.1)
    result = None
    looped = 0
    while result is None:
        looped = looped + 1
        try: #to get the next page
            response = requests.get(basepath,
                           params=params_cf,
                           headers={
                               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                           }).json()
            result = 1
        except requests.exceptions.RequestException as e: #if it didn't load try again
            print ('Trouble accessing server. Attempt %s' % str(looped))
            time.sleep(5)
            response = requests.get(basepath,
                           params=params_cf,
                           headers={
                               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                           }).json()
            result = None

    athletes = response['Athletes'] #get the athletes

    #loop through all the athletes on each page
    for i in range(numperpage):
        Id = athletes[i]['Id']
        Id_list.append(Id)
        Name = athletes[i]['Name']
        Div = div_dict[str(division)]
        ORank = athletes[i]['OverallRank']
        Rank = athletes[i]['Rank']

        for w in range(5): #loop through the workouts
            try:
                if athletes[i]['Weeks'][w]['Score'] == '--':
                    WkScore[w] = 0
                    WkRank[w] = 0
                WkScore[w] = athletes[i]['Weeks'][w]['Score']
                WkRank[w] = athletes[i]['Weeks'][w]['Rank']
            except TypeError:
                WkScore[w] = 0
                WkRank[w] = 0
            except ValueError:
                WkScore[w] = 0
                WkRank[w] = 0

        Scores.loc[Id] = (Name, Div, ORank, Rank, WkScore[0], WkRank[0], WkScore[1], WkRank[1], WkScore[2], WkRank[2],
                          WkScore[3], WkRank[3], WkScore[4], WkRank[4], WkScore[5], WkRank[5])

Scores.to_csv(path_or_buf='Scores_Men_Rx.csv')
print(Id_list)