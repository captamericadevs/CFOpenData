#!/usr/local/bin/python3.5

# Author: Will Parker <mr.william.a.parker@gmail.com>
"""
A class to download and process data from CrossFit Athletes
Profiles at: http://games.crossfit.com/athlete/

Usage:
getProfile.getProfile(Id_list, division)
:param Id_list: A list of Ids describing the athlete profile
:type Id_list: list<integer>
:param division: describes the competitive divsion (i.e. Male Rx, Female Rx, etc)
:type division: integer 1-15
"""
import asyncio
from aiohttp import ClientSession

import bs4
import pandas

import requests
import re, os
import logging

headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"}
file_path = 'Profiles'
file_enum = ['Profile_Men.csv', 'Profile_Women.csv', 'Profile_Master_Men_45.csv', 'Profile_Master_Women_45.csv',
             'Profile_Master_Men_50.csv', 'Profile_Master Women_50.csv', 'Profile_Master_Men_55.csv', 'Profile_Master_Women_55.csv',
             'Profile_Master_Men_60.csv', 'Profile_Master_Women_60.csv', 'Profile_Team.csv', 'Profile_Master_Men_40.csv',
             'Profile_Master_Women_40.csv', 'Profile_Teen_Boy_14.csv', 'Profile_Teen_Girl_14.csv', 'Profile_Teen_Boy_16.csv',
             'Profile_Teen_Girl_16.csv']

