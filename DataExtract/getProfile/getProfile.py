import bs4
import requests
import pandas
import re, os

class getProfile():                                      
    def __init__(self, Id_list, div):
        file_path = 'Profiles'
        file_enum = ['Profile_Men.csv', 'Profile_Women.csv', 'Profile_Master_Men_45.csv', 'Profile_Master_Women_45.csv',
             'Profile_Master_Men_50.csv', 'Profile_Master Women_50.csv', 'Profile_Master_Men_55.csv', 'Profile_Master_Women_55.csv',
             'Profile_Master_Men_60.csv', 'Profile_Master_Women_60.csv', 'Profile_Team.csv', 'Profile_Master_Men_40.csv',
             'Profile_Master_Women_40.csv', 'Profile_Teen_Boy_14.csv', 'Profile_Teen_Girl_14.csv', 'Profile_Teen_Boy_16.csv',
             'Profile_Teen_Girl_16.csv']
    
        #Open the CSV and read in the data
        Athletes = pandas.DataFrame(columns=('Name', 'Affiliate', 'Age', 'Height', 'Weight', 'Sprint 400m', 
                                        'Clean & Jerk', 'Snatch', 'Deadlift', 'Back Squat', 'Max Pull-ups'))
        #loop through out athlete ID list accessing each profile
        for profile in Id_list:
            url = 'http://games.crossfit.com/athlete/' + str(profile)
            response = requests.get(url, 
                                    headers={
                                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                                    })
            response.raise_for_status()
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            
            #grab name, affiliate
            name = soup.find(id="page-title").string.extract()
            name = name[9:]
            affiliate_txt = soup.find("dt", text="Affiliate:").next_sibling.string
            
            #collect age, height, weight
            age = int(soup.find("dt", text="Age:").next_sibling.string)
            height_txt = soup.find("dt", text="Height:").next_sibling.string

            m = [int(s) for s in re.findall(r'\d+', height_txt)]
            if m:
                height = int((m[0] * 12) + m[1])
            elif "cm" in height_txt:
                height = int(int(height_txt)/2.54)

            weight_txt = soup.find("dt", text="Weight:").next_sibling.string
            if "lb" in weight_txt:
                weight = int(weight_txt[:-3])
            else:
                weight = int(int(weight_txt[:-3])*0.453592)

            #collect maxes
            sprint = soup.find("td", text="Sprint 400m").next_sibling.string
            clean_jerk = soup.find("td", text="Clean & Jerk").next_sibling.string
            snatch = soup.find("td", text="Snatch").next_sibling.string
            deadlift = soup.find("td", text="Deadlift").next_sibling.string
            back_squat = soup.find("td", text="Back Squat").next_sibling.string
            pullups = soup.find("td", text="Max Pull-ups").next_sibling.string
            
            Athletes.loc[profile] = (name, affiliate_txt, age, height, weight, sprint, clean_jerk, snatch, deadlift, back_squat, pullups)
        filename = os.path.join(file_path, file_enum[div-1])
        print(filename + " written out.")
        Athletes.to_csv(path_or_buf=filename)