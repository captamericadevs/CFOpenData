#!/usr/local/bin/python3.5

# Author: Will Parker <mr.william.a.parker@gmail.com>
"""
A class to download and process data from an open database of 
CrossFit Open scores available at: http://openg.azurewebsites.net/

Usage:
extractScores.extractScores(division,year,numberperpage)
:param division: Defines the competitive division (i.e. Male Rx, Female Rx, etc)
:type division: integer 1-15
:param year: Defines the year of the competition
:type year: integer 11-16
:param numberperpage: number of athletes to extract per page
:type numberperpage: integer
"""

__docformat__ = 'restructuredtext'

import asyncio
from aiohttp import ClientSession

import requests

import os, re
from getProfile import *

import numpy
import pandas
import json
import logging
import time

headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"}
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

class extractScoresMainSite():
    """
    Downloads the pages for a division, extracts features, then stores data in a CSV file
    """
    Id_list = []
    basepath = 'https://games.crossfit.com/competitions/api/v1/competitions/open/'
    async def downloadPage(self, sem, nParams, session):
        """
        async function that checks semaphore unlocked before calling get function
    
        :param sem: asyncio.Semaphore
        :param nParams: dictionary of RESTful params
        :param session: TCP session info of type aiohttp.ClientSession() 
        :returns getPage: call function
        """
        async with sem:
            return await self.getPage(nParams, session)
    
    async def getPage(self, params, session):
        """
        async function that makes HTTP GET requests
    
        :param params: set of RESTful type parameters to describe response
        :param session: TCP session info of type aiohttp.ClientSession()
        :returns data: JSON response object
        """
        logging.info("Params = " + str(params))
        async with session.get(self.basepath, params=params, headers=headers) as response:
            data = await response.json()
            return data

    
    def getScores(self, response):
        """
        function that extracts scores for each athletes
    
        :params response: JSON response object
        """
        WkScore = numpy.array(range(5))
        WkRank = numpy.array(range(5))
        athletes = []
        athletes = response['athletes'] #get the athletes
        logging.info('Number of athletes ' + str(len(athletes)))
        
        #loop through all the athletes on each page
        for i in range(len(athletes)):
            Id = athletes[i]['userid']
            self.Id_list.append(Id)
            Name = athletes[i]['name']
            Div = div_dict[str(self.division)]
            ORank = athletes[i]['overallrank']
            Rank = athletes[i]['overallscore']

            for w in range(5): #loop through the workouts
                try:
                    if athletes[i]['scores'][w]['scoredisplay'] == '--' or athletes[i]['scores'][w]['scoredisplay'] == None or athletes[i]['scores'][w]['workoutrank'] == None: #if no score
                        WkScore[w] = 0
                        WkRank[w] = 0
                    elif "rep" in athletes[i]['scores'][w]['scoredisplay']: #if not a time
                        reps = athletes[i]['scores'][w]['scoredisplay'][:-5]
                        if w == 0: #20-min cap
                            WkScore[w] = 1200 + int(reps) #to compare those who finished under the time cap to those who didn't
                        elif w == 2: #24-min cap
                            try:
                                n_reps = int(reps)
                            except:
                                n_reps = reps[:-4]
                            WkScore[w] = 1440 + (216 - int(reps)) #216 total possible reps, so order by max - completed + max_time. Those who complete have scores in minutes
                        else:
                            WkScore[w] = int(reps)
                        WkRank[w] = int(athletes[i]['scores'][w]['workoutrank'])
                    else:
                        times = athletes[i]['scores'][w]['scoredisplay'].split(":")
                        WkScore[w] = int(times[0])
                        if len(times) == 3:
                            WkScore[w] = (WkScore[w]*60*60)+int(times[1])+int(times[2])
                        elif len(times) == 2:
                            WkScore[w] = (WkScore[w]*60)+int(times[1])
                        WkRank[w] = athletes[i]['scores'][w]['workoutrank']
                except ValueError:
                    logging.info("Value: " + Name)
                    logging.info(athletes[i]['scores'][w]['scoredisplay'])
                    WkScore[w] = 0
                    WkRank[w] = 0
                except TypeError:
                    logging.info("Type: " + Name)
                    logging.info(athletes[i]['scores'][w]['workoutrank'])
                    WkScore[w] = 0
                    WkRank[w] = 0

            self.Scores.loc[Id] = (Name, Div, ORank, Rank, WkScore[0], WkRank[0], WkScore[1], WkRank[1], WkScore[2], WkRank[2],
                              WkScore[3], WkRank[3], WkScore[4], WkRank[4]) #store in DataFrame
    
    async def loopPages(self, start, numberofpages):
        """
        async function that creates semaphore and prepares HTTP GET requests by a segmented number of pages
    
        :param start: page number at the beginning of this segment
        :param numberofpages: number of pages in this segment
        """
        logging.info('loopPages from ' + str(start))
        async_list = []
        sem = asyncio.Semaphore(numberofpages) #create semaphore
        
        async with ClientSession() as session:
            for p in range(start, start+numberofpages):
                params={"division": self.division, "scaled": "0", "sort": "0", "fittest": "1", 
                        "fittest1": "0", "occupation": "0","page": str(p)}
                task = asyncio.ensure_future(self.downloadPage(sem, params, session))
                async_list.append(task)
            results = await asyncio.gather(*async_list) 
        #loop through pages on complete
        logging.info('Number of results = ' + str(len(results)))
        
        for page in results:
            self.getScores(page)
            logging.info('Length of scores = ' + str(len(results)))

    def startEventLoop(self, start, num_per_block):
        """
        function that creates an concurrent event loop
    
        :params start: starting index of page number
        """
        self.Scores = pandas.DataFrame(columns=('Name', 'Division', 'OverallRank', 'Rank', 'Wk1_Score', 'Wk1_Rank',
                            'Wk2_Score', 'Wk2_Rank', 'Wk3_Score', 'Wk3_Rank', 'Wk4_Score', 'Wk4_Rank', 'Wk5_Score', 'Wk5_Rank'))
        
        #loop through the first segment of pages
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.loopPages(start, num_per_block))
        loop.run_until_complete(future)

        filename = os.path.join(file_path, str(self.year) + "_" + file_enum[int(self.division)-1]) #create file in Scores directory
        if start == 0:
            self.Scores.to_csv(path_or_buf=filename) #blocking function
            print(filename + " written out.")
        else:
            self.Scores.to_csv(path_or_buf=filename, mode='a', header=False) #blocking function
            print(filename + " written to page " + str(start))
        
    def __init__(self, div, year, numperpage):          
        """
        Initialize the class. Gets the total number of pages in the class based on the requested
        number per page. Segments the total pages by an integer number of pages (nper) to ensure
        sockets aren't maxed out (functions as a throttle)
        
        :param div: integer describing the competitive division
        :param year: integer describing the competition year
        :param numperpage: integer describing the number of athletes to return per page
        """
        self.division = div #for each division
        self.numperpage = numperpage
        self.year = year
        self.basepath = self.basepath+str(year)+"//leaderboards?"
            
        #request page 1
        response = requests.get(self.basepath,
                               params={
                                   "division": div,
                                   "scaled": "0",
                                   "sort": "0",
                                   "fittest": "1",
                                   "fittest1": "0",
                                   "occupation": "0",
                                   "page": "1"
                               },
                               headers=headers).json()

        num_pages = response['totalpages'] #get number of pages
        print("Number of Pages = " + str(num_pages))

        nper = 50 #number of pages in each block
        endoflist = num_pages % nper #number in last block 
        
        #Run the concurrent event loops
        i = 0
        while i < int(num_pages/nper):
            logging.info("Passing range from: " + str(i*nper))
            self.startEventLoop(i*nper,nper) 
            i = i + 1
            self.Scores = []
        self.startEventLoop(i*nper, endoflist)
        
        
        