class getProfile():   
    async def downloadPage(self, sem, url, session):
        """
        async function that checks semaphore unlocked before calling get function
    
        :param sem: asyncio.Semaphore
        :param url: url with appended profile Id
        :param session: TCP session info of type aiohttp.ClientSession() 
        :return getPage: function call
        """
        async with sem:
            return await self.getPage(url, session)
    
    async def getPage(self, url, session):
        """
        async function that makes HTTP GET requests
    
        :param url: url with appended profile Id
        :param session: TCP session info of type aiohttp.ClientSession()
        :return data: text() object
        """
        async with session.get(url, headers=headers) as response:
            data = await response.text()
            return data
            
    async def loopPages(self, Id_list):
        """
        async function that creates semaphore and prepares HTTP GET requests by a segmented number of pages
    
        :param Id_list: list of integers contain athlete Id numbers
        """
        async_list = []
        sem = asyncio.Semaphore(len(Id_list)) #create semaphore
        
        async with ClientSession() as session:
            for profile in Id_list:
                url = 'http://games.crossfit.com/athlete/' + str(profile)
                task = asyncio.ensure_future(self.downloadPage(sem, url, session))
                async_list.append(task)
            results = await asyncio.gather(*async_list) 
        #loop through pages on complete
        for page in results:
            self.getStats(page)            

    def getStats(self, response):
        """
        function that extracts features of athlete profile
    
        :params response: text() response object
        """
        soup = bs4.BeautifulSoup(response, "html.parser")
        
        #grab name, affiliate
        name = soup.find(id="page-title").string.extract()
        name = name[9:]
        affiliate_txt = soup.find("dt", text="Affiliate:")
        if affiliate_txt:
            affiliate_txt = affiliate_txt.next_sibling.string
         
        #collect age, height, weight
        age_txt = soup.find("dt", text="Age:")
        if age_txt:
            age = int(age_txt.next_sibling.string)
        else:
            age = 0
            
        height_txt = soup.find("dt", text="Height:")
        height = 0 #default value
        if height_txt:
            height_txt = height_txt.next_sibling.string
            m = [int(s) for s in re.findall(r'\d+', height_txt)]
            if "cm" in height_txt: #cm to inch
                height = int(int(m[0])*0.393701)

            elif m: #feet' inch" to inches
                height = int((m[0] * 12))
                if len(m) == 3:
                    height = height + (10 + m[2]) #if two digit inches, then inches are 10 + [1 or 0]
                else:
                    height = height + m[1]

        weight_txt = soup.find("dt", text="Weight:")
        if weight_txt:
            weight_txt = weight_txt.next_sibling.string
            weight = self.convertWeight(weight_txt)
        else:
            weight = 0

        #collect maxes
        try:
            sprint = soup.find("td", text="Sprint 400m").next_sibling.string
        except AttributeError:
            sprint = 0
        
        try:
            clean_jerk_txt = soup.find("td", text="Clean & Jerk").next_sibling.string
            clean_jerk = self.convertWeight(clean_jerk_txt)
        except AttributeError:
            clean_jerk = 0
            
        try:
            snatch_txt = soup.find("td", text="Snatch").next_sibling.string
            snatch = self.convertWeight(snatch_txt)
        except AttributeError:
            snatch = 0
            
        try:    
            deadlift_txt = soup.find("td", text="Deadlift").next_sibling.string
            deadlift = self.convertWeight(deadlift_txt)
        except AttributeError:
            deadlift = 0
            
        try:    
            back_squat_txt = soup.find("td", text="Back Squat").next_sibling.string
            back_squat = self.convertWeight(back_squat_txt)
        except AttributeError:
            back_squat = 0
        
        try:        
            pullup_txt = soup.find("td", text="Max Pull-ups").next_sibling.string
            if "--" in pullup_txt:
                pullups = 0
            else: 
                pullups = int(pullup_txt)
        except AttributeError:
            pullups = 0
        
        self.Athletes.loc[name] = (affiliate_txt, age, height, weight, sprint, clean_jerk, snatch, deadlift, back_squat, pullups)
    
    def convertWeight(self, kilos):
        """
        function that checks where a feature value is metric or null and converts to American Standard
    
        :params kilos: string object contain value of profile feature value
        """
        if "kg" in kilos:
            return int(int(kilos[:-3])*2.20462) #kg to lbs
        elif "--" in kilos:
            return 0
        else:
            return int(kilos[:-3]) #drop "lbs"
    
    def startProfileLoop(self, start, end):
        """
        function that creates an concurrent event loop
    
        :params start: starting index of page number
        """
        self.Athletes = pandas.DataFrame(columns=('Affiliate', 'Age', 'Height', 'Weight', 'Sprint 400m', 
                               'Clean & Jerk', 'Snatch', 'Deadlift', 'Back Squat', 'Max Pull-ups'))
        
        #loop through the first segment of pages
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.loopPages(self.Id_list[start:end]))
        loop.run_until_complete(future)

        filename = os.path.join(file_path, file_enum[int(self.division)-1]) #create file in Profile directory
        if not self.started:
            if start == 0:
                self.Athletes.to_csv(path_or_buf=filename) #blocking function
                print(filename + " written out.")
            else:
                self.Athletes.to_csv(path_or_buf=filename, mode='a', header=False) #blocking function
                print(filename + " appended with " + str(end) + " profiles")
        else:
            self.Athletes.to_csv(path_or_buf=filename, mode='a', header=False) #blocking function
            print(filename + " appended with " + str(end) + " profiles")
    
    def __init__(self, Id_list, div, started):
        """
        Initialize the class. Segments the total number of athlete Id by an integer number of pages (num_per) 
        to GET at a time to ensure sockets aren't maxed out (functions as a throttle)
        
        :param Id_list: list integers describing athlete profile Ids
        :param div: integer describing the competitive division
        """
        self.Id_list = Id_list
        self.division = div
        self.started = started
        
        #loop through the athlete ID list accessing each profile
        print(str(len(Id_list)) + " athletes in this division")
        num_per = 100 #number of pages to get at a time
        self.endoflist = len(Id_list) % num_per
 
        print("Downloading " + str(len(Id_list)) + " athlete profiles...")
        
        i = 0
        while i < int(len(Id_list)/num_per):
            start = int(i*num_per)
            self.startProfileLoop(start,(start+num_per))
            i = i + 1
        start = int(i*num_per)
        self.startProfileLoop(start,(start+self.endoflist))
            
        
   
  