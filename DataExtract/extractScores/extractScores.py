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

basepath = 'http://openg.azurewebsites.net/api/leaderboard?'
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

class extractScores():
    """
    Downloads the pages for a division, extracts features, then stores data in a CSV file
    """
    Id_list = []
    
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
        async with session.get(basepath, params=params, headers=headers) as response:
            data = await response.json()
            return data

    
    def getScores(self, response):
        """
        function that extracts scores for each athletes
    
        :params response: JSON response object
        """
        WkScore = numpy.array(range(5))
        WkRank = numpy.array(range(5))
        athletes = response['Athletes'] #get the athletes
        logging.info('Number of athletes ' + str(len(athletes)))
        
        #loop through all the athletes on each page
        for i in range(len(athletes)):
            Id = athletes[i]['Id']
            self.Id_list.append(Id)
            Name = athletes[i]['Name']
            Div = div_dict[str(self.division)]
            ORank = athletes[i]['OverallRank']
            Rank = athletes[i]['Rank']

            for w in range(5): #loop through the workouts
                try:
                    if athletes[i]['Weeks'][w]['Score'] == '--' or athletes[i]['Weeks'][w]['Score'] == None or athletes[i]['Weeks'][w]['Rank'] == None: #if no score
                        WkScore[w] = 0
                        WkRank[w] = 0
                    elif len(athletes[i]['Weeks'][w]['Score']) >= 5: #if a time
                        times = athletes[i]['Weeks'][w]['Score'].split(":")
                        WkScore[w] = int(times[0])
                        if len(times) == 3:
                            WkScore[w] = (WkScore[w]*60*60)+int(times[1])+int(times[2])
                        elif len(times) == 2:
                            WkScore[w] = (WkScore[w]*60)+int(times[1])
                        WkRank[w] = athletes[i]['Weeks'][w]['Rank']
                    else: #else it is a number
                        WkScore[w] = int(athletes[i]['Weeks'][w]['Score'])
                        WkRank[w] = int(athletes[i]['Weeks'][w]['Rank'])
                except ValueError:
                    print("Value: " + Name)
                    print(athletes[i]['Weeks'][w]['Score'])
                    WkScore[w] = 0
                    WkRank[w] = 0
                except TypeError:
                    print("Type: " + Name)
                    print(athletes[i]['Weeks'][w]['Rank'])
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
        
        tstart = time.time() #start timer
        async with ClientSession() as session:
            for p in range(start, start+numberofpages):
                params={"division": self.division, "sort": "1", "region": "0",
                        "stage": "15", "year": self.year, "page": str(p),
                        "numberperpage": self.numperpage, "scaled": "0", "occupation": "0"}
                task = asyncio.ensure_future(self.downloadPage(sem, params, session))
                async_list.append(task)
            results = await asyncio.gather(*async_list) 
        #loop through pages on complete
        logging.info('Number of results = ' + str(len(results)))
        tdownload = time.time() #timer for downloads
        
        for page in results:
            self.getScores(page)
            logging.info('Length of scores = ' + str(len(results)))
           
        logging.info('Time to Download = ' + str(tdownload - tstart))
        logging.info('Average time per page = ' + str((tdownload - tstart)/numberofpages))
        tend = time.time() #timer for number of pages
        logging.info('Time to Process = ' + str(tend - tstart))

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
                               headers=headers).json()

        num_pages = response['TotalPages'] #get number of pages
        print("Number of Pages = " + str(num_pages))

        nper = 1000 #number of pages in each block
        endoflist = num_pages % nper #number in last block 
        
        #Run the concurrent event loops
        i = 0
        while i < int(num_pages/nper):
            self.startEventLoop(i*nper,nper) 
            i = i + 1
        self.startEventLoop(i*nper, endoflist)
        
        
        
