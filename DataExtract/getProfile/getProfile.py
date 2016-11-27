import bs4
import grequests
import requests
import pandas
import re, os

file_path = 'Profiles'
file_enum = ['Profile_Men.csv', 'Profile_Women.csv', 'Profile_Master_Men_45.csv', 'Profile_Master_Women_45.csv',
             'Profile_Master_Men_50.csv', 'Profile_Master Women_50.csv', 'Profile_Master_Men_55.csv', 'Profile_Master_Women_55.csv',
             'Profile_Master_Men_60.csv', 'Profile_Master_Women_60.csv', 'Profile_Team.csv', 'Profile_Master_Men_40.csv',
             'Profile_Master_Women_40.csv', 'Profile_Teen_Boy_14.csv', 'Profile_Teen_Girl_14.csv', 'Profile_Teen_Boy_16.csv',
             'Profile_Teen_Girl_16.csv']

class getProfile():    
    def getStats(self, response, *args, **kwargs):
        soup = bs4.BeautifulSoup(response.text, "html.parser")
            
        #grab name, affiliate
        name = soup.find(id="page-title").string.extract()
        name = name[9:]
        affiliate_txt = soup.find("dt", text="Affiliate:")
        if affiliate_txt:
            affiliate_txt = affiliate_txt.next_sibling.string
         
        #collect age, height, weight
        age = int(soup.find("dt", text="Age:").next_sibling.string)
        height_txt = soup.find("dt", text="Height:").next_sibling.string

        m = [int(s) for s in re.findall(r'\d+', height_txt)]
        if "cm" in height_txt: #cm to inch
            height = int(int(height_txt[:2])*0.393701)
        elif m: #feet' inch" to inches
            height = int((m[0] * 12) + m[1])
        else:
            height = 0

        weight_txt = soup.find("dt", text="Weight:").next_sibling.string
        if "lb" in weight_txt:
            weight = int(weight_txt[:-3])
        elif "--" in weight_txt:
            weight = 0
        else:
            weight = int(int(weight_txt[:-3])*2.20462) #kg to lbs

        #collect maxes
        sprint = soup.find("td", text="Sprint 400m").next_sibling.string
        clean_jerk_txt = soup.find("td", text="Clean & Jerk").next_sibling.string
        clean_jerk = convertWeight(clean_jerk_txt)
        snatch_txt = soup.find("td", text="Snatch").next_sibling.string
        snatch = convertWeight(snatch_txt)
        deadlift_txt = soup.find("td", text="Deadlift").next_sibling.string
        deadlift = convertWeight(deadlift_txt)
        back_squat_txt = soup.find("td", text="Back Squat").next_sibling.string
        back_squat = convertWeight(back_squat_txt)
        pullups = int(soup.find("td", text="Max Pull-ups").next_sibling.string)
        
        self.Athletes.loc[name] = (affiliate_txt, age, height, weight, sprint, clean_jerk, snatch, deadlift, back_squat, pullups)
    
    def convertWeight(self, kilos):
        if "kg" in kilos:
            return int(int(kilos[:-3])*2.20462) #kg to lbs
        else:
            return int(kilos[:-3]) #drop "lbs"
            
        
    def __init__(self, Id_list, div):
        self.Athletes = pandas.DataFrame(columns=('Affiliate', 'Age', 'Height', 'Weight', 'Sprint 400m', 
                                        'Clean & Jerk', 'Snatch', 'Deadlift', 'Back Squat', 'Max Pull-ups')) 
        async_list = []
        
        #loop through the athlete ID list accessing each profile
        print(str(len(Id_list)) + " athletes in this division")
        session = requests.Session()
        for profile in Id_list:
            url = 'http://games.crossfit.com/athlete/' + str(profile)
            async_list.append(grequests.get(url, 
                                    headers={
                                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                                    }, hooks={'response':self.getStats}, session=session))
        print("Downloading " + str(len(Id_list)) + " athlete profiles...")
        grequests.map(async_list)
  
        filename = os.path.join(file_path, file_enum[int(div)-1])
        self.Athletes.to_csv(path_or_buf=filename)
        print(filename + " written out.")
        
   
  