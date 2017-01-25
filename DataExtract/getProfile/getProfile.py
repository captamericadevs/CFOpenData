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
        prof_list = []
        
        async with ClientSession() as session:
            for profile in Id_list:
                url = 'https://games.crossfit.com/athlete/' + str(profile)
                prof_list.append(str(profile))
                task = asyncio.ensure_future(self.downloadPage(sem, url, session))
                async_list.append(task)
            results = await asyncio.gather(*async_list) 
        #loop through pages on complete
        for page in results:
            self.getStats(page, prof_list[results.index(page)])            

    def getStats(self, response, id):
        """
        function that extracts features of athlete profile
    
        :params response: text() response object
        """
        soup = bs4.BeautifulSoup(response, "html.parser")
        
        #grab name, affiliate
        name_txt = soup.title.string
        if name_txt == "CrossFit Games | The Fittest on Earth":
            fail = soup.find("meta", property="og:url")
            logging.info("!!!Page Not Found: " + str(fail["content"]))
            return
        name = name_txt[9:]
        name = name[:-16]
        
        info_txt = soup.find_all("li", class_="item sm-inline")
        try:
            region = info_txt[0].find("div", class_="text").string.strip()
            affiliate = info_txt[2].find("a")
            if affiliate:
                affiliate = affiliate.string
            else:
                affiliate = info_txt[2].find("div", class_="text").string.strip()
            
        except AttributeError:
            logging.info("No region of affiliate for athlete: " + name)
            logging.info(info_txt)
        
        measurement_info = soup.find_all("li", class_="item sm-stacked")
        try:
            #collect age, height, weight
            age_txt = measurement_info[0].find("div", class_="text lg").string.strip()
            if age_txt == '--':
                age = 0
            else:
                age = int(age_txt)
        except:
            age = 0
            logging.info("No age for athlete: " + name)
            logging.info(measurement_info)
            
        try:
            height_txt = measurement_info[1].find("div", class_="text lg nowrap").string.strip()
            if height_txt == '--':
               height = 0
            else:
                m = [int(s) for s in re.findall(r'\d+', height_txt)]
                if "cm" in height_txt: #cm to inch
                    height = int(int(m[0])*0.393701)
                elif m: #feet' inch" to inches
                    height = int((m[0] * 12))
                    if len(m) == 3:
                        height = height + (10 + m[2]) #if two digit inches, then inches are 10 + [1 or 0]
                    else:
                        height = height + m[1]
        except:
            height = 0
            logging.info("No height for athlete: " + name)
            logging.info(measurement_info)
                
        try:
            weight_txt = measurement_info[2].find("div", class_="text lg nowrap").string.strip()
            if weight_txt == '--':
                weight = 0
            else:
                weight = self.convertWeight(weight_txt)
        except:
            weight = 0
            logging.info("No weight for athlete: " + name)
            logging.info(measurement_info)

        #collect maxes
        stats_info = soup.find_all("div", class_="stats-section")
        try: #games website breaks up stats_section into blocks of 3 movements
            squat_txt = stats_info[0].find_all("td")
            squat = self.convertWeight(squat_txt[0].string.strip())
            if squat == '--':
                squat = 0
            clean_jerk = self.convertWeight(squat_txt[1].string.strip())
            if clean_jerk == '--':
                clean_jerk = 0
            snatch = self.convertWeight(squat_txt[2].string.strip())
            if snatch == '--':
                snatch = 0
        except:
            squat = 0
            clean_jerk = 0
            snatch = 0
            logging.info("No stats for athlete: " + name)
            logging.info(stats_info)
                
        try:
            deadlift_txt = stats_info[1].find_all("td")
            deadlift = self.convertWeight(deadlift_txt[0].string.strip())
            if deadlift == '--':
                deadlift = 0
            fgb = deadlift_txt[1].string.strip()
            if fgb == '--':
                fgb = 0
            pullups = deadlift_txt[2].string.strip()
            if pullups == '--':
                pullups = 0
        except:
            deadlift = 0
            fgb = 0
            pullups = 0
            logging.info("No stats for athlete: " + name)
            logging.info(stats_info)
            
        try:
            fran_txt = stats_info[2].find_all("td")
            fran = fran_txt[0].string.strip()
            if fran == '--':
                fran = 0
            grace = fran_txt[1].string.strip()
            if grace == '--':
                grace = 0
            helen = fran_txt[2].string.strip()
            if helen == '--':
                helen = 0
        except:
            fran = 0
            grace = 0
            helen = 0
            logging.info("No stats for athlete: " + name)
            logging.info(stats_info)
                
        try:
            fill_txt = stats_info[3].find_all("td")
            fill50 = fill_txt[0].string.strip()
            if fill50 == '--':
                fill50 = 0
            sprint = fill_txt[1].string.strip()
            if sprint == '--':
                sprint = 0
            fivek = fill_txt[2].string.strip()
            if fivek == '--':
                fivek = 0
        except:
            fill50 = 0
            sprint = 0
            fivek = 0
            logging.info("No stats for athlete: " + name)
            logging.info(stats_info)
        
        self.Athletes.loc[id] = (name, affiliate, region, age, height, weight, squat, clean_jerk, snatch, deadlift, fgb, pullups, fran, grace, helen,  fill50, sprint, fivek)
    
    def convertWeight(self, kilos):
        """
        function that checks where a feature value is metric or null and converts to American Standard
    
        :params kilos: string object contain value of profile feature value
        """
        if "kg" in kilos:
            return int(int(kilos[:-3])*2.20462) #kg to lbs
        else:
            return int(kilos[:-3]) #drop "lbs"

    
    def startProfileLoop(self, start, end):
        """
        function that creates an concurrent event loop
    
        :params start: starting index of page number
        """
        self.Athletes = pandas.DataFrame(columns=('Name', 'Affiliate', 'Region', 'Age', 'Height', 'Weight', 'Back Squat', 'Clean & Jerk', 'Snatch', 'Deadlift',
                                 'Fight Gone Bad', 'Max Pull-ups', 'Fran', 'Grace', 'Helen', 'Filthy 50', 'Sprint 400m', 'Run 5K'))
        
        #loop through the first segment of pages
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.loopPages(self.Id_list[start:end]))
        loop.run_until_complete(future)

        filename = os.path.join(file_path, file_enum[int(self.division)]) #create file in Profile directory
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
            
        
   
  